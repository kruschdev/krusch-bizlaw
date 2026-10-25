import unittest
from unittest.mock import MagicMock
from src.backend.main import _safe_check_health


class TestHealthResilience(unittest.TestCase):
    def test_safe_check_health_handles_downstream_failure(self):
        # BUG-01: _safe_check_health returns "unreachable" when client.check_health raises
        healthy_client = MagicMock()
        healthy_client.check_health.return_value = {"status": "healthy"}
        self.assertEqual(
            _safe_check_health(healthy_client, "biz_client"), {"status": "healthy"}
        )

        failing_client = MagicMock()
        failing_client.check_health.side_effect = RuntimeError("connection refused")
        self.assertEqual(
            _safe_check_health(failing_client, "law_client"), "unreachable"
        )


if __name__ == "__main__":
    unittest.main()
