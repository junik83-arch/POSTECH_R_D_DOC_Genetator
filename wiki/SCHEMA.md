# Wiki 스키마 (Karpathy "LLM Wiki" 패턴)

이 위키는 https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f 에서 설명하는
**"LLM이 유지보수하는 누적형 지식베이스"** 패턴을 따릅니다. 매번 원본 문서를 처음부터 다시
검색하는 대신, 구조화된 마크다운 페이지를 쌓아두고 새 자료가 들어올 때마다 기존 페이지를
갱신·병합합니다.

## 3계층 구조

```
data/                         ← 1) 원본 자료 (Source) — 절대 수정하지 않음
  faculty_profiles_source.json   POSTECH R&D 실적 데이터베이스 원본 (교원 298명)
  homepage_crawl.json (선택)     개별 교원 홈페이지 크롤링 결과 (로컬에서 생성)

wiki/                          ← 2) 위키 (누적된 지식) — 아래 스키마를 따라 생성/갱신
  index.md                        전체 진입점: 통계, 학과 목록, 사용법
  research-areas.md               연구분야 키워드 빈도 인덱스 (브라우징용)
  departments/<학과>.md           학과별 교원 목록 + 학과 통계
  faculty/<개인번호>-<성명>.md    교원 1인당 1페이지
  researchers.json                위 내용을 브라우저용으로 압축한 JSON (dashboard/ 가 fetch로 읽음)

dashboard/                     ← 2) 위키를 소비하는 뷰어 (사람이 손으로 고치는 애플리케이션)
  index.html                      연구자 대시보드: 통계·필터·검색 + POSTECH AI API 자연어 추천

scripts/                       ← 3) 파이프라인 (위키를 재생성하는 도구)
  build_wiki.py                   data/*.json → wiki/**/*.md + wiki/researchers.json (결정론적, 재실행 가능)
  crawl_homepages.py              (로컬 전용) 교원 홈페이지를 크롤링해 homepage_crawl.json 생성
```

이 문서(SCHEMA.md) 자체가 3번째 계층인 **스키마** 입니다 — 위키를 만들거나 갱신하는 주체
(스크립트 또는 LLM)가 지켜야 할 규칙을 정의합니다.

## 원칙

1. **원본 무결성(No Hallucination)**: `wiki/faculty/*.md` 의 내용은 `data/` 안의 원본
   JSON 필드를 그대로 옮기거나 결정론적으로 재구성한 것이어야 합니다. 원본에 없는 내용을
   창작해서 채우지 않습니다 (POSTECH R&D전략팀의 공문 작성 원칙과 동일).
2. **재실행 가능(Idempotent)**: `python3 scripts/build_wiki.py` 를 몇 번을 실행해도 항상
   같은 결과가 나와야 합니다. 위키 페이지는 손으로 직접 고치는 파일이 아니라 **생성되는
   파일**입니다. 내용을 고치고 싶으면 원본(`data/`)을 갱신하거나 스키마/스크립트를 고치세요.
3. **점진적 병합(Incremental merge)**: 새 원본 자료(예: `data/homepage_crawl.json`)가
   추가되면, 빌드 스크립트가 해당 교원 페이지의 "홈페이지 추가 정보" 섹션에 자동으로
   병합합니다. 아직 크롤링되지 않은 교원은 플레이스홀더를 유지합니다.
4. **교차참조(Cross-reference)**: 교원 페이지 ↔ 학과 페이지는 상호 링크됩니다
   (`[[departments/전자전기공학과]]` 형태의 마크다운 상대경로 링크). Obsidian 등
   마크다운 위키 뷰어에서 그대로 그래프로 탐색할 수 있습니다.
5. **고유 식별자**: 파일명은 `개인번호-성명.md` 형식을 씁니다. 동명이인이 4쌍 있기 때문에
   이름만으로는 페이지를 구분할 수 없습니다 (개인번호가 실제 primary key).

## 교원 페이지(`wiki/faculty/*.md`) 섹션 구성

1. Frontmatter (YAML): `id, name, department, email, homepage, updated`
2. `## 기본 정보` — 이메일/학과/홈페이지 링크
3. `## 연구관심분야` — 원본 `관심분야` 필드
4. `## 실적 요약` — 원본 `실적건수` 딕셔너리를 표로 렌더링
5. 이후 섹션들은 원본 `text_public` 필드를 줄 단위로 파싱해 그대로 생성
   (`연구키워드`, `주요성과`, `대표연구·최근 주도논문`, `학회발표`, `저서` 등 —
   교원마다 존재하는 섹션이 다르므로 원본에 있는 섹션만 생성됩니다)
6. `## 홈페이지 추가 정보` — `data/homepage_crawl.json` 이 있고 해당 URL이 크롤링됐다면
   그 내용을, 없다면 안내 문구를 넣습니다. 홈페이지 첫 화면 아래에는 `### 홈페이지 내
   세부 페이지` 소제목으로 연구/논문/구성원/CV 등 내부 탭 페이지 내용이 이어집니다
   (아래 "서브페이지 크롤링" 참고).
7. `## 출처` — 개인번호, 최종 갱신일

## 홈페이지 크롤링 관련 참고사항

이 저장소를 실행하는 Claude Code 원격 환경은 네트워크 정책상 `postech.ac.kr` 등 외부
도메인에 접근할 수 없습니다 (egress 차단). 따라서 크롤링은 `scripts/crawl_homepages.py`
를 **인터넷 접근이 가능한 로컬 환경**에서 실행해 `data/homepage_crawl.json` 을 만든 뒤,
그 파일을 커밋하고 `scripts/build_wiki.py` 를 다시 돌려 위키에 반영하는 2단계로 진행합니다.

### 서브페이지(탭) 크롤링

교원 홈페이지 첫 화면만으로는 연구실적 등 정확도 높은 정보를 놓치는 경우가 많아,
`crawl_homepages.py` 는 첫 화면 안의 링크 중 **같은 사이트 내부로 연결되는** 링크를 찾아
(연구/논문/CV 등 키워드로 우선순위를 매겨) 교원 1명당 기본 8개까지 함께 가져옵니다.
"같은 사이트"의 범위는 사이트 종류에 따라 다르게 판단합니다:

- `sites.google.com` 처럼 여러 교원이 도메인을 공유하는 경우 → 경로 앞부분
  (`/view/아이디`, `/site/아이디`)까지 같아야 같은 사이트로 봅니다.
- 그 외(예: `gt.postech.ac.kr` 같은 전용 서브도메인) → 같은 netloc이면 같은 사이트로 봅니다.

**제외 규칙**: 구성원/멤버 명단, 뉴스·공지 게시판 링크는 후보에서 아예 제외합니다
(`SUBPAGE_EXCLUDE_KEYWORDS`) — 교수 개인의 연구 정보와 관련이 적기 때문입니다.

`data/homepage_crawl.json` 의 각 홈페이지 엔트리는 `subpages` 필드에
`{서브페이지 URL: {title, text, status, fetched_at, error?}}` 형태로 결과를 담습니다.
`--max-subpages 0` 으로 끄거나 `--max-subpages N` 으로 개수를 조절할 수 있습니다.

### 학과/그룹 공통 포털 제외

여러 교원이 정확히 같은 URL을 "홈페이지"로 등록한 경우(예: 8명이 모두
`http://hss.postech.ac.kr/` 를 씀), 이는 개인 페이지가 아니라 학과/그룹 공통
포털일 가능성이 높다고 보고 **아예 크롤링하지 않습니다** (`PORTAL_SHARE_THRESHOLD = 2`
이상 공유되면 제외). 해당 엔트리는 `data/homepage_crawl.json` 에
`{"skipped": "shared_portal", "shared_by": N, "fetched_at": ...}` 로 기록되고,
위키 페이지의 "홈페이지 추가 정보" 섹션에는 그 사유가 표시됩니다.
