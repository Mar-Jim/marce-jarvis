import * as vscode from "vscode";

import type {
  AzureDevOpsConfig,
  AzureDevOpsSyncResponse,
  AzureDevOpsUpdateResponse,
  BackendClient,
  BackendClientResult,
} from "../infrastructure/backendClient";
import type { SecretService } from "./secretService";

export class AzureDevOpsService {
  public constructor(
    private readonly backendClient: BackendClient,
    private readonly secretService: SecretService,
  ) {}

  public async syncTickets(): Promise<BackendClientResult<AzureDevOpsSyncResponse>> {
    const config = await this.getConfig();
    const pat = await this.getPat();
    if (!config.ok) {
      return failure(config.error);
    }
    if (!pat.ok) {
      return failure(pat.error);
    }
    if (!config.data || !pat.data) {
      return failure("Azure DevOps configuration is incomplete");
    }
    return this.backendClient.syncAzureDevOpsTickets(config.data, pat.data);
  }

  public async updateTicketProgress(
    workItemId: string,
    state: string,
  ): Promise<BackendClientResult<AzureDevOpsUpdateResponse>> {
    const config = await this.getConfig();
    const pat = await this.getPat();
    if (!config.ok) {
      return failure(config.error);
    }
    if (!pat.ok) {
      return failure(pat.error);
    }
    if (!config.data || !pat.data) {
      return failure("Azure DevOps configuration is incomplete");
    }
    return this.backendClient.updateAzureDevOpsTicket(
      {
        ...config.data,
        work_item_id: workItemId,
        state,
      },
      pat.data,
    );
  }

  private async getConfig(): Promise<BackendClientResult<AzureDevOpsConfig>> {
    const settings = vscode.workspace.getConfiguration("aiWorkAssistant.azureDevOps");
    let organization = settings.get<string>("organization", "").trim();
    let project = settings.get<string>("project", "").trim();

    if (!organization) {
      organization =
        (await vscode.window.showInputBox({
          prompt: "Azure DevOps organization",
          ignoreFocusOut: true,
        }))?.trim() ?? "";
    }
    if (!project) {
      project =
        (await vscode.window.showInputBox({
          prompt: "Azure DevOps project",
          ignoreFocusOut: true,
        }))?.trim() ?? "";
    }

    if (!organization || !project) {
      return {
        ok: false,
        error: "Azure DevOps organization and project are required",
      };
    }

    return {
      ok: true,
      data: {
        organization,
        project,
      },
    };
  }

  private async getPat(): Promise<BackendClientResult<string>> {
    const existing = await this.secretService.getAzureDevOpsPat();
    if (existing) {
      return {
        ok: true,
        data: existing,
      };
    }

    const token = await vscode.window.showInputBox({
      prompt: "Azure DevOps Personal Access Token",
      password: true,
      ignoreFocusOut: true,
    });
    if (!token) {
      return {
        ok: false,
        error: "Azure DevOps PAT is required",
      };
    }
    await this.secretService.storeAzureDevOpsPat(token);
    return {
      ok: true,
      data: token,
    };
  }
}

function failure<T>(error: string | undefined): BackendClientResult<T> {
  return {
    ok: false,
    error: error ?? "Azure DevOps operation failed",
  };
}
