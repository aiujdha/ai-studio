# AI Studio

面向图像 / 视频创作与 Agent 工具编排的 **Python 架构展示骨架**，用于说明模块划分和接口边界。

> 本仓库只有类型、协议接口与入口占位，不生成图片或视频，不运行 Agent、工具或沙箱；不包含企业源码、素材、账号与部署配置。

## 架构

```text
创作页面 / Agent 入口（预留）
             |
             v
       访问权限与额度
             |
             v
       Run 任务生命周期
             |
       +-----+-----+
       |           |
   模型 Provider  工具接口
       |           |
       +-----+-----+
             |
       结果资产与来源记录
```

## 目录与能力对应

| 文件 / 目录 | 展示内容 | 当前状态 |
| --- | --- | --- |
| `src/ai_studio/__main__.py` | 程序入口 | 输出说明，不启动服务 |
| `src/ai_studio/providers.py` | 图像 / 视频模型统一适配 | 类型与接口占位 |
| `src/ai_studio/tools.py` | 工具描述、发现与执行边界 | 类型与接口占位 |
| `src/ai_studio/runs.py` | 排队、运行、审批、取消与恢复状态 | 类型与接口占位 |
| `src/ai_studio/permissions.py` | 管理员角色、用户类型、模块授权 | 类型与接口占位 |
| `src/ai_studio/credits.py` | 额度预占、结算与释放 | 接口占位 |
| `src/ai_studio/assets.py` | 结果资产与任务来源关联 | 类型与接口占位 |
| `web/` | 创作与管理界面边界 | 目录说明 |
| `deploy/` | API / Worker / Runner 边界 | 目录说明 |

这里只展示与简历能力主题对应的设计位置，不包含真实模型适配器、MCP 服务、任务队列、权限校验、数据库或计费实现；也不表示已完成完整平台的模型与工具接入规模。

## 技术定位

- 骨架使用 Python 3.11+ 标准库，不需要安装依赖。
- 后续 API 层可使用 FastAPI，前端可使用 Vue 3 / TypeScript。
- SQLAlchemy、MySQL、Redis/arq、MinIO、MCP 与 Docker/gVisor 属于扩展边界，当前没有集成。

## 查看入口

```bash
cd src
python -m ai_studio
```

命令仅打印说明后退出，不发起网络请求、不需要 API Key，也不产生模型费用。

## 许可

本仓库为独立编写的通用架构骨架，不代表任何企业的正式产品，采用 [MIT License](LICENSE)。
