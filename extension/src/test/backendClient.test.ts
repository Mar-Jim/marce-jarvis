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

  it("loads todos", async () => {
    globalThis.fetch = async (input: string | URL | Request, init?: RequestInit) => {
      requests.push({ url: input.toString(), init });
      return jsonResponse([
        {
          id: "todo-1",
          title: "Review SQL",
          description: "",
          status: "pending",
          priority: "medium",
          source: "vscode",
          created_at: "2026-05-17T00:00:00Z",
          updated_at: "2026-05-17T00:00:00Z",
        },
      ]);
    };
    const client = new BackendClient(() => "http://127.0.0.1:8765");

    const result = await client.listTodos();

    assert.equal(result.ok, true);
    assert.equal(result.data?.[0]?.title, "Review SQL");
    assert.equal(requests[0]?.url, "http://127.0.0.1:8765/todos");
    assert.equal(requests[0]?.init?.method, "GET");
  });

  it("creates todos", async () => {
    globalThis.fetch = async (input: string | URL | Request, init?: RequestInit) => {
      requests.push({ url: input.toString(), init });
      return jsonResponse({
        id: "todo-1",
        title: "Review bundle",
        description: "Check target config",
        status: "pending",
        priority: "high",
        source: "vscode",
        created_at: "2026-05-17T00:00:00Z",
        updated_at: "2026-05-17T00:00:00Z",
      });
    };
    const client = new BackendClient(() => "http://127.0.0.1:8765");

    const result = await client.createTodo({
      title: "Review bundle",
      description: "Check target config",
      priority: "high",
      source: "vscode",
    });

    assert.equal(result.ok, true);
    assert.equal(requests[0]?.url, "http://127.0.0.1:8765/todos");
    assert.equal(requests[0]?.init?.method, "POST");
    assert.deepEqual(JSON.parse(requests[0]?.init?.body?.toString() ?? "{}"), {
      title: "Review bundle",
      description: "Check target config",
      priority: "high",
      source: "vscode",
    });
  });

  it("updates todo status", async () => {
    globalThis.fetch = async (input: string | URL | Request, init?: RequestInit) => {
      requests.push({ url: input.toString(), init });
      return jsonResponse({
        id: "todo-1",
        title: "Review bundle",
        description: "",
        status: "done",
        priority: "medium",
        source: "vscode",
        created_at: "2026-05-17T00:00:00Z",
        updated_at: "2026-05-17T00:01:00Z",
      });
    };
    const client = new BackendClient(() => "http://127.0.0.1:8765");

    const result = await client.patchTodo("todo-1", { status: "done" });

    assert.equal(result.ok, true);
    assert.equal(requests[0]?.url, "http://127.0.0.1:8765/todos/todo-1");
    assert.equal(requests[0]?.init?.method, "PATCH");
    assert.deepEqual(JSON.parse(requests[0]?.init?.body?.toString() ?? "{}"), {
      status: "done",
    });
  });

  it("retries transient backend failures", async () => {
    let attempt = 0;
    globalThis.fetch = async (input: string | URL | Request, init?: RequestInit) => {
      requests.push({ url: input.toString(), init });
      attempt += 1;
      if (attempt === 1) {
        return jsonResponse({ detail: "temporary" }, 503);
      }
      return jsonResponse({ status: "ok", version: "test" });
    };
    const client = new BackendClient(() => "http://127.0.0.1:8765", 1);

    const result = await client.health();

    assert.equal(result.ok, true);
    assert.equal(requests.length, 2);
  });
});

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "content-type": "application/json",
    },
  });
}
