# POSTECH 교원 R&D 위키 (LLM Wiki)

POSTECH R&D 실적 데이터베이스(`data/faculty_profiles_source.json`, 교원 298명)를 원본으로
삼아 자동 생성한 마크다운 지식베이스입니다. 설계는 Karpathy의
["LLM Wiki" 패턴](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)을
따릅니다 — 원본 자료는 그대로 두고, 구조화된 위키 페이지를 별도로 유지·누적하며, 새 자료
(예: 홈페이지 크롤링 결과)가 들어오면 기존 페이지를 다시 생성해 병합합니다.

## 둘러보기

- **[index.md](index.md)** — 전체 진입점 (학과별 인덱스)
- **[faculty-index.md](faculty-index.md)** — 교원 298명 가나다순 전체 목록
- **[research-areas.md](research-areas.md)** — 연구분야 키워드로 교원 찾기
- **[departments/](departments/)** — 학과별 페이지 (16개)
- **[faculty/](faculty/)** — 교원별 페이지 (298개, 파일명 = `개인번호-성명.md`)

GitHub에서 그대로 브라우징해도 되고, Obsidian 등 로컬 마크다운 뷰어로 `wiki/` 폴더를
열면 `[텍스트](경로)` 링크가 그래프/백링크로 연결됩니다.

## 위키를 다시 만들려면

```bash
python3 scripts/build_wiki.py
```

`wiki/faculty/*.md`, `wiki/departments/*.md` 등은 이 명령으로 **자동 생성되는 파일**입니다.
직접 고치지 말고, 원본(`data/faculty_profiles_source.json`)이 바뀌면 다시 실행하세요.
생성 규칙과 원칙은 [SCHEMA.md](SCHEMA.md)에 정리되어 있습니다.

## 교원 홈페이지 정보 (크롤링 완료)

이 저장소를 다루는 Claude Code 원격 환경은 `postech.ac.kr` 등 외부 도메인에 접근할 수 없어
(네트워크 egress 차단) 직접 크롤링하지 못합니다. 대신 로컬 환경에서 `scripts/crawl_homepages.py`
를 실행해 만든 `data/homepage_crawl.json` 을 받아 반영했습니다.

- 대상 URL 280개(중복 제거) 중 **262개 성공** (93.6%)
- 나머지 18개는 사이트 자체 문제(끊긴 링크·서버 다운·봇 차단·자바스크립트 렌더링 등)로
  실패 — 각 교원 페이지의 "홈페이지 추가 정보" 섹션에 실패 사유가 함께 표시됩니다.
  URL 오타·스킴 누락·프레임셋 구조는 `scripts/crawl_homepages.py` 가 자동으로 보정합니다.

다시 크롤링하거나 실패한 항목만 재시도하려면:

```bash
pip install -r scripts/requirements.txt
python3 scripts/crawl_homepages.py      # 기본: 이전에 실패한 URL만 재시도
python3 scripts/crawl_homepages.py --force  # 전부 다시 시도
python3 scripts/build_wiki.py           # 위키에 반영
```

## 알려진 데이터 이슈

- 동명이인 4쌍(이승우, 김영진, 김정훈, 이상민)이 있어 이름이 아닌 **개인번호**가 진짜
  식별자입니다 (파일명이 `개인번호-성명.md`인 이유).
- 박진수(물리학과) 1명은 원본에 홈페이지 URL이 없습니다.
- `관심분야` 등은 자유 서술형 텍스트라 `research-areas.md`의 키워드 집계가 완벽히
  정규화되어 있지는 않습니다 (참고용 인덱스).
