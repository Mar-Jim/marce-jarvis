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

export class BackendClient {
  public constructor(private readonly getBackendUrl: BackendUrlProvider) {}

  public async health(): Promise<BackendClientResult<HealthResponse>> {
    return this.getJson<HealthResponse>("/health");
  }

  public async sendChatTurn(message: string): Promise<BackendClientResult<ChatTurnResponse>> {
    return this.postJson<ChatTurnRequest, ChatTurnResponse>("/api/v1/chat/turn", {
      message,
      source: "vscode",
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

    try {
      const response = await fetch(url, init);
      if (!response.ok) {
        return {
          ok: false,
          error: `Backend returned HTTP ${response.status}`,
        };
      }

      const data = (await response.json()) as TResponse;
      return {
        ok: true,
        data,
      };
    } catch (error) {
      return {
        ok: false,
        error: error instanceof Error ? error.message : "Unknown backend error",
      };
    }
  }
}

function ensureTrailingSlash(value: string): string {
  return value.endsWith("/") ? value : `${value}/`;
}
