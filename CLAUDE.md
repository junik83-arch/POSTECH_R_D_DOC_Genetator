# CLAUDE.md

이 저장소에는 두 개의 독립된 프로젝트가 있습니다:

1. **`index.html` / 루트 `README.md`** — POSTECH R&D전략팀 사업 안내 공문 생성기 (Gemini 연동 웹앱). 아래 내용과 무관합니다.
2. **`sources/`, `wiki/`, `scripts/`** — POSTECH 교원 R&D 위키 ("LLM Wiki"). 이 문서는 **이 위키의 스키마**입니다.

이 파일이 있는 한, Claude Code로 이 저장소에서 위키 관련 작업을 할 때는 아래 규칙을 따르세요.

## 배경: LLM Wiki 패턴

이 위키는 [Andrej Karpathy의 "LLM Wiki" 패턴](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)을
따릅니다 — 매번 원본 문서를 처음부터 다시 검색하는 대신, LLM이 **영속적인 위키를
점진적으로 구축·유지**합니다. 새 자료가 들어오면 단순히 색인화하는 데 그치지 않고,
핵심 정보를 추출해 기존 위키에 통합합니다.

## 3계층 구조

```
sources/                       ← 1) 원본 자료 — 절대 수정하지 않음
  faculty_profiles_source.json    POSTECH R&D 실적 데이터베이스 (교원 298명)
  homepage_crawl.json             교원 홈페이지 크롤링 결과 (로컬에서 생성, 선택)

wiki/                           ← 2) 위키 — 두 종류의 페이지가 섞여 있음
  faculty/<개인번호>-<성명>.md    [기계 생성] 교원 1인당 1페이지 — 결정론적 추출
  index.md                        [기계 생성] 전체 평면 카탈로그
  faculty-index.md                [기계 생성] 가나다순 전체 목록
  research-areas.md               [기계 생성] 연구분야 키워드 인덱스
  home.md                         [LLM 큐레이션] 최상위 진입점, 학과 간 공통 흐름 종합
  domain/<학과>.moc.md            [LLM 큐레이션] 학과별 연구 클러스터 종합 (mermaid 포함)
  log.md                          [LLM 큐레이션] 시간순 append-only 변경 기록
  open-questions.md               [LLM 큐레이션] 데이터 모순·미해결 이슈

scripts/                        ← 3) 파이프라인
  build_wiki.py                    sources/*.json → wiki/faculty/*.md, index.md 등 (결정론적)
  crawl_homepages.py               (로컬 전용) 홈페이지+서브페이지 크롤링 → sources/homepage_crawl.json
```

이 문서(`CLAUDE.md`)가 3번째 레이어인 **스키마**입니다.

## 페이지 두 종류 — 소유권이 다름

**[기계 생성] `wiki/faculty/*.md`, `index.md`, `faculty-index.md`, `research-areas.md`**
`scripts/build_wiki.py` 가 소유합니다. **직접 손으로 고치지 마세요.** 원본(`sources/`)이
바뀌면 스크립트를 다시 실행하세요 (`python3 scripts/build_wiki.py`) — 몇 번을 실행해도
같은 결과가 나와야 합니다(idempotent). 정확도가 중요한 추출 데이터라 LLM이 임의로 요약·재구성하지
않고, 원본 필드를 그대로 옮기거나 결정론적으로만 재배열합니다 (No Hallucination — POSTECH
R&D전략팀의 공문 작성 원칙과 동일).

**[LLM 큐레이션] `home.md`, `domain/*.moc.md`, `log.md`, `open-questions.md`**
LLM(Claude)이 직접 쓰고 유지합니다. **스크립트가 건드리지 않으므로**, ingest/query/lint
작업 중 LLM이 직접 파일을 읽고 고칩니다. 여기서는 종합·요약·클러스터링이 기대되는 행위입니다
— 단, 무엇을 근거로 그렇게 판단했는지(예: `관심분야` 필드 클러스터링) 명시하고, 확신이 낮은
분류는 `open-questions.md`에 남기세요.

## 원칙

1. **원본 무결성**: `wiki/faculty/*.md` 는 `sources/` 의 원본 JSON 필드를 그대로 옮기거나
   결정론적으로 재구성한 것이어야 합니다. `domain/*.moc.md` 같은 큐레이션 페이지는 종합·해석이
   들어가지만, 원본에 없는 사실을 지어내지는 않습니다.
2. **재실행 가능**: 기계 생성 페이지는 `build_wiki.py` 를 몇 번 돌려도 동일해야 합니다.
3. **점진적 병합**: 새 원본(예: 재크롤링 결과)이 들어오면 `build_wiki.py` 를 다시 실행해
   기계 생성 페이지에 반영하고, 그 영향이 큐레이션 페이지(예: 학과 MOC의 통계)에도 미치면
   해당 MOC를 갱신하세요.
4. **고유 식별자**: 파일명은 `개인번호-성명.md`. 동명이인 4쌍이 있어 이름만으로는 구분 불가
   (`open-questions.md` 참고).
5. **상호참조**: 교원 페이지 ↔ 학과 MOC는 상호 링크됩니다. 큐레이션 페이지는 텍스트 링크(탐색
   골격)와 mermaid 다이어그램(조감도)을 함께 유지합니다 — 페이지를 추가/제거할 때 둘 다 갱신하세요.

## 운영 (Operations)

**Ingest (새 원본 반영)**: 새 원본 자료(예: 재크롤링 결과, 갱신된 실적 데이터)가 들어오면
1) `sources/` 에 넣고 2) `python3 scripts/build_wiki.py` 로 기계 생성 페이지를 갱신한 뒤
3) 영향받는 `domain/*.moc.md` 를 다시 읽고 클러스터·통계가 여전히 맞는지 확인해 필요하면
고치고 4) `log.md` 에 항목을 추가합니다.

**Query (질의)**: `home.md` → 관련 `domain/*.moc.md` → 개별 `faculty/*.md` 순으로 훑는
것이 색인을 임베딩 검색 없이도 효율적으로 타는 방법입니다. 좋은 답변(비교, 분석, 발견한
연결고리)은 새 페이지로 위키에 다시 저장할 가치가 있으면 그렇게 하세요.

**Lint (점검)**: 주기적으로 다음을 확인하세요 — 학과 MOC의 통계가 최신 `sources/` 와
어긋나지 않는지, 인바운드 링크 없는 고아 페이지, 언급되지만 자체 클러스터가 없는 개념,
`open-questions.md` 에 남은 항목이 해소됐는지. 발견한 것은 `open-questions.md` 에 적고
해소되면 지운 뒤 `log.md` 에 기록합니다.

## 홈페이지 크롤링 관련 참고사항

이 저장소를 다루는 Claude Code 원격 환경은 네트워크 정책상 `postech.ac.kr` 등 외부 도메인에
접근할 수 없습니다 (egress 차단 — WebFetch 도구도 동일하게 막힘). 따라서 크롤링은
`scripts/crawl_homepages.py` 를 **인터넷 접근이 가능한 로컬 환경**에서 실행해
`sources/homepage_crawl.json` 을 만든 뒤, `scripts/build_wiki.py` 로 위키에 반영하는
2단계로 진행합니다.

- **서브페이지(탭) 크롤링**: 홈페이지 첫 화면 안의 같은 사이트 내부 링크 중 연구/논문/CV
  등 키워드로 우선순위를 매겨 교원 1명당 기본 8개까지 함께 가져옵니다. 구성원 명단·뉴스/공지
  링크는 제외합니다 (`SUBPAGE_EXCLUDE_KEYWORDS`).
- **학과/그룹 공통 포털 제외**: 여러 교원이 정확히 같은 URL을 홈페이지로 등록한 경우
  (`PORTAL_SHARE_THRESHOLD = 2` 이상 공유) 개인 페이지가 아니라고 보고 크롤링하지 않습니다.

자세한 크롤러 옵션은 `scripts/crawl_homepages.py` 의 docstring을 참고하세요.
