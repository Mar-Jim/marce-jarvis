export type ChatRole = "user" | "assistant" | "system";

export interface ChatMessage {
  readonly id: string;
  readonly role: ChatRole;
  readonly content: string;
  readonly createdAt: string;
}

export interface DashboardState {
  readonly backend: BackendStatus;
  readonly messages: readonly ChatMessage[];
}

export interface BackendStatus {
  readonly state: "unknown" | "online" | "offline";
  readonly detail: string;
}
