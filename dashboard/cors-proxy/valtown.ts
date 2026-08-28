/**
 * dashboard/cors-proxy/valtown.ts
 *
 * worker.js(Cloudflare Workers용)와 동일한 CORS 프록시를 val.town(https://val.town)의
 * "HTTP val" 형식으로 옮긴 버전입니다. Cloudflare 대시보드 메뉴를 찾기 어려우면 이쪽이 더
 * 빠릅니다 — 회원가입 → New val → 코드 붙여넣기 → 저장, 끝입니다(별도 배포 버튼도 없음).
 *
 * 배포 방법은 dashboard/cors-proxy/README.md 의 "val.town으로 배포하기" 참고.
 */

const UPSTREAM_ORIGIN = "https://genai.postech.ac.kr";
const ALLOWED_PATH_PREFIX = "/agent/";

function corsHeaders(origin: string) {
  return {
    "Access-Control-Allow-Origin": origin || "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers":
      "Content-Type, Authorization, x-api-key, x-user-id, x-request-id, x-request-traces",
    "Access-Control-Max-Age": "86400",
  };
}

export default async function (req: Request): Promise<Response> {
  const origin = req.headers.get("Origin") || "*";

  if (req.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: corsHeaders(origin) });
  }

  const url = new URL(req.url);

  if (!url.pathname.startsWith(ALLOWED_PATH_PREFIX)) {
    return new Response(
      JSON.stringify({ error: "이 프록시는 /agent/ 로 시작하는 경로만 전달합니다." }),
      { status: 404, headers: { "Content-Type": "application/json", ...corsHeaders(origin) } },
    );
  }

  const forwardHeaders = new Headers();
  for (const key of ["content-type", "x-api-key", "authorization", "x-user-id", "x-request-id", "x-request-traces"]) {
    const v = req.headers.get(key);
    if (v) forwardHeaders.set(key, v);
  }

  let upstreamRes: Response;
  try {
    upstreamRes = await fetch(UPSTREAM_ORIGIN + url.pathname + url.search, {
      method: req.method,
      headers: forwardHeaders,
      body: ["GET", "HEAD"].includes(req.method) ? undefined : await req.text(),
    });
  } catch (e) {
    return new Response(
      JSON.stringify({ error: "업스트림(genai.postech.ac.kr) 요청 실패", detail: String(e) }),
      { status: 502, headers: { "Content-Type": "application/json", ...corsHeaders(origin) } },
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
}
