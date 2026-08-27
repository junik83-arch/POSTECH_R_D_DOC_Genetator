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
- **[researchers.json](researchers.json)** — 위 내용을 브라우저에서 바로 쓸 수 있도록 압축한
  JSON 인덱스. 사람이 읽는 문서가 아니라 **[../dashboard/index.html](../dashboard/index.html)
  연구자 대시보드**가 fetch로 읽는 기계용 산출물입니다 (AI 자연어 검색에 보내는
  `ai_summary` 압축 프로필 포함).
- **[log.md](log.md)** — 이 위키가 어떻게 만들어져 왔는지
- **[open-questions.md](open-questions.md)** — 데이터 모순·미해결 이슈

GitHub에서 그대로 브라우징해도 되고, Obsidian 등 로컬 마크다운 뷰어로 `wiki/` 폴더를
열면 `[텍스트](경로)` 링크가 그래프/백링크로 연결됩니다. 표/카드 형태로 훑어보고 싶다면
`dashboard/index.html`을 여세요 — 학과별 통계, 필터·검색, "LG생활건강 사업 포트폴리오에
맞는 연구자" 같은 자연어 질의로 POSTECH AI API를 통해 연구자를 추천받는 기능을 제공합니다.

## 위키를 다시 만들려면

```bash
python3 scripts/build_wiki.py
```

`wiki/faculty/*.md`, `index.md`, `faculty-index.md`, `research-areas.md`, `researchers.json`
은 이 명령으로 **자동 생성**됩니다 (직접 고치지 마세요 — 원본이 바뀌면 다시 실행). 반면 `home.md`,
`domain/*.moc.md`, `log.md`, `open-questions.md` 는 **이 스크립트가 건드리지 않는** LLM
큐레이션 페이지입니다 — 직접 읽고 고치세요. 두 종류를 구분하는 이유와 원칙은
[CLAUDE.md](../CLAUDE.md)에 있습니다.

## 교원 홈페이지 정보 크롤링

이 저장소를 다루는 Claude Code 원격 환경은 `postech.ac.kr` 등 외부 도메인에 접근할 수 없어
(네트워크 egress 차단 — WebFetch 도구도 동일) 직접 크롤링하지 못합니다. 로컬 환경에서:

```bash
pip install -r scripts/requirements.txt
python3 scripts/crawl_homepages.py            # 기본: 안 끝난 항목만 시도
python3 scripts/crawl_homepages.py --force    # 전부 다시 시도
python3 scripts/build_wiki.py                 # 위키에 반영
```

현재 상태: 개인 홈페이지 273개 중 255개 성공(93.4%), 서브페이지 1,213개, 학과 공통 포털
7개(24명)는 의도적으로 제외. 자세한 내용은 [open-questions.md](open-questions.md) 참고.
