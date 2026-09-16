"""Agent 实训教学运行时：无 GPU 也可完成本地验收。

真实课堂可把 OPENAI_BASE_URL 指到 Ollama / vLLM 的 /v1 端点。
未配置时使用进程内 FakeOpenAI，保证 experiment.py 可重复运行。
"""

from .health import HealthReport, probe
from .mock_openai import FakeOpenAI, get_client

__all__ = ["HealthReport", "probe", "FakeOpenAI", "get_client"]
