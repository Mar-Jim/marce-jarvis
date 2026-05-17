# VS Code Extension

TypeScript VS Code extension frontend for AI Work Assistant.

This package currently contains scaffolding only. It should own:

- VS Code activation.
- Webview UI.
- Command registration.
- Local agent process lifecycle.
- Typed client calls into the local Python agent.

Assistant behavior and tool execution should live in the Python agent, not in this package.

## Current Extension Surface

- Activity bar container: `AI Work Assistant`
- Sidebar webview: `AI Work Assistant`
- Command palette:
  - `Assistant: Open Dashboard`
  - `Assistant: Plan My Day`
- Local backend setting: `aiWorkAssistant.backendUrl`

The chat UI is intentionally non-AI for now. It sends typed REST requests to the configured localhost backend and shows placeholder responses until backend orchestration exists.

## Development

```bash
corepack pnpm --filter ai-work-assistant-extension build
corepack pnpm --filter ai-work-assistant-extension test
corepack pnpm --filter ai-work-assistant-extension package
```
