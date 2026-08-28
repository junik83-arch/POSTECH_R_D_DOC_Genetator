#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
summarize_homepages.py — 홈페이지 크롤링 원문을 Gemini API로 요약해 교원 위키에 반영

sources/homepage_crawl.json 에 저장된 크롤링 원문(홈페이지 본문 + 서브페이지)을
Google Gemini API로 교원 1인당 3~5문장으로 요약해 각 엔트리에 "summary" 필드로
저장한다. 이후 scripts/build_wiki.py 를 실행하면 그 요약이 교원 페이지에 반영된다.

이 저장소의 index.html(RFP 공문 생성기)이 이미 Gemini API를 REST로 직접 호출하는
방식을 쓰고 있어(동적 모델 탐색 + 폴백 후보 목록), 같은 패턴을 그대로 따른다 —
별도 SDK를 추가하지 않고 requests 만으로 호출한다.

설치:
    pip install -r scripts/requirements.txt   # requests 만 있으면 됨

환경변수:
    GEMINI_API_KEY   Google AI Studio에서 발급한 API 키
                      (https://aistudio.google.com/app/apikey)

사용법:
    python3 scripts/summarize_homepages.py            # 요약 없거나 원문이 바뀐 것만
    python3 scripts/summarize_homepages.py --force     # 전부 다시 요약
    python3 scripts/summarize_homepages.py --limit 5   # 테스트용 (앞 5명만)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    print("필요한 패키지가 없습니다. 먼저 실행하세요:\n  pip install -r scripts/requirements.txt", file=sys.stderr)
    sys.exit(1)

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_wiki  # noqa: E402 — HOMEPAGE_SUMMARY_NOT_FOUND 등 재사용

ROOT = build_wiki.ROOT
SOURCES_DIR = ROOT / "sources"
SOURCE_FILE = build_wiki.SOURCE_FILE
CRAWL_FILE = build_wiki.CRAWL_FILE

API_BASE = "https://generativelanguage.googleapis.com/v1beta"
# 모델 목록 조회가 실패할 때 쓰는 고정 폴백 (index.html 과 동일한 후보 사상)
FALLBACK_MODELS = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash-latest", "gemini-1.5-flash", "gemini-pro"]
MAX_INPUT_CHARS = 16000  # 원문이 너무 길면 비용/프롬프트 크기를 위해 앞부분만 사용

SYSTEM_INSTRUCTION_TEMPLATE = """당신은 대학교 R&D전략팀을 위해 교원 홈페이지 크롤링 원문을 읽고 사실에 기반한 간결한 요약을 쓰는 도우미입니다.

규칙:
1. 요약 대상은 오직 "{name}" 교수 1인입니다. 원문에 다른 사람 이름(동료 교수, 학생, 공동연구자 등)이 등장하더라도, 그 사람의 성과나 소식을 "{name}" 교수의 것으로 섞어 쓰지 마세요.
2. 원문에 명시되지 않은 사실을 지어내지 마세요.
3. "{name}" 교수 본인에 대한 내용을 명확히 찾을 수 없으면, 다른 내용을 채우지 말고 정확히 이렇게만 답하세요: \"""" + build_wiki.HOMEPAGE_SUMMARY_NOT_FOUND + """\"
4. 한국어로, 3~5문장, 마크다운 서식(굵게·목록·제목 등) 없이 평문으로 작성하세요.
5. 연구 초점, 대표 성과나 프로젝트, 소속/직함처럼 사실 확인이 되는 내용 위주로 쓰세요."""


def fetch_available_models(api_key: str) -> list[str]:
    """index.html의 fetchAvailableModels()와 동일한 로직: 사용 가능한 모델을 조회해
    flash 계열을 우선하도록 정렬한다. 실패하면 고정 폴백 목록을 쓴다."""
    try:
        resp = requests.get(f"{API_BASE}/models", params={"key": api_key}, timeout=15)
        if resp.ok:
            data = resp.json()
            models = [
                m["name"].removeprefix("models/")
                for m in data.get("models", [])
                if "generateContent" in m.get("supportedGenerationMethods", [])
            ]

            def score(name: str) -> int:
                if "2.5-flash" in name:
                    return 110
                if "2.0-flash" in name:
                    return 100
                if "1.5-flash" in name:
                    return 90
                if "flash" in name:
                    return 80
                if "1.5-pro" in name:
                    return 70
                if "pro" in name:
                    return 60
                return 10

            models.sort(key=score, reverse=True)
            if models:
                return models
    except requests.RequestException:
        pass
    return FALLBACK_MODELS


def call_gemini(api_key: str, model: str, system_instruction: str, user_text: str, timeout: float) -> str:
    url = f"{API_BASE}/models/{model}:generateContent"
    body = {
        "systemInstruction": {"parts": [{"text": system_instruction}]},
        "contents": [{"role": "user", "parts": [{"text": user_text}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 600},
    }
    resp = requests.post(url, params={"key": api_key}, json=body, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    candidates = data.get("candidates") or []
    if not candidates:
        raise RuntimeError(f"빈 응답 (promptFeedback: {data.get('promptFeedback')})")
    parts = candidates[0].get("content", {}).get("parts", [])
    text = "".join(p.get("text", "") for p in parts).strip()
    if not text:
        raise RuntimeError("빈 텍스트 응답")
    return text


def summarize_with_fallback(
    api_key: str, models: list[str], system_instruction: str, user_text: str
) -> tuple[str, str]:
    """후보 모델을 순서대로 시도. 429/5xx는 같은 모델로 재시도, 그 외 오류는 다음
    모델로 넘어간다 (index.html의 candidateModels 루프와 동일한 사상)."""
    last_err: Exception | None = None
    for model in models:
        for attempt in range(3):
            try:
                return call_gemini(api_key, model, system_instruction, user_text, timeout=30), model
            except requests.HTTPError as e:
                status = e.response.status_code if e.response is not None else None
                last_err = e
                if status == 429 or (status and status >= 500):
                    time.sleep(2 * (attempt + 1))
                    continue
                break  # 4xx(모델 없음/권한 등) — 다음 모델로 넘어감
            except requests.RequestException as e:
                last_err = e
                time.sleep(1)
    raise last_err or RuntimeError("모든 모델 시도 실패")


def build_input_text(entry: dict) -> str:
    parts = []
    main_text = (entry.get("text") or "").strip()
    if main_text:
        parts.append(f"[홈페이지 첫 화면]\n{main_text}")
    for sub_url, sub in (entry.get("subpages") or {}).items():
        sub_text = (sub.get("text") or "").strip()
        if not sub_text:
            continue
        title = sub.get("title") or sub_url
        parts.append(f"[서브페이지: {title}]\n{sub_text}")
    return "\n\n".join(parts)[:MAX_INPUT_CHARS]


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None, help="처리할 최대 교원 수 (테스트용)")
    ap.add_argument("--force", action="store_true", help="원문이 안 바뀌었어도 전부 다시 요약")
    args = ap.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise SystemExit(
            "GEMINI_API_KEY 환경변수가 없습니다. "
            "https://aistudio.google.com/app/apikey 에서 발급받아 설정하세요."
        )
    if not CRAWL_FILE.exists():
        raise SystemExit(f"크롤링 결과 파일이 없습니다: {CRAWL_FILE} (먼저 scripts/crawl_homepages.py 실행)")

    crawl = json.loads(CRAWL_FILE.read_text(encoding="utf-8"))
    records = json.loads(SOURCE_FILE.read_text(encoding="utf-8")) if SOURCE_FILE.exists() else []
    name_by_url: dict[str, dict] = {}
    for r in records:
        url = (r.get("홈페이지") or "").strip()
        if url:
            name_by_url[url] = r

    models = fetch_available_models(api_key)
    print(f"사용 가능한 모델(우선순위 상위): {models[:5]}")

    targets = [(url, entry) for url, entry in crawl.items() if entry.get("text") and not entry.get("skipped")]
    if args.limit:
        targets = targets[: args.limit]

    print(f"대상 {len(targets)}명")
    summarized = skipped = failed = 0
    for i, (url, entry) in enumerate(targets, 1):
        rec = name_by_url.get(url)
        name = rec["성명"] if rec else "해당 교원"
        input_text = build_input_text(entry)
        if not input_text:
            continue
        h = content_hash(input_text)
        if not args.force and entry.get("summary") and entry.get("summary_source_hash") == h:
            skipped += 1
            continue

        print(f"[{i}/{len(targets)}] {name} ({url})")
        system_instruction = SYSTEM_INSTRUCTION_TEMPLATE.format(name=name)
        user_text = f"다음은 {name} 교수 개인 홈페이지에서 크롤링한 원문입니다.\n\n{input_text}"
        try:
            summary, used_model = summarize_with_fallback(api_key, models, system_instruction, user_text)
            entry["summary"] = summary
            entry["summary_source_hash"] = h
            entry["summary_model"] = used_model
            entry["summary_generated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            summarized += 1
        except Exception as e:  # noqa: BLE001 — 개별 실패는 기록하고 계속 진행
            print(f"  실패: {e}")
            failed += 1
        CRAWL_FILE.write_text(json.dumps(crawl, ensure_ascii=False, indent=2), encoding="utf-8")
        time.sleep(0.5)

    print(f"\n완료: 요약 {summarized}건, 변경없어 건너뜀 {skipped}건, 실패 {failed}건")
    print("다음 단계: python3 scripts/build_wiki.py 를 실행해 위키에 반영하세요.")


if __name__ == "__main__":
    main()
