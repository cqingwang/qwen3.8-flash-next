import unittest
from pathlib import Path

from program import parse_config


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_CONTEXT = "100000"


class ContextWindowContractTest(unittest.TestCase):
    def test_all_deployment_and_agent_surfaces_use_100k(self):
        config = parse_config(ROOT / "config.yaml")
        self.assertEqual(config["env"]["CONTEXT_LENGTH"], EXPECTED_CONTEXT)
        self.assertEqual(
            config["env"].get("EXTRA_ARGS", ""),
            "",
            "100k is within the native 262144-token window and must not use a million-token override",
        )

        start_script = (ROOT / "dspark/start.sh").read_text(encoding="utf-8")
        self.assertRegex(start_script, r'CONTEXT_LENGTH="\$\{CONTEXT_LENGTH:-100000\}"')

        env_example = (ROOT / "dspark/.env.example").read_text(encoding="utf-8")
        self.assertRegex(env_example, r"(?m)^CONTEXT_LENGTH=100000$")

        agent_example = (ROOT / "dspark/README.md").read_text(encoding="utf-8")
        self.assertRegex(agent_example, r'"contextWindow": 100000,')
        self.assertNotRegex(agent_example, r'"contextWindow": (?:900000|1000000),')


if __name__ == "__main__":
    unittest.main()
