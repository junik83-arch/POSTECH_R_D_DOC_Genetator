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
  1. 팀원이 메신저/메일에서 위 링크를 **클릭 한 번**만 하면 끝납니다.
  2. 웹앱이 API 키를 자동으로 인식하여 팀원 PC 브라우저에 저장하고, 주소창에서 `?key=...` 부분을 자동으로 삭제해 깔끔한 주소로 변경해 줍니다.
  3. 이후 팀원은 주소창을 북마크(즐겨찾기)해두고 키 입력 없이 언제든지 바로 사용할 수 있습니다!
* **보안상 이점**:
  * GitHub 저장소 코드에는 API 키가 전혀 포함되지 않으므로 **GitHub 자동 차단 위험 0%**
  * 팀원들에게 API 키 발급/복사-붙여넣기 과정을 요구하지 않아 **최고의 편의성 제공**

---

## ✨ 주요 기능

1. **🤖 Gemini AI 기반 RFP 문서 자동 분석**:
   - **지원 포맷**: PDF, HWPX, 이미지(JPG, PNG), TXT 파일 및 텍스트 직접 붙여넣기 지원
   - **스마트 추출**: 사업명, 공고기관, 사업유형(A/B/C), 사업목적, 지원규모, 주요일정, 지원대상, 필수이행사항, 첨부파일명 등 자동 추출
   - **원문 충실 원칙 (No Hallucination)**: RFP에 명시되지 않은 정보는 임의 창작 없이 `[RFP 미기재]`로 자동 처리
2. **📋 3가지 사업 유형 자동 분기**:
   - **유형 A (외부·교내심의)**: 대학 신청 과제 수 제한이 있어 교내 선발/심의가 필요한 사업
   - **유형 B (외부·단순안내)**: 단순 공고 안내 및 교내 동향 파악 목적 사업
   - **유형 C (내부사업)**: POSTECH 자체 내부 연구지원사업
3. **📄 가독성 최적화 공문 서식 & 자가검증**:
   - 들여쓰기(`- ` 불릿) 및 줄바꿈이 완벽하게 정돈된 실시간 미리보기
   - 5단계 자가검증 체크리스트를 통한 필수 항목 누락 방지
4. **⚡ 원클릭 내보내기**:
   - 클립보드 원클릭 복사 (그룹웨어, 한글HWP, 메일 등에 붙여넣기 시 들여쓰기 서식 유지)
   - `[공문]사업명.txt` 파일 다운로드 지원

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
git commit -m "feat: POSTECH Smart Doc Generator with AI & Secret Link"
git branch -M main
git remote add origin https://github.com/<본인아이디>/postech-doc-generator.git
git push -u origin main
```

### 3단계: GitHub Pages 활성화
1. GitHub 저장소의 `Settings` -> `Pages` 이동
2. Branch를 `main`으로 선택하고 `Save` 클릭
3. 잠시 후 상단에 생성된 주소 확인: `https://<본인아이디>.github.io/postech-doc-generator/`

---

## 📄 라이선스
MIT License
