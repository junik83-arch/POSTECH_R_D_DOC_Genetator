#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
crawl_homepages.py — 교원 홈페이지 크롤러 (로컬 전용)

⚠️ 이 스크립트는 Claude Code 원격 실행 환경(이 세션)에서는 동작하지 않습니다.
   네트워크 정책상 postech.ac.kr 도메인 egress가 차단되어 있기 때문입니다.
   인터넷 접근이 가능한 로컬 PC 등에서 실행하세요.

동작:
    data/faculty_profiles_source.json 의 "홈페이지" URL(중복 제거)을 순회하며
    각 페이지를 요청해 제목/본문 텍스트를 추출한 뒤
    data/homepage_crawl.json 에 { url: {title, text, fetched_at, status} } 형태로 저장합니다.

    이후 `python3 scripts/build_wiki.py` 를 다시 실행하면 wiki/faculty/*.md 의
    "홈페이지 추가 정보" 섹션이 자동으로 채워집니다.

설치:
    pip install -r scripts/requirements.txt

사용법:
    python3 scripts/crawl_homepages.py                # 전체 URL 크롤링 (이미 성공한 URL은 건너뜀)
    python3 scripts/crawl_homepages.py --limit 10      # 앞 10개만 (테스트용)
    python3 scripts/crawl_homepages.py --delay 2.0     # 요청 간 대기시간(초), 기본 1.0
    python3 scripts/crawl_homepages.py --force         # 이미 성공한 URL도 전부 다시 시도
    python3 scripts/crawl_homepages.py --insecure       # SSL 인증서 오류 나는 서버도 시도 (주의)
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("필요한 패키지가 없습니다. 먼저 실행하세요:\n  pip install -r scripts/requirements.txt", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
SOURCE_FILE = DATA_DIR / "faculty_profiles_source.json"
OUTPUT_FILE = DATA_DIR / "homepage_crawl.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; POSTECH-RD-Wiki-Bot/1.0; +for internal faculty wiki)"
}
MAX_CHARS = 4000  # 페이지당 저장할 최대 텍스트 길이 (위키 페이지가 지나치게 비대해지는 것 방지)


def extract_text(html: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "nav", "footer", "header"]):
        tag.decompose()
    title = (soup.title.string or "").strip() if soup.title and soup.title.string else ""
    text = soup.get_text(separator="\n")
    lines = [ln.strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln]
    joined = "\n".join(lines)
    return title, joined[:MAX_CHARS]


def first_frame_src(html: str, base_url: str) -> str | None:
    """옛날 대학 부서 홈페이지는 <frameset>으로 실제 내용을 다른 페이지에 넣어두는
    경우가 많다. <body>가 비어 있어 extract_text가 빈 텍스트를 돌려줄 때, 첫 번째
    <frame>이 가리키는 실제 내용 페이지 URL을 찾아준다 (없으면 None)."""
    soup = BeautifulSoup(html, "html.parser")
    frame = soup.find("frame") or soup.find("iframe")
    if frame and frame.get("src"):
        return urljoin(base_url, frame["src"])
    return None


ZERO_WIDTH_CHARS = "﻿​‌‍\xa0"


def normalize_url(url: str) -> str:
    """요청에 실제로 사용할 URL을 정리한다 (BOM/제로폭 공백 제거, 스킴 누락 보정).

    data/homepage_crawl.json 의 키는 원본 그대로 유지해야 build_wiki.py 의 조회가
    맞아떨어지므로, 이 함수의 결과는 요청에만 쓰고 저장 키에는 쓰지 않는다.
    """
    cleaned = url.strip()
    for ch in ZERO_WIDTH_CHARS:
        cleaned = cleaned.replace(ch, "")
    cleaned = cleaned.strip()
    if "://" not in cleaned:
        cleaned = "https://" + cleaned
    return cleaned


def load_urls() -> list[str]:
    records = json.loads(SOURCE_FILE.read_text(encoding="utf-8"))
    urls = []
    seen = set()
    for r in records:
        url = (r.get("홈페이지") or "").strip()
        if url and url not in seen:
            seen.add(url)
            urls.append(url)
    return urls


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None, help="처리할 최대 URL 개수 (테스트용)")
    ap.add_argument("--delay", type=float, default=1.0, help="요청 간 대기시간(초)")
    ap.add_argument("--timeout", type=float, default=15.0, help="요청 타임아웃(초)")
    ap.add_argument(
        "--force",
        action="store_true",
        help="이미 성공적으로 크롤링된 URL도 다시 시도 (기본값: 실패했던 URL만 재시도)",
    )
    ap.add_argument(
        "--insecure",
        action="store_true",
        help="SSL 인증서 검증을 건너뜀 (postech.ac.kr 일부 서브도메인의 인증서 오류 우회용, 주의해서 사용)",
    )
    args = ap.parse_args()

    if not SOURCE_FILE.exists():
        raise SystemExit(f"원본 파일이 없습니다: {SOURCE_FILE}")

    if args.insecure:
        import urllib3

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    urls = load_urls()
    if args.limit:
        urls = urls[: args.limit]

    result: dict = {}
    if OUTPUT_FILE.exists():
        result = json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))

    print(f"대상 URL {len(urls)}개 (중복 제거됨)")
    for i, url in enumerate(urls, 1):
        if not args.force and result.get(url, {}).get("text"):
            print(f"[{i}/{len(urls)}] {url} — 이미 성공, 건너뜀")
            continue
        print(f"[{i}/{len(urls)}] {url}")
        try:
            fetch_url = normalize_url(url)
            resp = requests.get(
                fetch_url, headers=HEADERS, timeout=args.timeout, verify=not args.insecure
            )
            resp.raise_for_status()
            title, text = extract_text(resp.text)

            # <frameset> 기반 옛날 홈페이지 대응: 본문이 비어 있으면 첫 프레임을 한 번 더 따라간다
            if not text:
                frame_url = first_frame_src(resp.text, fetch_url)
                if frame_url:
                    frame_resp = requests.get(
                        frame_url, headers=HEADERS, timeout=args.timeout, verify=not args.insecure
                    )
                    frame_resp.raise_for_status()
                    frame_title, frame_text = extract_text(frame_resp.text)
                    title = title or frame_title
                    text = frame_text

            result[url] = {
                "title": title,
                "text": text,
                "status": resp.status_code,
                "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
        except Exception as e:  # noqa: BLE001 — 크롤링 스크립트 특성상 개별 실패는 기록하고 계속 진행
            print(f"  실패: {e}")
            result[url] = {
                "title": "",
                "text": "",
                "status": None,
                "error": str(e),
                "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
        OUTPUT_FILE.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        time.sleep(args.delay)

    ok = sum(1 for v in result.values() if v.get("text"))
    print(f"\n완료: {ok}/{len(result)} 성공. 결과 저장: {OUTPUT_FILE}")
    print("다음 단계: python3 scripts/build_wiki.py 를 다시 실행해 위키에 반영하세요.")


if __name__ == "__main__":
    main()
