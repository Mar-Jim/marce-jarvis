import * as vscode from "vscode";

import { BackendClient } from "./infrastructure/backendClient";
import { registerAssistantCommands } from "./presentation/commands";
import { AssistantDashboardProvider } from "./presentation/dashboardProvider";
import { AzureDevOpsService } from "./services/azureDevOpsService";
import { OutlookService } from "./services/outlookService";
import { SecretService } from "./services/secretService";
import { TodoService } from "./services/todoService";

export function activate(context: vscode.ExtensionContext): void {
  const backendClient = new BackendClient(() => getBackendUrl());
  const secretService = new SecretService(context.secrets);
  const azureDevOpsService = new AzureDevOpsService(backendClient, secretService);
  const outlookService = new OutlookService(backendClient, secretService);
  const todoService = new TodoService(backendClient);
  const dashboardProvider = new AssistantDashboardProvider(
    context.extensionUri,
    backendClient,
    todoService,
    azureDevOpsService,
    outlookService,
  );

  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider(
      AssistantDashboardProvider.viewType,
      dashboardProvider,
      {
        webviewOptions: {
          retainContextWhenHidden: true,
        },
      },
    ),
    ...registerAssistantCommands(dashboardProvider),
  );
}

export function deactivate(): void {
  // No background resources are started by the scaffolded extension.
}

function getBackendUrl(): string {
  return vscode.workspace
    .getConfiguration("aiWorkAssistant")
    .get<string>("backendUrl", "http://127.0.0.1:8765");
}
