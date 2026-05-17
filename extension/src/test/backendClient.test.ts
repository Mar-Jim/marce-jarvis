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
          external_provider: null,
          external_id: null,
          external_url: null,
          category: "normal",
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
        external_provider: null,
        external_id: null,
        external_url: null,
        category: "normal",
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
        external_provider: "azure_devops",
        external_id: "todo-1",
        external_url: "https://example.test",
        category: "in_progress",
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

  it("syncs Azure DevOps tickets with PAT header", async () => {
    globalThis.fetch = async (input: string | URL | Request, init?: RequestInit) => {
      requests.push({ url: input.toString(), init });
      return jsonResponse({
        synced_count: 1,
        todos: [],
      });
    };
    const client = new BackendClient(() => "http://127.0.0.1:8765");

    const result = await client.syncAzureDevOpsTickets(
      { organization: "org", project: "project" },
      "secret-token",
    );

    assert.equal(result.ok, true);
    assert.equal(
      requests[0]?.url,
      "http://127.0.0.1:8765/integrations/azure-devops/sync",
    );
    assert.equal(getHeader(requests[0]?.init?.headers, "X-Azure-DevOps-PAT"), "secret-token");
    assert.deepEqual(JSON.parse(requests[0]?.init?.body?.toString() ?? "{}"), {
      organization: "org",
      project: "project",
    });
  });

  it("updates Azure DevOps ticket progress with PAT header", async () => {
    globalThis.fetch = async (input: string | URL | Request, init?: RequestInit) => {
      requests.push({ url: input.toString(), init });
      return jsonResponse({ updated: true });
    };
    const client = new BackendClient(() => "http://127.0.0.1:8765");

    const result = await client.updateAzureDevOpsTicket(
      {
        organization: "org",
        project: "project",
        work_item_id: "123",
        state: "Active",
      },
      "secret-token",
    );

    assert.equal(result.ok, true);
    assert.equal(
      requests[0]?.url,
      "http://127.0.0.1:8765/integrations/azure-devops/update-progress",
    );
    assert.equal(getHeader(requests[0]?.init?.headers, "X-Azure-DevOps-PAT"), "secret-token");
    assert.deepEqual(JSON.parse(requests[0]?.init?.body?.toString() ?? "{}"), {
      organization: "org",
      project: "project",
      work_item_id: "123",
      state: "Active",
    });
  });

  it("syncs Outlook unread emails with Graph token header", async () => {
    globalThis.fetch = async (input: string | URL | Request, init?: RequestInit) => {
      requests.push({ url: input.toString(), init });
      return jsonResponse({
        synced_count: 1,
        todos: [],
      });
    };
    const client = new BackendClient(() => "http://127.0.0.1:8765");

    const result = await client.syncOutlookEmails("graph-token", 10);

    assert.equal(result.ok, true);
    assert.equal(
      requests[0]?.url,
      "http://127.0.0.1:8765/integrations/outlook/sync-unread",
    );
    assert.equal(getHeader(requests[0]?.init?.headers, "X-Microsoft-Graph-Token"), "graph-token");
    assert.deepEqual(JSON.parse(requests[0]?.init?.body?.toString() ?? "{}"), {
      limit: 10,
    });
  });

  it("creates Outlook draft responses only with approval header", async () => {
    globalThis.fetch = async (input: string | URL | Request, init?: RequestInit) => {
      requests.push({ url: input.toString(), init });
      return jsonResponse({ draft_id: "draft-1", web_url: null });
    };
    const client = new BackendClient(() => "http://127.0.0.1:8765");

    const result = await client.createOutlookDraftResponse(
      { message_id: "msg-1", comment: "Thanks" },
      "graph-token",
      true,
    );

    assert.equal(result.ok, true);
    assert.equal(
      requests[0]?.url,
      "http://127.0.0.1:8765/integrations/outlook/draft-response",
    );
    assert.equal(getHeader(requests[0]?.init?.headers, "X-Microsoft-Graph-Token"), "graph-token");
    assert.equal(getHeader(requests[0]?.init?.headers, "X-Approval-Decision"), "approved");
    assert.deepEqual(JSON.parse(requests[0]?.init?.body?.toString() ?? "{}"), {
      message_id: "msg-1",
      comment: "Thanks",
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

function getHeader(headers: HeadersInit | undefined, name: string): string | undefined {
  if (!headers) {
    return undefined;
  }
  if (headers instanceof Headers) {
    return headers.get(name) ?? undefined;
  }
  if (Array.isArray(headers)) {
    return headers.find(([key]) => key.toLowerCase() === name.toLowerCase())?.[1];
  }
  return headers[name];
}
