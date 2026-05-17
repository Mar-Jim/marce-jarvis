import * as crypto from "node:crypto";
import type * as vscode from "vscode";

import type { ChatMessage, DashboardState } from "../domain/chat";
import type { BackendClient } from "../infrastructure/backendClient";
import { renderDashboardHtml } from "./dashboardHtml";

type WebviewInboundMessage =
  | {
      readonly type: "ready";
    }
  | {
      readonly type: "sendMessage";
      readonly text: string;
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
  };

  public constructor(
    private readonly extensionUri: vscode.Uri,
    private readonly backendClient: BackendClient,
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
    await this.appendUserMessage("Plan my day");
    await this.appendAssistantMessage(
      "Planning workflows are not implemented yet. This command is wired for future local backend orchestration.",
    );
  }

  private async handleMessage(message: WebviewInboundMessage): Promise<void> {
    switch (message.type) {
      case "ready":
        await this.refreshBackendStatus();
        break;
      case "sendMessage":
        await this.appendUserMessage(message.text);
        await this.trySendToBackend(message.text);
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
