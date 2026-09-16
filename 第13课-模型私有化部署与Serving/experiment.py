from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent_lab.health import probe  # noqa: E402


def main() -> None:
    print("=== 第13课 模型私有化部署与 Serving ===")
    report = probe()
    print("端点来源:", report.source)
    print("模型列表:", report.model_ids)
    print("JSON 约束:", report.json_ok, report.detail)
    print("探活:", report.ok, "延迟ms=", report.latency_ms)
    assert report.ok and report.json_ok
    assert "qwen2.5" in report.model_ids
    print("本课验收通过")


if __name__ == "__main__":
    main()
