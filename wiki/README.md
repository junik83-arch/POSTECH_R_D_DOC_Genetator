# POSTECH 교원 R&D 위키 (LLM Wiki)

POSTECH 교원 298명의 R&D 실적 데이터와 홈페이지 크롤링 원문을 원본으로 삼아 LLM이 직접
읽고 종합해 유지하는 지식베이스입니다. **먼저 [home.md](home.md)를 여세요** — 학과별 MOC와
학과를 가로지르는 연구 흐름 종합이 거기 있습니다.

구조·갱신 규칙(스키마)은 저장소 루트의 [CLAUDE.md](../CLAUDE.md)에 있습니다.

## 둘러보기

- **[home.md](home.md)** — 큐레이션된 진입점 (여기서 시작하세요)
- **[index.md](index.md)** — 전체 교원·학과 평면 카탈로그 (기계 생성)
- **[faculty-index.md](faculty-index.md)** — 교원 298명 가나다순 전체 목록
- **[research-areas.md](research-areas.md)** — 연구분야 키워드로 교원 찾기
- **[domain/](domain/)** — 학과별 MOC, 16개 (LLM이 직접 종합)
- **[faculty/](faculty/)** — 교원별 페이지, 298개 (파일명 = `개인번호-성명.md`, 결정론적 생성)
- **[log.md](log.md)** — 이 위키가 어떻게 만들어져 왔는지
- **[open-questions.md](open-questions.md)** — 데이터 모순·미해결 이슈

## 위키를 다시 만들려면

```bash
python3 scripts/build_wiki.py
```

`wiki/faculty/*.md`, `index.md`, `faculty-index.md`, `research-areas.md` 는 이 명령으로
**자동 생성**됩니다 (직접 고치지 마세요 — 원본이 바뀌면 다시 실행). 반면 `home.md`,
`domain/*.moc.md`, `log.md`, `open-questions.md` 는 **이 스크립트가 건드리지 않는** LLM
큐레이션 페이지입니다 — 직접 읽고 고치세요. 두 종류를 구분하는 이유와 원칙은
[CLAUDE.md](../CLAUDE.md)에 있습니다.

## 교원 홈페이지 정보 크롤링 + AI 요약

**매월 1일 자동으로 갱신됩니다** — `.github/workflows/refresh-wiki.yml` 이 GitHub Actions
러너(인터넷 접근 가능)에서 ① 크롤러 전체 재실행 ② Gemini API로 원문 요약(`GEMINI_API_KEY`
시크릿 필요) ③ 위키 재생성을 순서대로 하고 결과를 `main`에 직접 커밋합니다. Actions 탭에서
수동 실행도 가능합니다.

각 교원 페이지의 "AI 생성 요약"은 크롤링 원문을 Gemini가 요약한 것입니다 — 원문은 그
아래 접이식 블록에서 그대로 확인할 수 있습니다. 신뢰도 한계는
[open-questions.md](open-questions.md) 참고.

수동으로 로컬에서 돌리고 싶다면 (이 저장소를 다루는 Claude Code 원격 환경은
`postech.ac.kr` 등 외부 도메인 egress가 차단돼 있어 직접 크롤링은 못 합니다):

```bash
pip install -r scripts/requirements.txt
python3 scripts/crawl_homepages.py            # 기본: 안 끝난 항목만 시도
python3 scripts/crawl_homepages.py --force    # 전부 다시 시도
GEMINI_API_KEY=... python3 scripts/summarize_homepages.py  # 원문 AI 요약 (선택)
python3 scripts/build_wiki.py                 # 위키에 반영
```

현재 상태: 개인 홈페이지 273개 중 255개 성공(93.4%), 서브페이지 1,213개, 학과 공통 포털
7개(24명)는 의도적으로 제외. 자세한 내용은 [open-questions.md](open-questions.md) 참고.
