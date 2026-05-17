import type * as vscode from "vscode";

const AZURE_DEVOPS_PAT_KEY = "azureDevOps.pat";

export class SecretService {
  public constructor(private readonly secretStorage: vscode.SecretStorage) {}

  public async getAzureDevOpsPat(): Promise<string | undefined> {
    return this.secretStorage.get(AZURE_DEVOPS_PAT_KEY);
  }

  public async storeAzureDevOpsPat(token: string): Promise<void> {
    await this.secretStorage.store(AZURE_DEVOPS_PAT_KEY, token);
  }
}
