# 로그

시간순 append-only 기록. 새 항목은 맨 아래에 추가합니다. 형식: `## [날짜] 유형 | 설명`
(`grep "^## \[" wiki/log.md | tail -5` 로 최근 항목만 뽑아볼 수 있습니다.)

## [2026-08-27] ingest | 원본 데이터 반영
POSTECH R&D 실적 데이터베이스(교원 298명, `faculty_profiles.json`)를 `sources/faculty_profiles_source.json`으로 반영. `scripts/build_wiki.py` 로 `wiki/faculty/*.md` 298개, 학과 인덱스, 색인 페이지를 최초 생성.

## [2026-08-27] ingest | 홈페이지 크롤링 1차 (262/280)
사용자가 로컬 환경에서 `scripts/crawl_homepages.py` 실행 (이 세션은 네트워크 egress 정책상 postech.ac.kr 등 외부 도메인에 직접 접근 불가). 대상 URL 280개 중 262개 성공.

## [2026-08-27] ingest | 서브페이지 크롤링 확장 (홈페이지 내 탭까지)
크롤러에 서브페이지(연구/논문/CV 등 탭) 탐색 기능 추가, 교원 1명당 최대 8개까지 함께 크롤링하도록 확장. 재크롤링 후 1,213개 서브페이지 반영.

## [2026-08-27] lint | 구성원/뉴스 서브페이지·학과 공통 포털 제외
서브페이지 중 구성원 명단·뉴스/공지 게시판(교수 개인 연구와 무관)을 제외 키워드로 필터링. 여러 교원이 정확히 같은 URL을 홈페이지로 등록한 경우(학과/그룹 공통 포털, 7개 URL·24명 공유)를 감지해 크롤링 대상에서 제외.

## [2026-08-27] merge | PR #1 머지
`wiki/`, `data/`(이후 `sources/`로 개명), `scripts/` 를 `main` 브랜치에 머지. 이 시점까지는 학과 페이지가 `wiki/departments/*.md` 로 스크립트가 기계적으로 생성.

## [2026-08-27] lint | 아키텍처 재구성 — sources/wiki/schema 3계층 + LLM 큐레이션 MOC
사용자가 Karpathy의 LLM Wiki 패턴 원문과 CLAUDE.md 스타일 가이드를 제공하며, (1) `data/` → `sources/` 로 개명해 "불변 원본" 레이어를 명확히 하고 (2) 학과 페이지를 스크립트의 기계적 나열이 아니라 LLM이 직접 원문을 읽고 종합하는 `wiki/domain/*.moc.md` 로 전환할 것을 요청. 16개 학과 전체를 읽고 연구 클러스터를 식별해 MOC 작성, `wiki/home.md`(전체 진입점, 학과 간 공통 흐름 종합), `wiki/log.md`, `wiki/open-questions.md`, 루트 `CLAUDE.md`(스키마) 신설. 교원 개별 페이지(`wiki/faculty/*.md`)는 정확도가 중요한 추출 데이터이므로 기존처럼 결정론적 생성 유지.

## [2026-08-27] lint | 교원 개별 페이지 가독성 개선
`wiki/faculty/*.md`가 최대 39KB까지 늘어나 스캔하기 어렵다는 피드백. ￭/`; ` 로 나열된 필드를 불릿 리스트로 렌더링하고, 홈페이지 크롤링 원문·서브페이지(최대 8개)를 `<details>` 접이식 블록으로 감싸 기본은 접어두도록 `build_wiki.py` 수정.

## [2026-08-27] ingest | 홈페이지 크롤링 정기 자동화 (GitHub Actions, 매월 1일)
사용자가 "수시로 업데이트해서 DB에 쌓을 방법"을 문의. `.github/workflows/refresh-wiki.yml` 추가 — 매월 1일 GitHub Actions 러너(이 세션과 달리 실제 인터넷 접근 가능)에서 `crawl_homepages.py --force` + `build_wiki.py` 를 실행해 main에 직접 커밋. 사용자 로컬 PC 없이도 홈페이지 정보가 계속 최신화됨. `main` 브랜치에 머지되어야 스케줄이 실제로 켜짐.

## [2026-08-27] lint | 실적 데이터베이스는 연 1회 수동 업로드로 확정
사용자가 `faculty_profiles_source.json`(실적 DB)은 매년 새 파일을 받아 수동 교체해야 한다고 확인. 자동화 대상이 아님을 CLAUDE.md에 명시.

## [2026-08-27] ingest | 홈페이지 원문 AI 요약 추가 (Gemini API)
사용자가 "크롤링한 원문을 그대로 접어두지 말고, 교원 개인에 대해 읽고 이해한 것처럼 정리해달라"고 요청. Claude API 대신 이 저장소의 index.html(RFP 공문 생성기)이 이미 쓰고 있는 Gemini API(REST, 동적 모델 탐색 + 폴백 목록)를 재사용하기로 결정 — 별도 결제 체계 없이 기존 패턴 재활용.

`scripts/summarize_homepages.py` 신설: 크롤링 원문(첫 화면 + 서브페이지)을 교원 1인당 3~5문장으로 요약해 `homepage_crawl.json`의 `summary` 필드에 저장. 원문에 다른 교원 이름이 섞여 있을 때(학과 뉴스 게시판이 서브페이지로 잡힌 경우 등) 잘못 귀속되지 않도록 프롬프트에 "요약 대상 1인만" 가드레일 포함 — 완전하지는 않아 `open-questions.md`에 한계 기록. 원문 해시가 안 바뀌면 재요약을 건너뛰어 비용 절감.

`.github/workflows/refresh-wiki.yml`에 요약 단계 추가 (`GEMINI_API_KEY` 시크릿이 설정된 경우에만 실행, 없으면 조용히 건너뜀). `build_wiki.py`가 "AI 생성 요약"이라는 라벨과 함께 요약을 교원 페이지 상단에 표시 (원문은 접이식 블록으로 계속 보존).

## [2026-08-27] ingest | 국가전략기술 인덱스 신설
원본 `text_public`의 `국가전략기술` 필드(정부 12대 국가전략기술 분류를 참조하는 자유 서술형 텍스트)를 발견 — 298명 중 195명이 태그를 갖고 있었으나 지금까지 위키에 반영되지 않았음. 번호매김·괄호 세부사항이 뒤섞인 원문을 표준 12개 명칭으로 정규화하는 파서(`parse_national_tech()`)를 `build_wiki.py`에 추가해 `wiki/national-strategic-tech.md` 생성 — RFP·공모사업 기술 분야와 매칭되는 교원을 바로 찾을 수 있도록 함 (루트 `index.html` RFP 공문 생성기와의 연계 지점이 될 수 있음).
