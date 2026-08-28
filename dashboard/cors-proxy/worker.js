/**
 * dashboard/cors-proxy/worker.js
 *
 * POSTECH AI API (genai.postech.ac.kr, posicube-services/llm-agent-api)는 서버 사이드
 * 클라이언트(httpx/node-fetch) 사용만 상정하고 있어 브라우저에서 dashboard/index.html이
 * 직접 fetch()로 호출하면 CORS 프리플라이트가 막혀 "Failed to fetch" 오류가 납니다.
 *
 * 이 워커는 브라우저 <-> genai.postech.ac.kr 사이에 끼어서
 *   1) 브라우저의 OPTIONS 프리플라이트에 CORS 허용 헤더로 응답하고
 *   2) 실제 요청(POST 등)을 genai.postech.ac.kr 로 그대로 전달한 뒤
 *   3) 응답에 CORS 헤더를 붙여 브라우저로 돌려줍니다.
 * 요청 본문과 x-api-key/Authorization 헤더는 그대로 통과시킬 뿐 이 워커가 들여다보거나
 * 저장하지 않습니다.
 *
 * 배포 방법: dashboard/cors-proxy/README.md 참고 (Cloudflare 대시보드에서 복사/붙여넣기만
 * 하면 됩니다 — CLI 불필요).
 */

const UPSTREAM_ORIGIN = "https://genai.postech.ac.kr";

// 이 프록시로 전달을 허용할 업스트림 경로 접두사 (posicube-services/llm-agent-api 의
// a1~a3 단일 호출 API + a11~a64 Agent API 모두 /agent/ 아래에 있음)
const ALLOWED_PATH_PREFIX = "/agent/";

function corsHeaders(origin) {
  return {
    "Access-Control-Allow-Origin": origin || "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization, x-api-key, x-user-id, x-request-id, x-request-traces",
    "Access-Control-Max-Age": "86400",
  };
}

export default {
  async fetch(request) {
    const origin = request.headers.get("Origin") || "*";

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders(origin) });
    }

    const url = new URL(request.url);
    // 워커 자신의 경로 앞부분(/proxy)을 떼고 genai.postech.ac.kr 쪽 경로로 그대로 매핑
    const upstreamPath = url.pathname.replace(/^\/proxy/, "");

    if (!upstreamPath.startsWith(ALLOWED_PATH_PREFIX)) {
      return new Response(
        JSON.stringify({ error: "이 프록시는 /agent/ 로 시작하는 경로만 전달합니다." }),
        { status: 404, headers: { "Content-Type": "application/json", ...corsHeaders(origin) } }
      );
    }

    const forwardHeaders = new Headers();
    for (const key of ["content-type", "x-api-key", "authorization", "x-user-id", "x-request-id", "x-request-traces"]) {
      const v = request.headers.get(key);
      if (v) forwardHeaders.set(key, v);
    }

    let upstreamRes;
    try {
      upstreamRes = await fetch(UPSTREAM_ORIGIN + upstreamPath + url.search, {
        method: request.method,
        headers: forwardHeaders,
        body: ["GET", "HEAD"].includes(request.method) ? undefined : await request.text(),
      });
    } catch (e) {
      return new Response(
        JSON.stringify({ error: "업스트림(genai.postech.ac.kr) 요청 실패", detail: String(e) }),
        { status: 502, headers: { "Content-Type": "application/json", ...corsHeaders(origin) } }
      );
    }

    const bodyText = await upstreamRes.text();
    return new Response(bodyText, {
      status: upstreamRes.status,
      headers: {
        "Content-Type": upstreamRes.headers.get("content-type") || "application/json",
        ...corsHeaders(origin),
      },
    });
  },
};
