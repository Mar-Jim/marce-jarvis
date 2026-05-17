export type TodoStatus = "pending" | "in_progress" | "done" | "canceled";
export type TodoPriority = "low" | "medium" | "high" | "urgent";

export interface Todo {
  readonly id: string;
  readonly title: string;
  readonly description: string;
  readonly status: TodoStatus;
  readonly priority: TodoPriority;
  readonly source: string;
  readonly external_provider: string | null;
  readonly external_id: string | null;
  readonly external_url: string | null;
  readonly category:
    | "blocked"
    | "in_progress"
    | "urgent"
    | "due_soon"
    | "pipeline_failure"
    | "needs_response"
    | "needs_action"
    | "informational"
    | "meeting_context"
    | "normal";
  readonly created_at: string;
  readonly updated_at: string;
}

export interface CreateTodoInput {
  readonly title: string;
  readonly description: string;
  readonly priority: TodoPriority;
  readonly source: string;
}

export interface PatchTodoInput {
  readonly status?: TodoStatus;
}

export interface TodosState {
  readonly items: readonly Todo[];
  readonly isLoading: boolean;
  readonly isSaving: boolean;
  readonly error: string | undefined;
}
