# VS Code Extension

TypeScript VS Code extension frontend for AI Work Assistant.

This package currently contains scaffolding only. It should own:

- VS Code activation.
- Webview UI.
- Command registration.
- Local agent process lifecycle.
- Typed client calls into the local Python agent.

Assistant behavior and tool execution should live in the Python agent, not in this package.
