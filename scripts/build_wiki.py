#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_wiki.py — POSTECH 교원 LLM Wiki 생성기

data/faculty_profiles_source.json (원본, 필수)
data/homepage_crawl.json          (홈페이지 크롤링 결과, 선택 — scripts/crawl_homepages.py 로 생성)

위 두 소스만 읽어서 wiki/ 아래 마크다운 파일들을 결정론적으로 (재실행해도 동일한 결과가
나오도록) 생성합니다. wiki/**/*.md 는 직접 손으로 수정하지 마세요 — 원본을 고치고 다시
이 스크립트를 실행하세요. 자세한 설계 원칙은 wiki/SCHEMA.md 참고.

사용법:
    python3 scripts/build_wiki.py
"""
from __future__ import annotations

import json
import re
from collections import Counter, OrderedDict, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
WIKI_DIR = ROOT / "wiki"
SOURCE_FILE = DATA_DIR / "faculty_profiles_source.json"
CRAWL_FILE = DATA_DIR / "homepage_crawl.json"

BUILD_DATE = date.today().isoformat()

# text_public 안에서 "라벨: 내용" 한 줄짜리 필드로 나오는 라벨들
KV_LINE_RE = re.compile(r"^([^:\[\]]{1,24}):\s?(.*)$")
# text_public 안에서 "[라벨] 내용" 형태로 나오는 필드들
BRACKET_LINE_RE = re.compile(r"^\[([^\]]+)\]\s*(.*)$")

# 교원 페이지 안에서 이미 별도 섹션(관심분야/실적건수)으로 렌더링하므로
# text_public 파싱 결과에서는 건너뛰는 라벨
SKIP_LABELS = {"성명", "연구관심분야"}


def slugify_dept(name: str) -> str:
    return (name or "미분류").strip()


def dept_link(dept: str) -> str:
    return f"[{dept}](../departments/{slugify_dept(dept)}.md)"


def faculty_filename(rec: dict) -> str:
    return f"{rec['개인번호']}-{rec['성명']}.md"


def faculty_link_from(rec: dict, relative_prefix: str = "../faculty/") -> str:
    return f"[{rec['성명']}]({relative_prefix}{faculty_filename(rec)})"


def parse_text_public(text: str) -> "OrderedDict[str, str]":
    """text_public을 줄 단위로 훑어 {섹션명: 내용} 순서를 보존한 딕셔너리로 변환."""
    sections: "OrderedDict[str, str]" = OrderedDict()
    current = None
    for raw_line in (text or "").split("\n"):
        line = raw_line.rstrip()
        if not line.strip():
            continue
        m = BRACKET_LINE_RE.match(line)
        if m:
            label, content = m.group(1).strip(), m.group(2).strip()
            sections[label] = content
            current = label
            continue
        m = KV_LINE_RE.match(line)
        if m:
            label, content = m.group(1).strip(), m.group(2).strip()
            sections[label] = content
            current = label
            continue
        # 어느 패턴에도 안 맞으면 직전 섹션의 연속으로 취급
        if current is not None:
            sections[current] += " " + line.strip()
    return sections


def render_perf_table(perf: dict) -> str:
    if not perf:
        return "_실적 데이터 없음_\n"
    header = "| 구분 | 건수 |\n|---|---|\n"
    rows = "".join(f"| {k} | {v} |\n" for k, v in perf.items())
    return header + rows


def render_faculty_page(rec: dict, crawl: dict) -> str:
    name = rec["성명"]
    dept = rec.get("학과", "").strip() or "미분류"
    email = rec.get("이메일", "") or "_기재 없음_"
    homepage = rec.get("홈페이지", "") or ""
    interests = rec.get("관심분야", "") or "_기재 없음_"
    perf = rec.get("실적건수", {}) or {}

    parsed = parse_text_public(rec.get("text_public", ""))

    lines = []
    lines.append("---")
    lines.append(f"id: {rec['개인번호']}")
    lines.append(f"name: {name}")
    lines.append(f"department: {dept}")
    lines.append(f"email: {email}")
    lines.append(f"homepage: {homepage}")
    lines.append(f"updated: {BUILD_DATE}")
    lines.append("---")
    lines.append("")
    lines.append(f"# {name} ({dept})")
    lines.append("")
    lines.append("## 기본 정보")
    lines.append(f"- 학과: {dept_link(dept)}")
    lines.append(f"- 이메일: {email}")
    if homepage:
        lines.append(f"- 홈페이지: <{homepage}>")
    else:
        lines.append("- 홈페이지: _등록된 홈페이지 없음_")
    lines.append("")
    lines.append("## 연구관심분야")
    lines.append(interests)
    lines.append("")
    lines.append("## 실적 요약")
    lines.append(render_perf_table(perf))

    for label, content in parsed.items():
        if label in SKIP_LABELS:
            continue
        lines.append(f"## {label}")
        lines.append(content)
        lines.append("")

    lines.append("## 홈페이지 추가 정보")
    crawled = crawl.get(homepage) if homepage else None
    if crawled and crawled.get("text"):
        lines.append(f"> 크롤링 시각: {crawled.get('fetched_at', '알 수 없음')} · 출처: <{homepage}>")
        lines.append("")
        lines.append(crawled["text"].strip())
    elif not homepage:
        lines.append("_등록된 홈페이지가 없어 크롤링 대상이 아닙니다._")
    else:
        lines.append(
            "_아직 크롤링되지 않았습니다. `scripts/crawl_homepages.py` 를 인터넷 접근이 "
            "가능한 환경에서 실행해 `data/homepage_crawl.json` 을 만든 뒤 "
            "`scripts/build_wiki.py` 를 다시 실행하면 이 섹션이 채워집니다._"
        )
    lines.append("")

    lines.append("## 출처")
    lines.append(f"- POSTECH R&D 실적 데이터베이스 (개인번호 {rec['개인번호']})")
    lines.append(f"- 최종 갱신: {BUILD_DATE}")
    lines.append("")

    return "\n".join(lines)


def render_department_page(dept: str, members: list[dict]) -> str:
    members_sorted = sorted(members, key=lambda r: r["성명"])
    total_perf = Counter()
    for r in members:
        for k, v in (r.get("실적건수") or {}).items():
            total_perf[k] += v

    lines = []
    lines.append("---")
    lines.append(f"department: {dept}")
    lines.append(f"faculty_count: {len(members)}")
    lines.append(f"updated: {BUILD_DATE}")
    lines.append("---")
    lines.append("")
    lines.append(f"# {dept}")
    lines.append("")
    lines.append(f"- 소속 교원 수: **{len(members)}명**")
    lines.append("")
    lines.append("## 학과 전체 실적 합계")
    lines.append(render_perf_table(dict(total_perf)))
    lines.append("## 교원 목록")
    for r in members_sorted:
        interests = (r.get("관심분야") or "").replace("￭", "").strip()
        interests_short = interests[:80] + ("…" if len(interests) > 80 else "")
        lines.append(f"- {faculty_link_from(r)} — {interests_short}")
    lines.append("")
    lines.append("[← 전체 인덱스로](../index.md)")
    lines.append("")
    return "\n".join(lines)


def render_index(records: list[dict], by_dept: dict[str, list[dict]]) -> str:
    lines = []
    lines.append("---")
    lines.append("title: POSTECH 교원 R&D 위키")
    lines.append(f"faculty_count: {len(records)}")
    lines.append(f"updated: {BUILD_DATE}")
    lines.append("---")
    lines.append("")
    lines.append("# POSTECH 교원 R&D 위키")
    lines.append("")
    lines.append(
        "POSTECH R&D 실적 데이터베이스를 원본(source)으로 삼아 생성한 교원 지식베이스입니다. "
        "구조와 갱신 규칙은 [SCHEMA.md](SCHEMA.md) 를 참고하세요."
    )
    lines.append("")
    lines.append(f"- 전체 교원: **{len(records)}명**")
    lines.append(f"- 학과 수: **{len(by_dept)}개**")
    lines.append(f"- 최종 생성일: {BUILD_DATE}")
    lines.append("")
    lines.append("## 학과별 인덱스")
    lines.append("")
    for dept in sorted(by_dept.keys()):
        members = by_dept[dept]
        lines.append(f"- [{dept}](departments/{slugify_dept(dept)}.md) ({len(members)}명)")
    lines.append("")
    lines.append("## 기타")
    lines.append("- [연구분야 키워드 인덱스](research-areas.md)")
    lines.append("- [전체 교원 가나다순 목록](faculty-index.md)")
    lines.append("")
    return "\n".join(lines)


def render_faculty_flat_index(records: list[dict]) -> str:
    lines = ["# 전체 교원 가나다순 목록", ""]
    for r in sorted(records, key=lambda r: r["성명"]):
        dept = r.get("학과", "").strip() or "미분류"
        lines.append(f"- {faculty_link_from(r, 'faculty/')} ({dept})")
    lines.append("")
    lines.append("[← 전체 인덱스로](index.md)")
    lines.append("")
    return "\n".join(lines)


def render_research_areas(records: list[dict]) -> str:
    counter: Counter[str] = Counter()
    keyword_to_faculty: defaultdict[str, list[dict]] = defaultdict(list)
    for r in records:
        raw = (r.get("관심분야") or "").replace("￭", "|")
        parts = [p.strip() for p in raw.split("|") if p.strip()]
        for p in parts:
            counter[p] += 1
            keyword_to_faculty[p].append(r)

    lines = ["# 연구분야 키워드 인덱스", ""]
    lines.append(
        "원본 `관심분야` 필드를 그대로 분리·집계한 목록입니다 (자유 서술형 텍스트라 완전히 "
        "정규화되어 있지는 않습니다). 2명 이상이 공유하는 키워드만 표시합니다."
    )
    lines.append("")
    shared = [(k, v) for k, v in counter.items() if v >= 2]
    shared.sort(key=lambda kv: (-kv[1], kv[0]))
    for keyword, count in shared:
        names = ", ".join(faculty_link_from(r, "faculty/") for r in keyword_to_faculty[keyword])
        lines.append(f"- **{keyword}** ({count}명): {names}")
    lines.append("")
    lines.append("[← 전체 인덱스로](index.md)")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    if not SOURCE_FILE.exists():
        raise SystemExit(f"원본 파일이 없습니다: {SOURCE_FILE}")

    records = json.loads(SOURCE_FILE.read_text(encoding="utf-8"))
    crawl = {}
    if CRAWL_FILE.exists():
        crawl = json.loads(CRAWL_FILE.read_text(encoding="utf-8"))

    by_dept: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        dept = (r.get("학과") or "").strip() or "미분류"
        r["학과"] = dept  # 앞뒤 공백(예: " 물리학과") 정규화
        by_dept[dept].append(r)

    faculty_dir = WIKI_DIR / "faculty"
    dept_dir = WIKI_DIR / "departments"
    faculty_dir.mkdir(parents=True, exist_ok=True)
    dept_dir.mkdir(parents=True, exist_ok=True)

    for r in records:
        page = render_faculty_page(r, crawl)
        (faculty_dir / faculty_filename(r)).write_text(page, encoding="utf-8")

    for dept, members in by_dept.items():
        page = render_department_page(dept, members)
        (dept_dir / f"{slugify_dept(dept)}.md").write_text(page, encoding="utf-8")

    (WIKI_DIR / "index.md").write_text(render_index(records, by_dept), encoding="utf-8")
    (WIKI_DIR / "faculty-index.md").write_text(render_faculty_flat_index(records), encoding="utf-8")
    (WIKI_DIR / "research-areas.md").write_text(render_research_areas(records), encoding="utf-8")

    print(f"생성 완료: 교원 {len(records)}명, 학과 {len(by_dept)}개")
    print(f"  wiki/faculty/      {len(records)} 개 파일")
    print(f"  wiki/departments/  {len(by_dept)} 개 파일")
    print("  wiki/index.md, wiki/faculty-index.md, wiki/research-areas.md")
    if not crawl:
        print(
            "참고: data/homepage_crawl.json 이 없어 '홈페이지 추가 정보' 섹션은 "
            "플레이스홀더로 채워졌습니다. scripts/crawl_homepages.py 참고."
        )


if __name__ == "__main__":
    main()
