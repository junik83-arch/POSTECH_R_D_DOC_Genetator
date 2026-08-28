# 🏛️ POSTECH R&D전략팀 도구 모음

> **R&D전략팀 업무를 지원하는 웹 도구 모음** — 필요에 따라 하나씩 늘어납니다.

`index.html`을 열면 도구 허브(랜딩 페이지)가 뜨고, 거기서 각 도구로 들어갑니다.

| 도구 | 위치 | 설명 |
|---|---|---|
| 📋 사업 안내 공문 생성기 | [`tools/doc-generator.html`](tools/doc-generator.html) | Google Gemini AI 연동 · RFP/공고문을 분석해 표준 서식의 안내 공문 초안 자동 작성 |
| 🔍 연구자 대시보드 | [`dashboard/index.html`](dashboard/index.html) | POSTECH 교원 298명 통계·검색 + POSTECH AI API 자연어 추천 ([`wiki/`](wiki/) 데이터 기반) |

---

## ⚡ 팀원들을 위한 가장 간편한 공유 방법 (시크릿 링크)

GitHub에 소스코드를 올리고 **GitHub Pages**를 활성화한 뒤, 공문 생성기를 공유할 때 링크 뒤에
`?key=발급받은API키`를 붙여서 1회 전달하세요.

### 🔗 팀원 공유용 시크릿 링크 형식:
```text
https://<본인아이디>.github.io/postech-doc-generator/tools/doc-generator.html?key=AIzaSy...
```

* **동작 방식**:
  1. 팀원이 위 링크를 **클릭 한 번**만 하면 브라우저에 공용 키가 자동 등록됩니다.
  2. 주소창에서 `?key=...` 부분이 자동으로 삭제되어 깔끔한 주소로 정리됩니다.
  3. 이후 팀원은 키 입력 절차 없이 언제든 즐겨찾기로 바로 사용할 수 있습니다!

> 예전에는 루트(`.../postech-doc-generator/?key=...`)가 곧 공문 생성기였습니다. 이제 루트는
> 도구 허브지만, **예전 형식의 링크도 계속 동작합니다** — 허브가 `?key=`를 감지하면 자동으로
> 공문 생성기로 넘겨줍니다. 새로 공유할 때는 위의 새 형식(`tools/doc-generator.html?key=...`)을
> 쓰는 걸 권장합니다.

---

## ✨ 공문 생성기 주요 기능

1. **🤖 Gemini AI 기반 RFP 문서 자동 분석 & 중복 단어 정제**:
   - **지원 포맷**: PDF, HWPX, 이미지(JPG, PNG), TXT 파일 및 텍스트 직접 붙여넣기 지원
   - **스마트 추출 & 중복 필터링**: '사업 공고 공고' 등 접미사 중복 방지 정제 및 사업명, 공고기관, 사업목적, 지원규모, 주요일정, 지원대상, 필수이행사항 자동 추출
   - **원문 충실 원칙 (No Hallucination)**: RFP에 명시되지 않은 정보는 임의 창작 없이 `[RFP 미기재]`로 자동 처리
2. **📋 3가지 사업 유형 자동 분기**:
   - **유형 A (외부·교내심의)**: 대학 신청 과제 수 제한이 있어 교내 선발/심의가 필요한 사업
   - **유형 B (외부·단순안내)**: 단순 공고 안내 및 교내 동향 파악 목적 사업
   - **유형 C (내부사업)**: POSTECH 자체 내부 연구지원사업
3. **📄 가독성 최적화 공문 서식 & 자가검증**:
   - 들여쓰기(`- ` 불릿) 및 줄바꿈이 완벽하게 정돈된 실시간 미리보기
   - 5단계 자가검증 체크리스트를 통한 필수 항목 누락 방지
4. **📋 전자결재 맞춤 '공문 본문 복사' & 파일 다운로드**:
   - **[공문 본문 복사 (1~5번)]**: 제목·붙임 등을 제외한 **공문 본문(1번 ~ 5번 조항)만 정돈된 들여쓰기 서식으로 클립보드에 복사** (전자결재 기안문 본문에 바로 붙여넣기 최적화)
   - **[.txt 내려받기 (전체)]**: 보관 및 출력용 전체 양식 텍스트 파일 저장 지원

---

## 🔍 연구자 대시보드 (LLM Wiki 기반, AI 자연어 추천)

`dashboard/index.html` — LLM Wiki를 브라우저에서 바로 탐색할 수 있는 대시보드입니다.
`python3 scripts/build_wiki.py` 실행 시 함께 생성되는 `wiki/researchers.json`을 fetch로
읽어와 동작하며(별도 서버·빌드 불필요), 다음 기능을 제공합니다.

- **현황 통계**: 전체 교원 수, 학과 수, 학과별 인원 분포, 실적(논문·특허·과제 등) 합계
- **디렉터리 탐색**: 이름/학과/연구관심분야/키워드 검색, 학과 필터, 정렬, 카드 클릭 시
  실적·연구키워드·대표연구 등을 담은 상세 프로필 모달
- **🤖 자연어 연구자 추천**: "LG생활건강의 사업 포트폴리오에 맞는 연구를 하는 연구자"처럼
  자연어로 질의하면 **POSTECH AI API**로 (1) 질의를 연구분야 키워드/학과로 확장 →
  (2) 브라우저에서 로컬로 후보를 1차 압축 → (3) 압축된 후보 프로필과 원 질의를 다시 AI에
  보내 관련도 순 추천 + 근거를 받아오는 2단계 파이프라인으로 동작합니다. 추천 이유는
  원본 위키 데이터에 실제로 있는 내용에만 근거하도록 프롬프트에서 강제합니다(No Hallucination).

**AI API 연동 방식**: [posicube-services/llm-agent-api](https://github.com/posicube-services/llm-agent-api)의
**a1~a3 단일 호출 API** 규격을 사용합니다.

- 엔드포인트: `POST https://genai.postech.ac.kr/agent/api/a{1|2|3}/{gpt|gemini|claude}`
- 요청: `{"message": "...", "stream": false}` / 응답: `{"message": "..."}`
- 헤더: `x-api-key: <API 키>` 필수, Claude·Gemini는 `Authorization: <API 키>`도 함께 전송
  (Bearer 접두어 없음 — GPT는 `x-api-key`만 사용)

대시보드 우측 상단 **POSTECH AI API 설정** 버튼에서 모델(GPT/Gemini/Claude)·엔드포인트·API
Key를 입력하면 브라우저 LocalStorage에만 저장되어 즉시 사용할 수 있습니다.

> ⚠️ 이 대시보드는 순수 정적 페이지에서 브라우저가 직접 `genai.postech.ac.kr`로 요청을
> 보내는데, 이 게이트웨이는 브라우저 간 요청(CORS)을 막아 두고 있어 그대로는
> `Failed to fetch`가 납니다. [dashboard/cors-proxy/](dashboard/cors-proxy/)에 CORS
> 헤더를 붙여 중계하는 프록시(Cloudflare Worker / val.town 버전)와 배포 방법이
> 준비되어 있으니, 대시보드 **POSTECH AI API 설정**의 엔드포인트를 그 프록시 주소로
> 바꿔서 쓰세요.

---

## 🚀 GitHub 저장소 업로드 및 배포 가이드

### 1단계: GitHub 새 저장소 생성
1. [GitHub](https://github.com/) 로그인 후 `New repository` 클릭
2. Repository name: `postech-doc-generator` 입력 후 `Create repository` 클릭

### 2단계: 터미널에서 코드 업로드
```powershell
cd C:\Users\user\.gemini\antigravity\scratch\postech-doc-generator
git init
git add .
git commit -m "feat: POSTECH Smart Doc Generator with body-only copy & title sanitization"
git branch -M main
git remote add origin https://github.com/<본인아이디>/postech-doc-generator.git
git push -u origin main
```

### 3단계: GitHub Pages 활성화
1. GitHub 저장소의 `Settings` -> `Pages` 이동
2. Branch를 `main`으로 선택하고 `Save` 클릭
3. 잠시 후 상단에 생성된 주소 확인: `https://<본인아이디>.github.io/postech-doc-generator/`
   (도구 허브가 뜹니다 — 개별 도구는 위 표의 경로로 들어갑니다)

> ⚠️ 저장소 루트의 `.nojekyll` 파일을 지우지 마세요. GitHub Pages는 기본적으로 Jekyll로
> 사이트를 빌드하는데, `wiki/**/*.md`처럼 YAML 프런트매터(`---`)로 시작하는 마크다운 파일을
> Jekyll이 "페이지"로 인식해 다른 경로로 변환해버려 `wiki/domain/*.moc.md`, `wiki/faculty/*.md`
> 같은 링크가 전부 404가 납니다. `.nojekyll`은 Jekyll 처리를 끄고 모든 파일을 있는 그대로
> 정적 서빙하게 만들어 이 문제를 막습니다.

---

## 📄 라이선스
MIT License
