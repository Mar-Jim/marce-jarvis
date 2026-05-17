import type { CreateTodoInput, PatchTodoInput, Todo } from "../domain/todos";

export interface HealthResponse {
  readonly status?: string;
  readonly version?: string;
}

export interface ChatTurnRequest {
  readonly message: string;
  readonly source: "vscode";
}

export interface ChatTurnResponse {
  readonly message?: string;
}

export interface BackendClientResult<T> {
  readonly ok: boolean;
  readonly data?: T;
  readonly error?: string;
}

export type BackendUrlProvider = () => string;

const DEFAULT_RETRY_COUNT = 2;

export class BackendClient {
  public constructor(
    private readonly getBackendUrl: BackendUrlProvider,
    private readonly retryCount = DEFAULT_RETRY_COUNT,
  ) {}

  public async health(): Promise<BackendClientResult<HealthResponse>> {
    return this.getJson<HealthResponse>("/health");
  }

  public async sendChatTurn(message: string): Promise<BackendClientResult<ChatTurnResponse>> {
    return this.postJson<ChatTurnRequest, ChatTurnResponse>("/api/v1/chat/turn", {
      message,
      source: "vscode",
    });
  }

  public async listTodos(): Promise<BackendClientResult<readonly Todo[]>> {
    return this.getJson<readonly Todo[]>("/todos");
  }

  public async createTodo(input: CreateTodoInput): Promise<BackendClientResult<Todo>> {
    return this.postJson<CreateTodoInput, Todo>("/todos", input);
  }

  public async patchTodo(
    todoId: string,
    input: PatchTodoInput,
  ): Promise<BackendClientResult<Todo>> {
    return this.requestJson<Todo>(`/todos/${encodeURIComponent(todoId)}`, {
      method: "PATCH",
      headers: {
        "content-type": "application/json",
      },
      body: JSON.stringify(input),
    });
  }

  private async getJson<TResponse>(path: string): Promise<BackendClientResult<TResponse>> {
    return this.requestJson<TResponse>(path, {
      method: "GET",
    });
  }

  private async postJson<TRequest, TResponse>(
    path: string,
    body: TRequest,
  ): Promise<BackendClientResult<TResponse>> {
    return this.requestJson<TResponse>(path, {
      method: "POST",
      headers: {
        "content-type": "application/json",
      },
      body: JSON.stringify(body),
    });
  }

  private async requestJson<TResponse>(
    path: string,
    init: RequestInit,
  ): Promise<BackendClientResult<TResponse>> {
    const url = new URL(path, ensureTrailingSlash(this.getBackendUrl()));
    let lastError = "Unknown backend error";

    for (let attempt = 0; attempt <= this.retryCount; attempt += 1) {
      try {
        const response = await fetch(url, init);
        if (!response.ok) {
          const detail = await readErrorDetail(response);
          const error = `Backend returned HTTP ${response.status}${detail ? `: ${detail}` : ""}`;
          if (!isRetriableStatus(response.status) || attempt === this.retryCount) {
            return {
              ok: false,
              error,
            };
          }
          lastError = error;
          await delay(retryDelayMs(attempt));
          continue;
        }

        const data = (await response.json()) as TResponse;
        return {
          ok: true,
          data,
        };
      } catch (error) {
        lastError = error instanceof Error ? error.message : "Unknown backend error";
        if (attempt === this.retryCount) {
          return {
            ok: false,
            error: lastError,
          };
        }
        await delay(retryDelayMs(attempt));
      }
    }

    return {
      ok: false,
      error: lastError,
    };
  }
}

function ensureTrailingSlash(value: string): string {
  return value.endsWith("/") ? value : `${value}/`;
}

function isRetriableStatus(status: number): boolean {
  return status === 408 || status === 429 || status >= 500;
}

function retryDelayMs(attempt: number): number {
  return 100 * 2 ** attempt;
}

async function delay(milliseconds: number): Promise<void> {
  await new Promise((resolve) => {
    setTimeout(resolve, milliseconds);
  });
}

async function readErrorDetail(response: Response): Promise<string> {
  try {
    const contentType = response.headers.get("content-type") ?? "";
    if (contentType.includes("application/json")) {
      const body = (await response.json()) as { readonly detail?: unknown };
      return typeof body.detail === "string" ? body.detail : "";
    }
    return await response.text();
  } catch {
    return "";
  }
}
