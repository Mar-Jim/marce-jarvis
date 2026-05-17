import type { CreateTodoInput, Todo, TodoStatus } from "../domain/todos";
import type { BackendClient, BackendClientResult } from "../infrastructure/backendClient";

export class TodoService {
  public constructor(private readonly backendClient: BackendClient) {}

  public async listTodos(): Promise<BackendClientResult<readonly Todo[]>> {
    return this.backendClient.listTodos();
  }

  public async createTodo(input: CreateTodoInput): Promise<BackendClientResult<Todo>> {
    return this.backendClient.createTodo(input);
  }

  public async updateStatus(
    todoId: string,
    status: TodoStatus,
  ): Promise<BackendClientResult<Todo>> {
    return this.backendClient.patchTodo(todoId, { status });
  }
}
