import assert from "node:assert/strict";
import { afterEach, describe, it } from "node:test";

import { BackendClient } from "../infrastructure/backendClient";

interface CapturedRequest {
  readonly url: string;
  readonly init: RequestInit | undefined;
}

describe("BackendClient", () => {
  const originalFetch = globalThis.fetch;
  const requests: CapturedRequest[] = [];

  afterEach(() => {
    globalThis.fetch = originalFetch;
    requests.length = 0;
  });

  it("checks backend health", async () => {
    globalThis.fetch = async (input: string | URL | Request, init?: RequestInit) => {
      requests.push({ url: input.toString(), init });
      return jsonResponse({ status: "ok", version: "test" });
    };
    const client = new BackendClient(() => "http://127.0.0.1:8765");

    const result = await client.health();

    assert.equal(result.ok, true);
    assert.equal(result.data?.status, "ok");
    assert.equal(result.data?.version, "test");
    assert.equal(requests[0]?.url, "http://127.0.0.1:8765/health");
    assert.equal(requests[0]?.init?.method, "GET");
  });

  it("posts typed chat turns", async () => {
    globalThis.fetch = async (input: string | URL | Request, init?: RequestInit) => {
      requests.push({ url: input.toString(), init });
      return jsonResponse({ message: "ack" });
    };
    const client = new BackendClient(() => "http://127.0.0.1:8765");

    const result = await client.sendChatTurn("hello");

    assert.equal(result.ok, true);
    assert.equal(result.data?.message, "ack");
    assert.equal(requests[0]?.url, "http://127.0.0.1:8765/api/v1/chat/turn");
    assert.equal(requests[0]?.init?.method, "POST");
    assert.deepEqual(JSON.parse(requests[0]?.init?.body?.toString() ?? "{}"), {
      message: "hello",
      source: "vscode",
    });
  });
});

function jsonResponse(body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status: 200,
    headers: {
      "content-type": "application/json",
    },
  });
}
