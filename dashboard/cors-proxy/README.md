# CORS 프록시 (POSTECH AI API 브라우저 연동용)

`dashboard/index.html`의 "자연어로 연구자 추천받기"에서 **`❌ 오류: Failed to fetch`**가
뜬다면 거의 확실히 CORS 문제입니다. `posicube-services/llm-agent-api`의 공식 예제(README,
a1_a3_README.md)는 전부 Python `httpx` / Node `node-fetch` 같은 **서버 사이드 클라이언트**만
보여줍니다 — 즉 이 API는 브라우저에서 직접 호출하는 걸 상정하고 있지 않아서, 브라우저가
자동으로 보내는 사전요청(OPTIONS preflight)을 `genai.postech.ac.kr`가 CORS 허용 헤더 없이
응답하고, 그 결과 브라우저의 `fetch()`가 `Failed to fetch`로 실패합니다.

`dashboard/index.html`은 정적 페이지라 서버 코드를 돌릴 수 없으므로, 브라우저와
`genai.postech.ac.kr` 사이에 CORS 헤더를 붙여주는 아주 작은 프록시(`worker.js`)를 하나 세워야
합니다. Cloudflare Workers 무료 티어면 충분하고, 신용카드나 CLI 설치 없이 대시보드에서
복사/붙여넣기만 하면 됩니다.

## 1. 진짜 CORS 문제인지 먼저 확인하기 (선택)

브라우저 개발자 도구(F12) → **Network** 탭 → 실패한 요청을 눌러보면:
- 요청 자체가 안 뜨거나 콘솔에 `has been blocked by CORS policy` 문구가 보이면 → 아래 프록시가 정답입니다.
- 요청은 갔는데 401/403 등 에러 코드가 보이면 → API 키가 틀렸거나 만료된 것이니 프록시가 아니라 키를 다시 확인하세요.
- 요청이 아예 오래 걸리다 타임아웃되면 → `genai.postech.ac.kr`가 POSTECH 사내망/VPN 안에서만 열려 있을 수 있습니다.

## 2. Cloudflare Worker 배포 (2분)

1. https://dash.cloudflare.com/ 에서 무료 계정 생성 후 로그인
2. 왼쪽 메뉴 **Workers & Pages** → **Create** → **Create Worker**
3. 이름은 원하는 대로(예: `postech-ai-proxy`) 입력하고 **Deploy** (기본 "Hello World" 코드로 일단 배포됨)
4. 방금 만든 워커 → **Edit code** 클릭 → 에디터 안 내용을 전부 지우고, 이 저장소의
   [`worker.js`](worker.js) 내용을 그대로 붙여넣기
5. 우측 상단 **Deploy** 클릭

배포가 끝나면 `https://postech-ai-proxy.<your-subdomain>.workers.dev` 같은 URL이 생깁니다.

## 3. 대시보드에 연결하기

`dashboard/index.html` 우측 상단 **POSTECH AI API 설정**에서 **엔드포인트 URL**을 다음처럼
워커 주소 + `/proxy` + 원래 경로로 바꿔주세요.

| 모델 | 기존 엔드포인트 (CORS 막힘) | 워커 경유 엔드포인트 |
|---|---|---|
| Claude (a3) | `https://genai.postech.ac.kr/agent/api/a3/claude` | `https://<워커주소>/proxy/agent/api/a3/claude` |
| GPT (a1) | `https://genai.postech.ac.kr/agent/api/a1/gpt` | `https://<워커주소>/proxy/agent/api/a1/gpt` |
| Gemini (a2) | `https://genai.postech.ac.kr/agent/api/a2/gemini` | `https://<워커주소>/proxy/agent/api/a2/gemini` |

API 키는 그대로 입력하면 됩니다 (워커가 `x-api-key`/`Authorization` 헤더를 그대로 통과시킬
뿐 저장하거나 들여다보지 않습니다).

## 참고

- `genai.postech.ac.kr`가 애초에 POSTECH 사내망/VPN에서만 접근 가능하다면, 이 프록시도
  똑같이 사내망 안에서 실행되는 환경(예: 사내 서버)에 올려야 동작합니다 — Cloudflare Workers는
  전 세계 엣지에서 실행되므로, 사내망 제한이 있다면 대신 사내 서버에 이 `worker.js`와 동일한
  로직을 Express/FastAPI 등으로 옮겨 배포하세요.
- 이 워커는 요청/응답을 그대로 통과시키기만 하고 로깅하지 않지만, 배포 후에는 누구나 그
  워커 URL로 요청을 보내 여러분의 API 키 사용량에 얹을 수 있습니다. 필요하면 워커 코드에
  Origin 화이트리스트(예: 여러분의 GitHub Pages 도메인만 허용)를 추가하세요.
