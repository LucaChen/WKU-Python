from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class MCPToolMeta(BaseModel):
    name: str
    description: str
    protocol: str


class MCPResourceMeta(BaseModel):
    uri: str
    name: str
    mime_type: str


class MCPHandshake(BaseModel):
    ok: bool
    protocol: str
    server: str
    tools: List[MCPToolMeta]
    resources: List[MCPResourceMeta]


class LocalMCPServer:
    """进程内 MCP Server：演示握手与能力发现，不依赖外部进程。"""

    name = "lab-mcp"
    protocol = "stdio"

    def list_tools(self) -> List[MCPToolMeta]:
        return [
            MCPToolMeta(name="kb_lookup", description="按关键字读取知识库片段", protocol=self.protocol),
            MCPToolMeta(name="echo_time", description="返回服务器逻辑时钟", protocol=self.protocol),
        ]

    def list_resources(self) -> List[MCPResourceMeta]:
        return [
            MCPResourceMeta(uri="kb://manual", name="产品手册", mime_type="text/markdown"),
            MCPResourceMeta(uri="kb://policy", name="售后政策", mime_type="text/markdown"),
        ]


class MCPClient:
    def __init__(self, transport: str = "stdio", server: Optional[LocalMCPServer] = None):
        self.transport = transport
        self.server = server or LocalMCPServer()

    def handshake(self) -> MCPHandshake:
        tools = self.server.list_tools()
        resources = self.server.list_resources()
        return MCPHandshake(
            ok=True,
            protocol=self.transport,
            server=self.server.name,
            tools=tools,
            resources=resources,
        )

    def metadata(self) -> Dict[str, Any]:
        hs = self.handshake()
        return hs.model_dump()
