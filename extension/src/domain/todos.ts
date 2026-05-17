export type TodoStatus = "pending" | "in_progress" | "done" | "canceled";
export type TodoPriority = "low" | "medium" | "high" | "urgent";

export interface Todo {
  readonly id: string;
  readonly title: string;
  readonly description: string;
  readonly status: TodoStatus;
  readonly priority: TodoPriority;
  readonly source: string;
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
