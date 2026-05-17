# Phased Roadmap

## Phase 0: Documentation And Design

Status: current phase.

Deliverables:

- Technical architecture.
- Recommended repository structure.
- Initial scaffolding plan.
- Phased roadmap.
- Initial engineering principles and safety model.

Exit criteria:

- Documentation reviewed.
- Initial scope agreed.
- Implementation order clear.

## Phase 1: Local Development Scaffold

Goal: establish the repo, build system, and local app shell without assistant features.

Deliverables:

- VS Code extension skeleton.
- FastAPI backend skeleton.
- Health and version endpoints.
- SQLite initialization.
- Local dev commands.
- Basic CI.
- Type checking and linting.
- Backend lifecycle from extension.

Exit criteria:

- Extension launches in VS Code.
- Backend starts locally.
- Extension can call `/health`.
- Tests run locally and in CI.

## Phase 2: Contracts, Persistence, And Approval Core

Goal: build the typed foundation for assistant turns and safe tool execution.

Deliverables:

- Versioned API contracts.
- Conversation and message persistence.
- Approval request model.
- Approval decision persistence.
- Tool base interface.
- Tool registry.
- Audit log.
- Minimal webview approval UI.

Exit criteria:

- Backend can create a mock assistant turn.
- Backend can request approval for a mock tool.
- Extension can approve or deny.
- Approval decisions are persisted.

## Phase 3: Read-Only Workspace Intelligence

Goal: support safe local context gathering.

Deliverables:

- Workspace file search tool.
- File read tool with workspace boundaries.
- Python project summarization.
- SQL file discovery.
- DAB project detection.
- Conversation UI for read-only analysis.

Exit criteria:

- Assistant can answer questions about local workspace files.
- Tool calls are auditable.
- No write actions are available.

## Phase 4: Databricks Asset Bundle Support

Goal: add high-value Databricks project support while staying safe by default.

Deliverables:

- `databricks.yml` parser.
- Bundle target/resource explainer.
- Bundle validation command preview.
- Approval-gated `databricks bundle validate`.
- Deployment plan summarization.
- Draft-only bundle change suggestions.

Exit criteria:

- Assistant can explain a DAB project.
- Assistant can validate a bundle only after approval.
- Assistant does not deploy or mutate Databricks resources.

## Phase 5: Python And SQL Productivity Tools

Goal: support day-to-day analysis and engineering review.

Deliverables:

- SQL explanation and review.
- SQL refactoring suggestions.
- Python code review.
- Test suggestion workflows.
- Optional approval-gated local command execution.

Exit criteria:

- Assistant can review Python and SQL files.
- Assistant can propose changes without applying them automatically.
- Any execution or edit requires approval.

## Phase 6: Controlled Local File Edits

Goal: allow safe local modifications with clear previews.

Deliverables:

- Diff generation.
- Approval-gated file writes.
- Workspace-root enforcement.
- Revert guidance.
- Edit audit log.

Exit criteria:

- Assistant can propose file edits.
- User sees exact diff before approval.
- Approved edits are persisted to disk and audit log.

## Phase 7: Azure DevOps Integration

Goal: support enterprise delivery workflows.

Deliverables:

- Azure DevOps configuration.
- Read-only work item and PR tools.
- PR summary drafts.
- Work item update drafts.
- Approval-gated external mutations.

Exit criteria:

- Assistant can summarize Azure DevOps context.
- Mutations are impossible without explicit approval.
- Credentials are never logged.

## Phase 8: Email Drafting

Goal: improve communication workflows without unsafe sending.

Deliverables:

- Email draft templates.
- Status update drafting.
- Meeting follow-up drafting.
- Optional connector design for future mailbox access.

Exit criteria:

- Assistant can draft email content.
- Assistant cannot send email.
- Future sending path is documented as approval-gated.

## Phase 9: Packaging And Hardening

Goal: make the assistant reliable for daily use.

Deliverables:

- `.vsix` packaging.
- Backend packaging strategy.
- Settings migration.
- Database migration workflow.
- Error reporting without sensitive data.
- Performance profiling.
- Security review checklist.

Exit criteria:

- Installation is repeatable.
- Upgrade path is defined.
- Common failures have clear diagnostics.

## Phase 10: Extensibility And Internal Platform

Goal: make new tools straightforward to add and review.

Deliverables:

- Tool authoring guide.
- Tool test harness.
- Permission policy examples.
- Internal plugin conventions.
- Evaluation fixtures for assistant behavior.

Exit criteria:

- A new tool can be added with schema, tests, approval metadata, and docs.
- Tool behavior is covered by unit and policy tests.
