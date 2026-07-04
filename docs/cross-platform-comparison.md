# Cross-Platform Adapter Comparison

This comparison explains the platform-specific adapter work for OpenClaw,
Hermes, and Dify. The target architecture keeps memory behavior in `TdaiCore`
and limits each adapter to host integration concerns.

The core differences are session management, LLM invocation, and tool registration.

| Dimension | OpenClaw | Hermes | Dify |
| --- | --- | --- | --- |
| Adapter shape | Native OpenClaw plugin hooks in `index.ts` and `src/adapters/openclaw`. | Python provider plus Gateway sidecar under `hermes-plugin/memory/memory_tencentdb`. | Dify tool plugin under `dify-plugin-tdai-memory`. |
| Session management | Uses OpenClaw session context and host lifecycle hooks. | Uses Hermes conversation/session identifiers and forwards them to Gateway routes. | Uses Dify `conversation_id` as `session_key`; workflow authors must pass it to recall, capture, and session end. |
| LLM invocation | Can use OpenClaw host LLM APIs through the OpenClaw adapter. | Uses standalone Gateway/Hermes path with OpenAI-compatible configuration from environment or Gateway config. | Does not call an LLM. Dify owns the LLM node; the plugin only returns recalled context. |
| Tool registration | Registered through `openclaw.plugin.json` and OpenClaw extension loading. | Registered as a Hermes memory provider module. | Registered through Dify `manifest.yaml`, provider YAML, and tool YAML files. |
| Recall injection | Hook injects memory before prompt construction. | Provider/Gateway path supplies recall context to Hermes. | Workflow explicitly calls `tdai_recall` before the LLM node and injects returned `context`. |
| Capture timing | Hook captures completed turns from OpenClaw runtime events. | Provider sends completed conversation turns to Gateway. | Workflow explicitly calls `tdai_capture` after the assistant response exists. |
| Gateway lifecycle | OpenClaw can manage plugin/gateway lifecycle through host integration. | Hermes can auto-start or connect to a sidecar Gateway. | Dify plugin does not start Gateway; operator starts Gateway separately or uses the quickstart mock harness. |
| Auth | Host/plugin configuration plus optional Gateway Bearer auth. | `MEMORY_TENCENTDB_GATEWAY_API_KEY` or `TDAI_GATEWAY_API_KEY` for client-side Bearer auth. | Provider credential `gateway_api_key`; remote plain HTTP with API key is rejected by the adapter. |
| Failure mode | Host hook errors should degrade without breaking the conversation. | Provider degrades when Gateway is unavailable. | Tool calls return `{ "ok": false, ... }` so Dify workflows can continue without memory. |

## Key Difference

OpenClaw and Hermes can integrate at host lifecycle points. Dify workflows are
graph-based, so the user must place recall and capture tools in the graph. This
is why the Dify adapter favors explicit tools rather than hidden hooks.
