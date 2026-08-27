# 🏛️ POSTECH R&D전략팀 스마트 사업 안내 공문 생성기
> **Google Gemini AI 연동 · RFP/공고문 자동 분석 및 표준 공문 작성 도구**

포항공과대학교(POSTECH) 연구처 R&D전략팀에서 사용하는 사업 안내 공문을 표준 서식에 맞춰 신속하고 정확하게 작성할 수 있도록 지원하는 웹 애플리케이션입니다.

---

## ⚡ 팀원들을 위한 가장 간편한 공유 방법 (시크릿 링크)

GitHub에 소스코드를 올리고 **GitHub Pages**를 활성화한 뒤, 팀원들에게 공유할 때 링크 뒤에 `?key=발급받은API키`를 붙여서 1회 전달하세요.

### 🔗 팀원 공유용 시크릿 링크 형식:
```text
https://<본인아이디>.github.io/postech-doc-generator/?key=AIzaSy...
```

* **동작 방식**:
  1. 팀원이 위 링크를 **클릭 한 번**만 하면 브라우저에 공용 키가 자동 등록됩니다.
  2. 주소창에서 `?key=...` 부분이 자동으로 삭제되어 깔끔한 주소로 정리됩니다.
  3. 이후 팀원은 키 입력 절차 없이 언제든 즐겨찾기로 바로 사용할 수 있습니다!

---

## ✨ 주요 기능

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

---

---

## 🧠 POSTECH 교원 R&D 위키 (LLM Wiki)

`wiki/` 디렉터리에는 교원 실적 데이터(`data/faculty_profiles_source.json`, 298명)로부터
생성한 마크다운 지식베이스가 있습니다. 자세한 내용은 [wiki/README.md](wiki/README.md) 참고.

```bash
python3 scripts/build_wiki.py   # data/*.json → wiki/**/*.md + wiki/researchers.json 재생성
```

---

## 🧑‍🔬 연구자 대시보드 (LLM Wiki 기반, AI 자연어 추천)

`dashboard/index.html` — 위 LLM Wiki를 브라우저에서 바로 탐색할 수 있는 대시보드입니다.
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

**AI API 연동 방식**: 기본값은 OpenAI Chat Completions 호환 규격
(`POST {Base URL}/chat/completions`, `Authorization: Bearer <key>`)을 가정합니다.
대시보드 우측 상단 **POSTECH AI API 설정** 버튼에서 Base URL·API Key·모델명을 입력하면
브라우저 LocalStorage에만 저장되어 즉시 사용할 수 있습니다. 실제 POSTECH AI API 게이트웨이의
요청/응답 규격이 다르다면 `dashboard/index.html`의 `callChatApi()` 함수만 수정하면 됩니다.

```bash
# 로컬에서 열어보기 (fetch가 file:// 를 막는 브라우저가 있으므로 정적 서버 권장)
python3 -m http.server 8000
# 이후 http://localhost:8000/dashboard/ 접속
```

---

## 📄 라이선스
MIT License
