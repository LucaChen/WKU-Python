from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent_lab.openclaw import OpenClawClient, OpenClawConfig  # noqa: E402


def main() -> None:
    print("=== 第15课 OpenClaw 运行时初始化 ===")
    client = OpenClawClient(
        OpenClawConfig(timeout_s=5.0, model="qwen2.5", session_id="handshake-1", agent_runtime="openclaw")
    )
    report = client.handshake()
    print("握手:", report.ok, report.model_ids, "source=", report.source)
    assert report.ok
    result = client.run_turn("健康探活")
    print("首轮状态迁移日志:", result["state_log"])
    print("回复摘要:", str(result.get("reply"))[:80])
    assert result["state_log"]
    assert result["state_log"][0]["runtime"] == "openclaw"
    print("本课验收通过")


if __name__ == "__main__":
    main()
