import unittest
from pathlib import Path

from program import parse_config


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_CONTEXT = "1000000"


class ContextWindowContractTest(unittest.TestCase):
    def test_vllm_deployment_contract_uses_1m(self):
        config = parse_config(ROOT / "config.yaml")
        self.assertEqual(config["env"]["MAX_MODEL_LEN"], EXPECTED_CONTEXT)
        self.assertEqual(config["env"]["MODEL_ID"], "RadixArk/Qwen3.8-Flash-Next-NVFP4")
        self.assertEqual(config["common"]["model"], "/opt/models/RadixArk/Qwen3.8-Flash-Next-NVFP4")
        self.assertEqual(config["env"]["MODEL_PATH"], "/opt/models/RadixArk/Qwen3.8-Flash-Next-NVFP4")
        self.assertEqual(config["env"]["MODEL_ROOT"], "/opt/models")
        self.assertEqual(config["env"]["CONTAINER_MODEL_ROOT"], "/models")
        self.assertEqual(config["env"]["WORKER_SSH"], "chan@192.168.2.161")
        self.assertEqual(config["env"]["IMAGE"], "vllm/vllm-openai:qwen38-flash-next")

        start_script = (ROOT / "dspark/start.sh").read_text(encoding="utf-8")
        self.assertIn("--max-model-len", start_script)
        self.assertIn('"--reasoning-parser" "qwen3"', start_script)
        self.assertIn('"--tool-call-parser" "qwen3_coder"', start_script)
        self.assertIn("CONTAINER_MODEL_ROOT", start_script)
        self.assertNotIn('MODEL_CONTAINER_PATH="/models/', start_script)

        env_example = (ROOT / "dspark/.env.sample").read_text(encoding="utf-8")
        self.assertRegex(env_example, r"(?m)^MAX_MODEL_LEN=1000000")
        self.assertRegex(env_example, r"(?m)^IMAGE=\"vllm/vllm-openai:qwen38-flash-next\"")

        readme = (ROOT / "dspark/README.md").read_text(encoding="utf-8")
        self.assertIn("MAX_MODEL_LEN=1000000", readme)


if __name__ == "__main__":
    unittest.main()
