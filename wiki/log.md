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

## [2026-08-27] ingest | 도구 허브 신설 + 교원 검색 웹앱 신설
사용자가 "루트가 공문 생성기인 게 애매하다, 기능들이 병렬적으로 독립적인데 첫 페이지가 그거인 게 이상하다"며 여러 도구를 한눈에 볼 수 있는 메인 페이지를 요청. 앞으로 도구가 계속 늘어날 걸 감안한 구조 변경.

- 기존 `index.html`(공문 생성기)을 `tools/doc-generator.html`로 이동
- 새 루트 `index.html` = 도구 허브(랜딩 페이지) — 카드형 메뉴로 공문 생성기/교원 검색 연결, 향후 도구 추가될 자리도 마련
- 호환성: 팀원들이 쓰던 기존 공유 링크(`?key=...`)가 루트로 들어오면 허브가 자동으로 파라미터를 유지한 채 `tools/doc-generator.html`로 리다이렉트 — 예전 링크도 계속 동작
- **`tools/faculty-search.html` 신설** — 이름/학과/연구분야/국가전략기술로 교원 298명을 검색·필터링하는 실제 웹앱(바닐라 JS, 별도 서버 불필요). `tools/faculty-search-data.json`(build_wiki.py가 함께 생성하는 경량 데이터, 원본 4MB+ JSON 대신 ~190KB만 fetch)을 읽어 동작. 각 결과는 GitHub 위키 페이지로 연결
- jsdom으로 검색/필터/하이라이트 로직을 실제 데이터(298명)에 대해 테스트 — 학과 필터, 국가전략기술 필터, 자유 텍스트 검색 모두 확인. 검색어가 관심분야 원문(주로 영어)과 매칭 안 되는 경우(예: "양자"가 "Quantum"과 매칭 안 됨)를 발견해, 국가전략기술 태그(정확한 한글 표준 명칭)도 검색 대상에 포함시켜 보완
- README.md, CLAUDE.md 를 새 구조(허브 + tools/)에 맞게 갱신

## [2026-08-27] ingest | 국가전략기술 인덱스 신설
원본 `text_public`의 `국가전략기술` 필드(정부 12대 국가전략기술 분류를 참조하는 자유 서술형 텍스트)를 발견 — 298명 중 195명이 태그를 갖고 있었으나 지금까지 위키에 반영되지 않았음. 번호매김·괄호 세부사항이 뒤섞인 원문을 표준 12개 명칭으로 정규화하는 파서(`parse_national_tech()`)를 `build_wiki.py`에 추가해 `wiki/national-strategic-tech.md` 생성 — RFP·공모사업 기술 분야와 매칭되는 교원을 바로 찾을 수 있도록 함 (루트 `index.html` RFP 공문 생성기와의 연계 지점이 될 수 있음).

## [2026-08-28] ingest | 교원 검색기에 Gemini 자연어 검색 추가
사용자가 "교원 자연어 검색도 Gemini API로 되면 편할 것 같다"고 요청. 기존 키워드 매칭 검색은 그대로 두고, "AI에게 자연어로 물어보기" 패널을 추가 — 복합 조건 질문(예: "양자컴퓨팅 연구하면서 특허가 많은 교수")을 Gemini가 처리해 일치하는 교원 id 목록을 돌려주는 방식.

- `tools/doc-generator.html`과 동일한 패턴 재사용: REST 직접 호출(동적 모델 탐색 + flash 계열 우선 + 폴백 후보 목록), API 키는 브라우저 LocalStorage에 사용자 자신의 키로 저장
- **같은 LocalStorage 키(`postech_gemini_api_key`)를 씀** — 같은 오리진(GitHub Pages 사이트)이라 공문 생성기에서 키를 등록하면 검색기에서도 바로 쓸 수 있음
- 프롬프트에 교원 298명의 경량 데이터(id/성명/학과/관심분야/국가전략기술/실적)를 JSON으로 통째로 전달 — "목록에 없는 사실은 지어내지 말 것" 가드레일 포함, `responseMimeType: application/json`으로 응답 형식 강제
- jsdom으로 전체 흐름(키 없음→모달, 키 저장, AI 검색→3~4명 결과, 일반 검색 복귀, 일반 검색창 타이핑 시 AI 모드 자동 해제) 목 데이터로 검증, Playwright로 실제 렌더링도 스크린샷 확인

## [2026-08-28] revert | 검색 도구를 dashboard/(POSTECH AI API)로 되돌림
사용자가 실사용해보니 `tools/faculty-search.html`(Gemini, 단일 호출 방식)보다 이전에 있었던
`dashboard/index.html`(POSTECH AI API, 통계·학과 분포·상세 프로필 모달을 갖춘 인터페이스 +
문장 단위 추천 이유)이 인터페이스·추천 이유 형식 모두 더 낫다고 판단 — **위키 콘텐츠는 건드리지
않고 검색 도구만** 되돌림.

- `dashboard/index.html`, `dashboard/cors-proxy/`(Cloudflare Worker·val.town CORS 프록시)를
  머지 직전 커밋(27ea0ee)에서 복원, `tools/faculty-search.html`·`tools/faculty-search-data.json`
  삭제
- `build_wiki.py`: 검색 데이터 생성 함수를 `build_search_data()`(tools/ 출력) →
  `build_researchers_json()`(`wiki/researchers.json` 출력)으로 교체. `NATIONAL_TECH_CATEGORIES`/
  `parse_national_tech()`/`render_national_tech()` 등 위키 생성 로직은 전부 그대로 둠 —
  `national-strategic-tech.md`, `domain/*.moc.md`, `home.md` 등 위키 콘텐츠는 무관
- 루트 `index.html`(도구 허브) 카드 링크를 `dashboard/index.html`로 변경
- 위 "AI 자연어 검색(교원 검색기)의 한계" open-question은 그 대상 도구(`tools/faculty-search.html`)가
  삭제되어 더 이상 유효하지 않아 open-questions.md 에서 제거

## [2026-08-28] lint | 자동 갱신 워크플로 실패 원인 확인 + 주기를 매월 → 연 2회로 변경
`.github/workflows/refresh-wiki.yml`의 모든 실행(run 1~9)이 `conclusion: failure`였던 원인을
GitHub Actions API로 조사. `get_job_logs`/`list_workflow_jobs` 결과 모든 실패 run이 **job이
0개, 로그 없음, billable 시간 0**으로 — 워크플로 YAML 자체는 유효(`state: active`)하고
`scripts/crawl_homepages.py`·`build_wiki.py` 등 실제 스텝은 시작조차 하지 못한 채 러너 배정
전에 즉시 실패한 것으로 확인됨. 이는 저장소 코드의 버그가 아니라 **계정/조직 수준의 GitHub
Actions 설정**(예: Settings → Billing → Actions 지출 한도가 $0로 막혀 있거나, 해당 저장소에
대한 Actions 사용 자체가 아직 승인/활성화되지 않은 경우)이 원인일 가능성이 매우 높음 —
저장소 Settings → Actions 및 조직/개인 Billing 설정에서 Actions 지출 한도·사용 승인 여부를
확인 필요 (이 세션은 계정 결제 설정에 접근 권한이 없어 직접 해소는 불가).

별도로, 사용자 요청에 따라 크롤링·요약·위키 재생성 주기를 매월 1일 → **연 2회(3월 1일·9월
1일)** 로 변경 (`cron: "0 3 1 * *"` → `"0 3 1 3,9 *"`). CLAUDE.md·wiki/README.md·
open-questions.md의 "매월" 표현도 함께 갱신. (기존 참고사항대로, 스케줄 트리거가 실제로
켜지려면 이 워크플로 파일이 `main` 브랜치에 머지돼 있어야 함 — 현재 `main`에는 이 파일이
없어 병합 전까지는 스케줄이 동작하지 않음.)

## [2026-08-28] fix | 자동 갱신 워크플로의 진짜 원인 2건 확정 + 수정
위 항목에서 "계정/조직 설정 문제로 추정"이라 남겨뒀던 것을 사용자와 함께 실제로 좁혀서 확정함.

1. **GitHub Actions 지출 한도(Budget)** — 사용자 계정의 Actions budget이 `$0` + `Stop
   usage: Yes`로 잡혀 있어 러너 배정 전에 즉시 차단되고 있었음(추정이 맞았음). 사용자가
   `$5`로 올려 해결.
2. **워크플로 YAML의 실제 버그** — 1번을 해결한 뒤 API로 수동 실행(`workflow_dispatch`)을
   걸어보니 이번엔 파싱 에러가 노출됨: `Unrecognized named-value: 'secrets'` (38번째 줄,
   `if: ${{ secrets.GEMINI_API_KEY != '' }}`). GitHub Actions는 스텝의 `if:` 조건식 안에서
   `secrets` 컨텍스트를 직접 참조할 수 없음 — `env` 컨텍스트만 가능. 이 버그가 사실 처음부터
   있었고, 지출 한도 차단 때문에 여태 이 파싱 단계까지 도달하지 못해 가려져 있었던 것으로
   보임(그래서 그동안 모든 실패 run이 한결같이 "job 0개, 로그 없음"으로 보였음).

   `env: GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}`를 job 레벨로 옮기고, 요약 스텝의
   `if:`를 `${{ env.GEMINI_API_KEY != '' }}`로 바꿔 해결. `python3 -c "import yaml; ..."`로
   문법 재검증.

`main` 머지(PR #2) 이후 첫 수동 실행에서 발견·수정한 것이라, 이 변경은 새 PR로 다시 `main`에
반영한다.

## [2026-08-28] fix | 워크플로 타임아웃으로 크롤링·요약 결과 전량 유실 → 중간 커밋 + 타임아웃 연장
위 수정 반영 후 `main`에서 `workflow_dispatch`로 처음 성공적으로 돌려본 실행(run #14)이
실제로 어떻게 흘러가는지 지켜봄:

- 홈페이지 재크롤링(280개 URL, `--force`): **05:02:36 → 05:57:34, 55분** 소요 후 성공
- 홈페이지 원문 AI 요약(Gemini, 255명): 05:57:34에 시작해 35분 진행되다 **06:32:43에
  `timeout-minutes: 90` 제한에 걸려 job 전체가 `cancelled`로 강제 종료**됨
- 뒤이은 "위키 재생성"·"커밋 & 푸시" 스텝은 실행되지 못하고 skip — **커밋이 맨 마지막
  스텝에서만 일어나는 구조라, 55분짜리 크롤링 + 35분짜리 부분 요약 결과가 git에 단 한 줄도
  안 남고 통째로 유실됨** (다음 실행 때 크롤링부터 처음부터 다시)

두 가지로 수정:
1. `timeout-minutes: 90` → **180** — 크롤링(~55분) + 요약(255명, 최소 35분 이상 소요 확인됨)
   + 위키 재생성/커밋(수 초~수 분)을 여유 있게 담도록
2. **크롤링 직후 중간 커밋 스텝 추가** — `sources/homepage_crawl.json`을 요약 전에 먼저 한 번
   커밋·푸시해서, 뒤이은 요약 단계가 또 타임아웃 나더라도 제일 비용이 큰 크롤링 결과만큼은
   보존되도록 함. 마지막 커밋 스텝은 요약이 채운 `summary` 필드 + `wiki/`를 그대로 이어서 커밋.

`git config`(사용자명/이메일)도 중복 정의를 피하려고 별도 "Git 사용자 설정" 스텝으로 한 번만
분리.

## [2026-08-28] ingest | 수동 전체 갱신 성공 (크롤링 256/273 + 요약 256명) + 2026-09-01 자동 실행 건너뛰기
위 수정을 반영한 뒤 `main`에서 `workflow_dispatch`로 다시 실행(run #15), 이번엔 끝까지 성공:

- 홈페이지 크롤링: 256/273 성공(7개는 학과 공통 포털로 판단해 제외), 서브페이지 1,441개
- 중간 커밋(`4a9551c` 이전 `78f6fca`) → Gemini 요약 256명 전원 성공(스킵 0, 실패 0) →
  위키 재생성(교원 298명, 학과 16개) → 최종 커밋(`4a9551c`)까지 총 1시간 37분

바로 며칠 뒤인 2026-09-01에 예정된 자동 갱신은 이번에 이미 전체를 새로 갱신했으니 중복이라,
사용자 요청으로 **이번 한 번만 건너뛰도록** `refresh-wiki.yml`에 `gate` job을 추가함 —
`github.event_name == 'schedule'`이고 오늘 날짜가 `2026-09-01`일 때만 건너뛰고, 수동 실행은
이 판단과 무관하게 항상 그대로 실행됨. 2027-03-01 이후 스케줄은 정상 진행. 이 gate는
2026-09-01이 지나면 자연히 무해해지므로 그 뒤 정리 삼아 지워도 됨(파일 내 주석 참고).

## [2026-08-28] bugfix | 논문 목록 줄바꿈 오류 수정 (괄호 안 세미콜론 오분할)
`scripts/build_wiki.py`의 `split_list_items()`가 나열형 텍스트를 `; ` 기준으로 항목을 쪼갤 때,
`(2026; Nature Communications)`처럼 **항목 하나 안의 (연도; 저널명) 괄호 안에 있는 `; `까지**
구분자로 오인해 논문 제목과 저널명이 서로 다른 불릿으로 쪼개지는 문제 발견 (예:
"...classification (2026" / "- Nature Communications)"). 원본 `text_public` 전수 검사 결과
이 패턴이 4,682회 나타나 사실상 전체 논문/실적 목록에 영향 — 298명 중 254명 페이지가
실제로 개선됨.
- 수정: 괄호(`()`/`[]`) 중첩 깊이를 추적해 **깊이 0(괄호 밖)에서만** `; `로 쪼개는
  `split_on_top_level()` 추가, `split_list_items()`가 이를 사용하도록 교체. 순수 표시
  형식만 바꾸는 것이라 원본 내용은 그대로 유지 (No Hallucination 원칙 준수).
- 중첩 괄호(`(A (B))`)와 원본 데이터의 괄호 짝 불일치(5명, 크롤링/실적 원문 자체의
  오탈자) 케이스를 모두 확인 — 깊이가 음수로 내려가지 않도록 방어해 안전하게 처리됨.
  괄호 짝이 안 맞는 원문 자체의 오탈자는 원칙상 고치지 않고 그대로 둠.
- `python3 scripts/build_wiki.py` 재실행으로 `wiki/faculty/*.md` 254개 파일, `wiki/researchers.json` 갱신.
