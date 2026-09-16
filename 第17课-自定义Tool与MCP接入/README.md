# 第17课-自定义Tool与MCP接入

**主题**：自定义 Tool 与 MCP 接入

**当堂验收**：导出 Function Calling Schema；参数/业务异常隔离；MCP 握手读出 Tools 与 Resources。

**说明**：课堂讲义与本课材料同目录；课后练习使用题面指定的运行时与数据。从该文件夹启动内核。

Tool 失败必须返回标准化错误字段，禁止让整个程序崩溃。

## 本课文件

| 文件 | 用途 |
|------|------|
| `chapter17_自定义Tool与MCP_学生讲义.ipynb` | 课堂讲义：知识点、案例、即时练习、综合练习 P1 |
| `chapter17_自定义Tool与MCP_课后练习.ipynb` | 课后练习：P1、P2 必做，P3 选做 |
| `experiment.py` | 验收脚本 |

运行验收版：

```bash
python3 experiment.py
```
