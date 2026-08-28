import unittest

from dspark.tool_thinking_policy import should_disable_thinking_for_tools


class ToolThinkingPolicyTest(unittest.TestCase):
    def test_disables_qwen_thinking_when_tools_are_present(self):
        self.assertTrue(
            should_disable_thinking_for_tools(
                reasoning_parser="qwen3",
                tool_call_parser="qwen3_coder",
                tools=[{"type": "function"}],
                chat_template_kwargs=None,
            )
        )

    def test_keeps_thinking_for_plain_qwen_requests(self):
        self.assertFalse(
            should_disable_thinking_for_tools(
                reasoning_parser="qwen3",
                tool_call_parser="qwen3_coder",
                tools=[],
                chat_template_kwargs=None,
            )
        )

    def test_respects_explicit_thinking_disable(self):
        self.assertFalse(
            should_disable_thinking_for_tools(
                reasoning_parser="qwen3",
                tool_call_parser="qwen3_coder",
                tools=[{"type": "function"}],
                chat_template_kwargs={"enable_thinking": False},
            )
        )

    def test_does_not_change_other_reasoning_parsers(self):
        self.assertFalse(
            should_disable_thinking_for_tools(
                reasoning_parser="deepseek_v3",
                tool_call_parser="qwen3_coder",
                tools=[{"type": "function"}],
                chat_template_kwargs=None,
            )
        )


if __name__ == "__main__":
    unittest.main()
