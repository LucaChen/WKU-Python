from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent_lab.mcp import MCPClient  # noqa: E402
from agent_lab.tools import inventory_tool  # noqa: E402


def main() -> None:
    print("=== 第17课 自定义 Tool 与 MCP 接入（任务二 2.1+2.2 / 15分） ===")
    schema = inventory_tool.export_function_schema()
    print("Function Calling Schema:", json.dumps(schema["function"]["name"]), list(schema["function"]["parameters"]["properties"]))
    good = inventory_tool.run(sku="WIDGET-X")
    print("正常调用:", good)
    isolated = inventory_tool.run(sku="x")
    print("参数隔离:", isolated.ok, isolated.error)
    unknown = inventory_tool.run(sku="UNKNOWN-SKU")
    print("业务隔离:", unknown.ok, unknown.error)
    assert good.ok and good.stock == 12
    assert isolated.ok is False
    hs = MCPClient(transport="stdio").handshake()
    print("MCP 握手:", hs.ok, hs.protocol, hs.server)
    print("Tools:", [t.name for t in hs.tools])
    print("Resources:", [r.uri for r in hs.resources])
    assert hs.ok and len(hs.tools) >= 2 and len(hs.resources) >= 2
    print("本课验收通过")


if __name__ == "__main__":
    main()
