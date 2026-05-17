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
        --input: var(--vscode-input-background);
        --input-fg: var(--vscode-input-foreground);
      }

      * {
        box-sizing: border-box;
      }

      body {
        margin: 0;
        padding: 0;
        color: var(--vscode-foreground);
        background: var(--vscode-sideBar-background);
        font-family: var(--vscode-font-family);
        font-size: var(--vscode-font-size);
      }

      .app {
        display: grid;
        grid-template-rows: auto 1fr auto;
        height: 100vh;
        min-width: 0;
      }

      .header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 8px;
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

      .messages {
        display: flex;
        flex-direction: column;
        gap: 10px;
        min-height: 0;
        overflow-y: auto;
        padding: 12px;
      }

      .message {
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 9px 10px;
        line-height: 1.45;
        word-break: break-word;
      }

      .message.user {
        background: var(--vscode-inputOption-activeBackground);
      }

      .message.assistant,
      .message.system {
        background: var(--vscode-editorWidget-background);
      }

      .role {
        display: block;
        margin-bottom: 4px;
        color: var(--muted);
        font-size: 11px;
        text-transform: uppercase;
      }

      .composer {
        display: grid;
        grid-template-columns: 1fr auto;
        gap: 8px;
        padding: 10px 12px;
        border-top: 1px solid var(--border);
      }

      textarea {
        width: 100%;
        min-height: 38px;
        max-height: 120px;
        resize: vertical;
        border: 1px solid var(--vscode-input-border, transparent);
        border-radius: 4px;
        padding: 8px;
        color: var(--input-fg);
        background: var(--input);
        font-family: inherit;
      }

      button {
        align-self: end;
        min-height: 32px;
        border: 0;
        border-radius: 4px;
        padding: 0 12px;
        color: var(--button-fg);
        background: var(--button);
        cursor: pointer;
      }

      button:disabled {
        cursor: not-allowed;
        opacity: 0.65;
      }
    </style>
  </head>
  <body>
    <main class="app">
      <header class="header">
        <div class="title">AI Work Assistant</div>
        <div id="status" class="status"></div>
      </header>
      <section id="messages" class="messages" aria-live="polite"></section>
      <form id="composer" class="composer">
        <textarea id="messageInput" placeholder="Ask about your work..." rows="2"></textarea>
        <button id="sendButton" type="submit">Send</button>
      </form>
    </main>
    <script nonce="${nonce}">
      const vscode = acquireVsCodeApi();
      let state = ${serializedState};

      const statusEl = document.getElementById("status");
      const messagesEl = document.getElementById("messages");
      const formEl = document.getElementById("composer");
      const inputEl = document.getElementById("messageInput");
      const sendButtonEl = document.getElementById("sendButton");

      function render(nextState) {
        state = nextState;
        vscode.setState(state);
        statusEl.textContent = state.backend.detail;
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
        messagesEl.scrollTop = messagesEl.scrollHeight;
      }

      formEl.addEventListener("submit", (event) => {
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
