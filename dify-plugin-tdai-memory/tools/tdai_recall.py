from __future__ import annotations

from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.base import TdaiToolMixin, build_error_payload, truncate_text


class TdaiRecallTool(TdaiToolMixin, Tool):
    """Recall memory context before a Dify LLM node runs."""

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            result = self._client().recall(
                self._text(tool_parameters, "query"),
                self._text(tool_parameters, "session_key"),
                user_id=self._text(tool_parameters, "user_id"),
            )
            raw_context = result.get("context")
            context = truncate_text(
                str(raw_context) if raw_context is not None else "",
                self._max_chars(tool_parameters),
            )
            payload: dict[str, Any] = {"ok": True, "context": context}
            if "strategy" in result:
                payload["strategy"] = result["strategy"]
            if "memory_count" in result:
                payload["memory_count"] = result["memory_count"]
            yield self.create_json_message(payload)
        except Exception as exc:
            yield self.create_json_message(build_error_payload("recall", exc))
