# CORS 프록시 (POSTECH AI API 브라우저 연동용)

`dashboard/index.html`의 "자연어로 연구자 추천받기"에서 **`❌ 오류: Failed to fetch`**가
뜬다면 거의 확실히 CORS 문제입니다. `posicube-services/llm-agent-api`의 공식 예제(README,
a1_a3_README.md)는 전부 Python `httpx` / Node `node-fetch` 같은 **서버 사이드 클라이언트**만
보여줍니다 — 즉 이 API는 브라우저에서 직접 호출하는 걸 상정하고 있지 않아서, 브라우저가
자동으로 보내는 사전요청(OPTIONS preflight)을 `genai.postech.ac.kr`가 CORS 허용 헤더 없이
응답하고, 그 결과 브라우저의 `fetch()`가 `Failed to fetch`로 실패합니다.

`dashboard/index.html`은 정적 페이지라 서버 코드를 돌릴 수 없으므로, 브라우저와
`genai.postech.ac.kr` 사이에 CORS 헤더를 붙여주는 아주 작은 프록시를 하나 세워야 합니다.
아래 두 방법 모두 신용카드·CLI 설치 없이 됩니다 — **val.town이 메뉴가 더 단순해서 먼저
추천**하고, Cloudflare는 대안으로 남겨둡니다 (대시보드 메뉴 이름/위치가 자주 바뀝니다).

## 1. 진짜 CORS 문제인지 먼저 확인하기 (선택)

브라우저 개발자 도구(F12) → **Network** 탭 → 실패한 요청을 눌러보면:
- 요청 자체가 안 뜨거나 콘솔에 `has been blocked by CORS policy` 문구가 보이면 → 아래 프록시가 정답입니다.
- 요청은 갔는데 401/403 등 에러 코드가 보이면 → API 키가 틀렸거나 만료된 것이니 프록시가 아니라 키를 다시 확인하세요.
- 요청이 아예 오래 걸리다 타임아웃되면 → `genai.postech.ac.kr`가 POSTECH 사내망/VPN 안에서만 열려 있을 수 있습니다.

## 2A. val.town으로 배포하기 (추천 — 메뉴 헤맬 일 없음)

1. https://www.val.town/ 접속 → 우측 상단 **Sign in** → GitHub 계정으로 로그인(가입 자동)
2. 로그인 후 우측 상단 **+ New val** (또는 좌측 **Create** 버튼) 클릭
3. 코드 타입을 고르라고 하면 **HTTP** (HTTP handler / HTTP val) 선택
4. 에디터에 기본으로 들어있는 코드를 전부 지우고, 이 저장소의
   [`valtown.ts`](valtown.ts) 내용을 그대로 붙여넣기
5. 이름을 정하고(예: `postechAiProxy`) 저장(Cmd/Ctrl+S, 또는 저장 버튼) — **별도 "배포" 버튼이
   없습니다.** 저장하는 순간 바로 공개 URL이 생깁니다.
6. 에디터 위쪽이나 val 상세 페이지에 뜨는 `https://<계정명>-<val이름>.web.val.run` 형태 URL을
   복사

## 2B. Cloudflare Worker로 배포하기 (대안)

1. https://dash.cloudflare.com/ 에서 무료 계정 생성 후 로그인
2. 왼쪽 메뉴에서 **Workers & Pages**(또는 최근 개편된 대시보드에서는 **Compute (Workers)** /
   **Workers**라는 이름으로 보일 수 있습니다) 클릭
3. **Create application** 또는 **Create** 버튼 → **Create Worker** (역시 "Start with Hello
   World!" 처럼 다른 문구로 보일 수 있음) 선택
4. 이름은 원하는 대로(예: `postech-ai-proxy`) 입력하고 **Deploy**
5. 방금 만든 워커 → **Edit code** → 에디터 내용을 전부 지우고 이 저장소의
   [`worker.js`](worker.js) 내용을 그대로 붙여넣기 → 우측 상단 **Deploy**

> 위 메뉴가 안 보이면: (a) 좌측 사이드바를 접었다 펴보기, (b) 계정을 새로 만든 직후라면
> 이메일 인증이 안 끝났을 수 있으니 인증 메일 확인, (c) 그래도 안 보이면 val.town(2A)으로
> 진행하세요 — 결과물은 동일합니다.

배포가 끝나면 val.town은 `https://<계정명>-<val이름>.web.val.run`, Cloudflare는
`https://<워커이름>.<your-subdomain>.workers.dev` 형태의 URL이 생깁니다.

## 3. 대시보드에 연결하기

`dashboard/index.html` 우측 상단 **POSTECH AI API 설정**에서 **엔드포인트 URL**을 프록시
주소로 바꿔주세요. val.town과 Cloudflare Worker는 경로 규칙이 다릅니다 —
**val.town은 `/proxy` 접두어 없이**, **Cloudflare Worker는 `/proxy`를 붙여서** 원래 경로를
이어줍니다.

| 모델 | 기존 엔드포인트 (CORS 막힘) | val.town 경유 | Cloudflare Worker 경유 |
|---|---|---|---|
| Claude (a3) | `https://genai.postech.ac.kr/agent/api/a3/claude` | `https://<val주소>/agent/api/a3/claude` | `https://<워커주소>/proxy/agent/api/a3/claude` |
| GPT (a1) | `https://genai.postech.ac.kr/agent/api/a1/gpt` | `https://<val주소>/agent/api/a1/gpt` | `https://<워커주소>/proxy/agent/api/a1/gpt` |
| Gemini (a2) | `https://genai.postech.ac.kr/agent/api/a2/gemini` | `https://<val주소>/agent/api/a2/gemini` | `https://<워커주소>/proxy/agent/api/a2/gemini` |

API 키는 그대로 입력하면 됩니다 (프록시가 `x-api-key`/`Authorization` 헤더를 그대로
통과시킬 뿐 저장하거나 들여다보지 않습니다).

## 참고

- `genai.postech.ac.kr`가 애초에 POSTECH 사내망/VPN에서만 접근 가능하다면, 이 프록시도
  똑같이 사내망 안에서 실행되는 환경(예: 사내 서버)에 올려야 동작합니다 — val.town/Cloudflare
  Workers는 전 세계 엣지에서 실행되므로, 사내망 제한이 있다면 대신 사내 서버에 `worker.js`/
  `valtown.ts`와 동일한 로직을 Express/FastAPI 등으로 옮겨 배포하세요.
- 이 프록시는 요청/응답을 그대로 통과시키기만 하고 로깅하지 않지만, 배포 후에는 누구나 그
  URL로 요청을 보내 여러분의 API 키 사용량에 얹을 수 있습니다. val.town은 기본적으로 코드가
  공개되니(비공개로 만들 수도 있음) 민감한 값을 하드코딩하지 마세요 — 이 코드는 API 키를
  요청 헤더로만 받아 그대로 전달할 뿐 코드에 값이 들어가지 않습니다. 필요하면 코드에 Origin
  화이트리스트(예: 여러분의 GitHub Pages 도메인만 허용)를 추가해 더 제한할 수 있습니다.
