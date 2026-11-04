# 部署边界

本目录只保留服务划分，不提供容器编排或沙箱实现。

```text
Web -> API -> Worker -> 模型 / 工具
        |       |
        |       +----> Runner（代码执行隔离边界，预留）
        |
        +--> MySQL / Redis / MinIO（均未连接）
```

FastAPI、arq、Docker/gVisor 和 MCP 是后续接入位置，不是当前已实现能力。
