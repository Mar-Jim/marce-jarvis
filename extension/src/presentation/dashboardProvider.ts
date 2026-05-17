import * as crypto from "node:crypto";
import * as vscode from "vscode";

import type { ChatMessage, DashboardState } from "../domain/chat";
import type { CreateTodoInput, Todo, TodoStatus } from "../domain/todos";
import type { BackendClient } from "../infrastructure/backendClient";
import type { AzureDevOpsService } from "../services/azureDevOpsService";
import type { TodoService } from "../services/todoService";
import { renderDashboardHtml } from "./dashboardHtml";

type WebviewInboundMessage =
  | {
      readonly type: "ready";
    }
  | {
      readonly type: "sendMessage";
      readonly text: string;
    }
  | {
      readonly type: "refreshTodos";
    }
  | {
      readonly type: "createTodo";
      readonly input: CreateTodoInput;
    }
  | {
      readonly type: "updateTodoStatus";
      readonly todoId: string;
      readonly status: TodoStatus;
    };

type WebviewOutboundMessage = {
  readonly type: "stateChanged";
  readonly state: DashboardState;
};

export class AssistantDashboardProvider implements vscode.WebviewViewProvider {
  public static readonly viewType = "aiWorkAssistant.dashboard";

  private view?: vscode.WebviewView;
  private state: DashboardState = {
    backend: {
      state: "unknown",
      detail: "Backend status unknown",
    },
    messages: [
      createMessage(
        "assistant",
        "Local assistant shell is ready. AI features are not implemented yet.",
      ),
    ],
    todos: {
      items: [],
      isLoading: false,
      isSaving: false,
      error: undefined,
    },
  };

  public constructor(
    private readonly extensionUri: vscode.Uri,
    private readonly backendClient: BackendClient,
    private readonly todoService: TodoService,
    private readonly azureDevOpsService: AzureDevOpsService,
  ) {}

  public resolveWebviewView(webviewView: vscode.WebviewView): void {
    this.view = webviewView;
    webviewView.webview.options = {
      enableScripts: true,
      localResourceRoots: [this.extensionUri],
    };

    webviewView.webview.html = renderDashboardHtml(createNonce(), this.state);
    webviewView.webview.onDidReceiveMessage((message: WebviewInboundMessage) => {
      void this.handleMessage(message);
    });
  }

  public async planMyDay(): Promise<void> {
    await this.loadTodos();
    await this.appendUserMessage("Plan my day");
    const urgent = this.state.todos.items.filter((todo) => todo.category === "urgent");
    const blocked = this.state.todos.items.filter((todo) => todo.category === "blocked");
    const dueSoon = this.state.todos.items.filter((todo) => todo.category === "due_soon");
    await this.appendAssistantMessage(
      `Local plan: ${urgent.length} urgent, ${blocked.length} blocked, ${dueSoon.length} due soon.`,
    );
  }

  public async syncDevOpsTickets(): Promise<void> {
    this.state = {
      ...this.state,
      todos: {
        ...this.state.todos,
        isLoading: true,
        error: undefined,
      },
    };
    await this.postState();

    const result = await this.azureDevOpsService.syncTickets();
    if (!result.ok) {
      this.state = {
        ...this.state,
        todos: {
          ...this.state.todos,
          isLoading: false,
          error: result.error ?? "Unable to sync Azure DevOps tickets",
        },
      };
      await this.postState();
      return;
    }

    await this.loadTodos();
    await this.appendAssistantMessage(
      `Synced ${result.data?.synced_count ?? 0} Azure DevOps ticket(s).`,
    );
  }

  public async updateCurrentTicket(): Promise<void> {
    const linkedTodos = this.state.todos.items.filter(
      (todo) => todo.external_provider === "azure_devops" && todo.external_id,
    );
    if (linkedTodos.length === 0) {
      await this.loadTodos();
    }

    const refreshedLinkedTodos = this.state.todos.items.filter(
      (todo) => todo.external_provider === "azure_devops" && todo.external_id,
    );
    const selected = await vscode.window.showQuickPick(
      refreshedLinkedTodos.map((todo) => ({
        label: `${todo.external_id}: ${todo.title}`,
        description: todo.status,
        todo,
      })),
      {
        placeHolder: "Select an Azure DevOps-linked todo",
      },
    );
    if (!selected?.todo.external_id) {
      return;
    }

    const state = await vscode.window.showQuickPick(["New", "Active", "Resolved", "Closed"], {
      placeHolder: "Select Azure DevOps ticket state",
    });
    if (!state) {
      return;
    }

    const result = await this.azureDevOpsService.updateTicketProgress(
      selected.todo.external_id,
      state,
    );
    if (!result.ok) {
      this.state = {
        ...this.state,
        todos: {
          ...this.state.todos,
          error: result.error ?? "Unable to update Azure DevOps ticket",
        },
      };
      await this.postState();
      return;
    }

    await this.updateTodoStatus(selected.todo.id, mapAzureStateToTodoStatus(state));
    await this.appendAssistantMessage(`Updated Azure DevOps ticket ${selected.todo.external_id}.`);
  }

  private async handleMessage(message: WebviewInboundMessage): Promise<void> {
    switch (message.type) {
      case "ready":
        await this.refreshBackendStatus();
        await this.loadTodos();
        break;
      case "sendMessage":
        await this.appendUserMessage(message.text);
        await this.trySendToBackend(message.text);
        break;
      case "refreshTodos":
        await this.loadTodos();
        break;
      case "createTodo":
        await this.createTodo(message.input);
        break;
      case "updateTodoStatus":
        await this.updateTodoStatus(message.todoId, message.status);
        break;
    }
  }

  private async refreshBackendStatus(): Promise<void> {
    const result = await this.backendClient.health();
    this.state = {
      ...this.state,
      backend: result.ok
        ? {
            state: "online",
            detail: `Backend online${result.data?.version ? ` (${result.data.version})` : ""}`,
          }
        : {
            state: "offline",
            detail: `Backend offline: ${result.error ?? "Unable to connect"}`,
          },
    };
    await this.postState();
  }

  private async trySendToBackend(text: string): Promise<void> {
    const result = await this.backendClient.sendChatTurn(text);
    if (result.ok && result.data?.message) {
      await this.appendAssistantMessage(result.data.message);
      return;
    }

    await this.appendAssistantMessage(
      "Chat orchestration is not implemented yet. The extension is connected to the local REST client shell.",
    );
  }

  private async loadTodos(): Promise<void> {
    this.state = {
      ...this.state,
      todos: {
        ...this.state.todos,
        isLoading: true,
        error: undefined,
      },
    };
    await this.postState();

    const result = await this.todoService.listTodos();
    if (!result.ok || !result.data) {
      this.state = {
        ...this.state,
        todos: {
          ...this.state.todos,
          isLoading: false,
          error: result.error ?? "Unable to load todos",
        },
      };
      await this.postState();
      return;
    }

    this.state = {
      ...this.state,
      todos: {
        items: result.data,
        isLoading: false,
        isSaving: false,
        error: undefined,
      },
    };
    await this.postState();
  }

  private async createTodo(input: CreateTodoInput): Promise<void> {
    this.state = {
      ...this.state,
      todos: {
        ...this.state.todos,
        isSaving: true,
        error: undefined,
      },
    };
    await this.postState();

    const result = await this.todoService.createTodo(input);
    if (!result.ok || !result.data) {
      this.state = {
        ...this.state,
        todos: {
          ...this.state.todos,
          isSaving: false,
          error: result.error ?? "Unable to create todo",
        },
      };
      await this.postState();
      return;
    }

    this.state = {
      ...this.state,
      todos: {
        items: [result.data, ...this.state.todos.items],
        isLoading: false,
        isSaving: false,
        error: undefined,
      },
    };
    await this.postState();
  }

  private async updateTodoStatus(todoId: string, status: TodoStatus): Promise<void> {
    this.state = {
      ...this.state,
      todos: {
        ...this.state.todos,
        isSaving: true,
        error: undefined,
      },
    };
    await this.postState();

    const result = await this.todoService.updateStatus(todoId, status);
    if (!result.ok || !result.data) {
      this.state = {
        ...this.state,
        todos: {
          ...this.state.todos,
          isSaving: false,
          error: result.error ?? "Unable to update todo",
        },
      };
      await this.postState();
      return;
    }

    this.state = {
      ...this.state,
      todos: {
        ...this.state.todos,
        items: replaceTodo(this.state.todos.items, result.data),
        isSaving: false,
      },
    };
    await this.postState();
  }

  private async appendUserMessage(content: string): Promise<void> {
    this.state = {
      ...this.state,
      messages: [...this.state.messages, createMessage("user", content)],
    };
    await this.postState();
  }

  private async appendAssistantMessage(content: string): Promise<void> {
    this.state = {
      ...this.state,
      messages: [...this.state.messages, createMessage("assistant", content)],
    };
    await this.postState();
  }

  private async postState(): Promise<void> {
    const message: WebviewOutboundMessage = {
      type: "stateChanged",
      state: this.state,
    };
    await this.view?.webview.postMessage(message);
  }
}

function createMessage(role: ChatMessage["role"], content: string): ChatMessage {
  return {
    id: crypto.randomUUID(),
    role,
    content,
    createdAt: new Date().toISOString(),
  };
}

function createNonce(): string {
  return crypto.randomBytes(16).toString("base64");
}

function replaceTodo(todos: readonly Todo[], updatedTodo: Todo): readonly Todo[] {
  return todos.map((todo) => (todo.id === updatedTodo.id ? updatedTodo : todo));
}

function mapAzureStateToTodoStatus(state: string): TodoStatus {
  const normalized = state.toLowerCase();
  if (normalized === "active") {
    return "in_progress";
  }
  if (normalized === "resolved" || normalized === "closed") {
    return "done";
  }
  return "pending";
}
