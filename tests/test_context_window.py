import unittest
from pathlib import Path

from program import parse_config


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_CONTEXT = "1000000"


class ContextWindowContractTest(unittest.TestCase):
    def test_all_deployment_and_agent_surfaces_use_1m(self):
        config = parse_config(ROOT / "config.yaml")
        self.assertEqual(config["env"]["CONTEXT_LENGTH"], EXPECTED_CONTEXT)
        extra_args = config["env"].get("EXTRA_ARGS", "")
        self.assertIn("rope_scaling", extra_args)
        self.assertIn('max_position_embeddings":1000000', extra_args)

        start_script = (ROOT / "dspark/start.sh").read_text(encoding="utf-8")
        self.assertRegex(start_script, r'CONTEXT_LENGTH="\$\{CONTEXT_LENGTH:-262144\}"')

        env_example = (ROOT / "dspark/.env.example").read_text(encoding="utf-8")
        self.assertRegex(env_example, r"(?m)^CONTEXT_LENGTH=1000000$")

        agent_example = (ROOT / "dspark/README.md").read_text(encoding="utf-8")
        self.assertRegex(agent_example, r'"contextWindow": 1000000,')
        self.assertNotRegex(agent_example, r'"contextWindow": (?:900000|100000),')


if __name__ == "__main__":
    unittest.main()
