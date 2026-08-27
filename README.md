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

## 🧠 POSTECH 교원 R&D 위키 (LLM Wiki)

`wiki/` 디렉터리에는 교원 실적 데이터(`sources/faculty_profiles_source.json`, 298명)로부터
생성·종합한 마크다운 지식베이스가 있습니다. 시작은 [wiki/home.md](wiki/home.md), 구조·갱신
규칙은 [CLAUDE.md](CLAUDE.md) 참고.

```bash
python3 scripts/build_wiki.py   # sources/*.json → wiki/faculty/*.md, index.md 등 재생성
```

---

## 📄 라이선스
MIT License
