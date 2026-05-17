import type { DashboardState } from "../domain/chat";

export function renderDashboardHtml(nonce: string, initialState: DashboardState): string {
  const serializedState = JSON.stringify(initialState).replace(/</g, "\\u003c");

  return /* html */ `<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta
      http-equiv="Content-Security-Policy"
      content="default-src 'none'; img-src data:; style-src 'unsafe-inline'; script-src 'nonce-${nonce}';"
    />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>AI Work Assistant</title>
    <style>
      :root {
        color-scheme: light dark;
        --border: var(--vscode-panel-border);
        --muted: var(--vscode-descriptionForeground);
        --button: var(--vscode-button-background);
        --button-fg: var(--vscode-button-foreground);
        --secondary-button: var(--vscode-button-secondaryBackground);
        --secondary-button-fg: var(--vscode-button-secondaryForeground);
        --input: var(--vscode-input-background);
        --input-fg: var(--vscode-input-foreground);
        --danger: var(--vscode-errorForeground);
      }

      * {
        box-sizing: border-box;
      }

      body {
        margin: 0;
        color: var(--vscode-foreground);
        background: var(--vscode-sideBar-background);
        font-family: var(--vscode-font-family);
        font-size: var(--vscode-font-size);
      }

      .app {
        display: grid;
        grid-template-rows: auto 1fr;
        height: 100vh;
        min-width: 0;
      }

      .header,
      .section-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 8px;
      }

      .header {
        padding: 10px 12px;
        border-bottom: 1px solid var(--border);
      }

      .title {
        font-weight: 600;
      }

      .status {
        min-width: 0;
        color: var(--muted);
        font-size: 12px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .content {
        min-height: 0;
        overflow-y: auto;
        padding: 12px;
      }

      .section {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin-bottom: 18px;
      }

      .section-title {
        margin: 0;
        font-size: 13px;
        font-weight: 600;
      }

      .todo-form {
        display: grid;
        grid-template-columns: 1fr;
        gap: 8px;
      }

      .row {
        display: grid;
        grid-template-columns: 1fr auto;
        gap: 8px;
      }

      input,
      textarea,
      select {
        width: 100%;
        min-width: 0;
        border: 1px solid var(--vscode-input-border, transparent);
        border-radius: 4px;
        padding: 7px 8px;
        color: var(--input-fg);
        background: var(--input);
        font-family: inherit;
        font-size: inherit;
      }

      textarea {
        min-height: 56px;
        resize: vertical;
      }

      button {
        min-height: 30px;
        border: 0;
        border-radius: 4px;
        padding: 0 10px;
        color: var(--button-fg);
        background: var(--button);
        cursor: pointer;
        white-space: nowrap;
      }

      button.secondary {
        color: var(--secondary-button-fg);
        background: var(--secondary-button);
      }

      button:disabled,
      select:disabled,
      input:disabled,
      textarea:disabled {
        cursor: not-allowed;
        opacity: 0.65;
      }

      .todo-list {
        display: flex;
        flex-direction: column;
        gap: 8px;
      }

      .todo {
        display: flex;
        flex-direction: column;
        gap: 7px;
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 9px 10px;
        background: var(--vscode-editorWidget-background);
      }

      .todo-title {
        font-weight: 600;
        line-height: 1.35;
        word-break: break-word;
      }

      .todo-description,
      .empty,
      .meta {
        color: var(--muted);
        line-height: 1.4;
      }

      .meta {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 8px;
        font-size: 12px;
      }

      .error {
        border: 1px solid var(--danger);
        border-radius: 6px;
        padding: 8px;
        color: var(--danger);
      }

      .messages {
        display: flex;
        flex-direction: column;
        gap: 8px;
      }

      .message {
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 8px;
        line-height: 1.45;
        word-break: break-word;
      }

      .role {
        display: block;
        margin-bottom: 4px;
        color: var(--muted);
        font-size: 11px;
        text-transform: uppercase;
      }

      .chat-form {
        display: grid;
        grid-template-columns: 1fr auto;
        gap: 8px;
      }
    </style>
  </head>
  <body>
    <main class="app">
      <header class="header">
        <div class="title">AI Work Assistant</div>
        <div id="status" class="status"></div>
      </header>
      <div class="content">
        <section class="section">
          <div class="section-header">
            <h2 class="section-title">Todos</h2>
            <button id="refreshTodosButton" class="secondary" type="button">Refresh</button>
          </div>
          <form id="todoForm" class="todo-form">
            <input id="todoTitleInput" type="text" maxlength="200" placeholder="New todo title" />
            <textarea
              id="todoDescriptionInput"
              maxlength="4000"
              placeholder="Description"
            ></textarea>
            <div class="row">
              <select id="todoPriorityInput" aria-label="Priority">
                <option value="low">Low</option>
                <option value="medium" selected>Medium</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
              <button id="createTodoButton" type="submit">Add</button>
            </div>
          </form>
          <div id="todoError" class="error" hidden></div>
          <div id="todoLoading" class="empty" hidden>Loading todos...</div>
          <div id="todoList" class="todo-list"></div>
        </section>

        <section class="section">
          <h2 class="section-title">Chat</h2>
          <div id="messages" class="messages" aria-live="polite"></div>
          <form id="chatForm" class="chat-form">
            <input id="messageInput" type="text" placeholder="Ask about your work..." />
            <button id="sendButton" type="submit">Send</button>
          </form>
        </section>
      </div>
    </main>
    <script nonce="${nonce}">
      const vscode = acquireVsCodeApi();
      let state = ${serializedState};

      const statusEl = document.getElementById("status");
      const messagesEl = document.getElementById("messages");
      const chatFormEl = document.getElementById("chatForm");
      const inputEl = document.getElementById("messageInput");
      const sendButtonEl = document.getElementById("sendButton");

      const todoFormEl = document.getElementById("todoForm");
      const todoTitleInputEl = document.getElementById("todoTitleInput");
      const todoDescriptionInputEl = document.getElementById("todoDescriptionInput");
      const todoPriorityInputEl = document.getElementById("todoPriorityInput");
      const createTodoButtonEl = document.getElementById("createTodoButton");
      const refreshTodosButtonEl = document.getElementById("refreshTodosButton");
      const todoErrorEl = document.getElementById("todoError");
      const todoLoadingEl = document.getElementById("todoLoading");
      const todoListEl = document.getElementById("todoList");

      function render(nextState) {
        state = nextState;
        vscode.setState(state);
        statusEl.textContent = state.backend.detail;
        renderTodos();
        renderMessages();
      }

      function renderTodos() {
        const todos = state.todos;
        todoLoadingEl.hidden = !todos.isLoading;
        todoErrorEl.hidden = !todos.error;
        todoErrorEl.textContent = todos.error || "";
        createTodoButtonEl.disabled = todos.isSaving;
        refreshTodosButtonEl.disabled = todos.isLoading || todos.isSaving;
        todoTitleInputEl.disabled = todos.isSaving;
        todoDescriptionInputEl.disabled = todos.isSaving;
        todoPriorityInputEl.disabled = todos.isSaving;

        if (!todos.isLoading && todos.items.length === 0) {
          const empty = document.createElement("div");
          empty.className = "empty";
          empty.textContent = "No todos yet.";
          todoListEl.replaceChildren(empty);
          return;
        }

        todoListEl.replaceChildren(
          ...todos.items.map((todo) => {
            const item = document.createElement("article");
            item.className = "todo";

            const title = document.createElement("div");
            title.className = "todo-title";
            title.textContent = todo.title;

            const description = document.createElement("div");
            description.className = "todo-description";
            description.textContent = todo.description || "No description";

            const meta = document.createElement("div");
            meta.className = "meta";

            const priority = document.createElement("span");
            priority.textContent =
              (todo.external_id ? "#" + todo.external_id + " · " : "") +
              todo.priority +
              " · " +
              todo.category.replace("_", " ");

            const status = document.createElement("select");
            status.setAttribute("aria-label", "Todo status");
            status.disabled = todos.isSaving;
            for (const optionValue of ["pending", "in_progress", "done", "canceled"]) {
              const option = document.createElement("option");
              option.value = optionValue;
              option.textContent = optionValue.replace("_", " ");
              option.selected = optionValue === todo.status;
              status.append(option);
            }
            status.addEventListener("change", () => {
              vscode.postMessage({
                type: "updateTodoStatus",
                todoId: todo.id,
                status: status.value,
              });
            });

            meta.append(priority, status);
            item.append(title, description, meta);
            return item;
          }),
        );
      }

      function renderMessages() {
        messagesEl.replaceChildren(
          ...state.messages.map((message) => {
            const item = document.createElement("article");
            item.className = "message " + message.role;

            const role = document.createElement("strong");
            role.className = "role";
            role.textContent = message.role;

            const content = document.createElement("div");
            content.textContent = message.content;

            item.append(role, content);
            return item;
          }),
        );
      }

      todoFormEl.addEventListener("submit", (event) => {
        event.preventDefault();
        const title = todoTitleInputEl.value.trim();
        if (!title) {
          return;
        }

        vscode.postMessage({
          type: "createTodo",
          input: {
            title,
            description: todoDescriptionInputEl.value.trim(),
            priority: todoPriorityInputEl.value,
            source: "vscode",
          },
        });
        todoTitleInputEl.value = "";
        todoDescriptionInputEl.value = "";
        todoPriorityInputEl.value = "medium";
      });

      refreshTodosButtonEl.addEventListener("click", () => {
        vscode.postMessage({ type: "refreshTodos" });
      });

      chatFormEl.addEventListener("submit", (event) => {
        event.preventDefault();
        const text = inputEl.value.trim();
        if (!text) {
          return;
        }

        inputEl.value = "";
        sendButtonEl.disabled = true;
        vscode.postMessage({ type: "sendMessage", text });
      });

      window.addEventListener("message", (event) => {
        const message = event.data;
        if (message.type === "stateChanged") {
          sendButtonEl.disabled = false;
          render(message.state);
        }
      });

      render(state);
      vscode.postMessage({ type: "ready" });
    </script>
  </body>
</html>`;
}
