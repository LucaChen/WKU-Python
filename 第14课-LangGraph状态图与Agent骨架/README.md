# 第14课-LangGraph状态图与Agent骨架

**主题**：LangGraph 状态图与 Agent 骨架

**当堂验收**：条件边走出 agent→tool→finalize；Checkpointer 累积 messages；recursion_limit 触发熔断。

**说明**：课堂讲义与本课材料同目录；课后练习使用题面指定的运行时与数据。从该文件夹启动内核。

教学 StateGraph 在 agent_lab.graph，接口对齐 LangGraph 的 Node / Edge / 条件边。

## 本课文件

| 文件 | 用途 |
|------|------|
| `chapter14_LangGraph状态图_学生讲义.ipynb` | 课堂讲义：知识点、案例、即时练习、综合练习 P1 |
| `chapter14_LangGraph状态图_课后练习.ipynb` | 课后练习：P1、P2 必做，P3 选做 |
| `experiment.py` | 验收脚本 |

运行验收版：

```bash
python3 experiment.py
```
