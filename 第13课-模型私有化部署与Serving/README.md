# 第13课-模型私有化部署与Serving

**主题**：模型私有化部署与 Serving

**当堂验收**：探活通过，模型列表含 qwen2.5，JSON 约束输出 ping=ok。

**说明**：课堂讲义与本课材料同目录；课后练习使用题面指定的运行时与数据。从该文件夹启动内核。

课堂用教学 Fake 端点即可验收；可选对接本机 Ollama / vLLM 的 /v1。环境样例见 serving.env.example。

## 本课文件

| 文件 | 用途 |
|------|------|
| `chapter13_模型私有化部署与Serving_学生讲义.ipynb` | 课堂讲义：知识点、案例、即时练习、综合练习 P1 |
| `chapter13_模型私有化部署与Serving_课后练习.ipynb` | 课后练习：P1、P2 必做，P3 选做 |
| `serving.env.example` | 可选：真实 /v1 端点环境变量样例 |
| `experiment.py` | 验收脚本 |

运行验收版：

```bash
python3 experiment.py
```
