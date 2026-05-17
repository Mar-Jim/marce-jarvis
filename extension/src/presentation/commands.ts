import * as vscode from "vscode";

import { AssistantDashboardProvider } from "./dashboardProvider";

export function registerAssistantCommands(
  dashboardProvider: AssistantDashboardProvider,
): vscode.Disposable[] {
  return [
    vscode.commands.registerCommand("assistant.openDashboard", async () => {
      await vscode.commands.executeCommand(`${AssistantDashboardProvider.viewType}.focus`);
    }),
    vscode.commands.registerCommand("assistant.syncDevOpsTickets", async () => {
      await vscode.commands.executeCommand(`${AssistantDashboardProvider.viewType}.focus`);
      await dashboardProvider.syncDevOpsTickets();
    }),
    vscode.commands.registerCommand("assistant.updateCurrentTicket", async () => {
      await vscode.commands.executeCommand(`${AssistantDashboardProvider.viewType}.focus`);
      await dashboardProvider.updateCurrentTicket();
    }),
    vscode.commands.registerCommand("assistant.planMyDay", async () => {
      await vscode.commands.executeCommand(`${AssistantDashboardProvider.viewType}.focus`);
      await dashboardProvider.planMyDay();
    }),
  ];
}
