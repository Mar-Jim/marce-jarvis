import * as vscode from "vscode";

import type {
  BackendClient,
  BackendClientResult,
  OutlookDraftResponse,
  OutlookSyncResponse,
} from "../infrastructure/backendClient";
import type { SecretService } from "./secretService";

export class OutlookService {
  public constructor(
    private readonly backendClient: BackendClient,
    private readonly secretService: SecretService,
  ) {}

  public async syncUnreadEmails(): Promise<BackendClientResult<OutlookSyncResponse>> {
    const token = await this.getGraphToken();
    if (!token.ok || !token.data) {
      return failure(token.error);
    }
    return this.backendClient.syncOutlookEmails(token.data);
  }

  public async createDraftResponse(
    messageId: string,
    comment: string,
  ): Promise<BackendClientResult<OutlookDraftResponse>> {
    const token = await this.getGraphToken();
    if (!token.ok || !token.data) {
      return failure(token.error);
    }

    const approval = await vscode.window.showWarningMessage(
      "Create an Outlook draft response? This will create a draft only and will not send email.",
      { modal: true },
      "Create Draft",
    );
    if (approval !== "Create Draft") {
      return failure("Draft response was not approved");
    }

    return this.backendClient.createOutlookDraftResponse(
      {
        message_id: messageId,
        comment,
      },
      token.data,
      true,
    );
  }

  private async getGraphToken(): Promise<BackendClientResult<string>> {
    const existing = await this.secretService.getMicrosoftGraphToken();
    if (existing) {
      return {
        ok: true,
        data: existing,
      };
    }

    const token = await vscode.window.showInputBox({
      prompt: "Microsoft Graph access token with Mail.ReadWrite permissions",
      password: true,
      ignoreFocusOut: true,
    });
    if (!token) {
      return failure("Microsoft Graph access token is required");
    }
    await this.secretService.storeMicrosoftGraphToken(token);
    return {
      ok: true,
      data: token,
    };
  }
}

function failure<T>(error: string | undefined): BackendClientResult<T> {
  return {
    ok: false,
    error: error ?? "Outlook operation failed",
  };
}
