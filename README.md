# AI Studio

本地创作任务与工具工作台，包含任务提交、后台执行、状态查看、取消、额度预占与结算，以及结果素材预览。

## 启动

需要 Python 3.11+，不需要安装第三方运行依赖。在仓库根目录：

```powershell
cd src
py -m ai_studio
```

macOS / Linux 将 py 替换为 python3。打开 http://127.0.0.1:8081 。端口可通过 STUDIO_PORT 环境变量调整。

## 使用

1. 选择“普通用户”，提交简约海报任务。
2. 观察 queued → running → completed 状态，以及可用、预占、已消耗额度的变化。
3. 查看卡片、下载 SVG，或在任务结束前取消以释放预占额度。
4. 选择文本工具，查看字符统计或英文大写转换结果。
5. 切换“管理员 / 专业用户”，使用另一个卡片样式，并查看所有用户任务。

图像任务消耗 2 个本地单位，工具任务消耗 1 个单位。每个用户启动时有 100 个单位，失败或取消会释放额度。

## 接口与实现

| 接口 | 用途 |
| --- | --- |
| GET /api/catalog | 当前用户可使用的模型与工具 |
| GET /api/profile | 当前用户与额度 |
| GET、POST /api/runs | 查看及创建任务 |
| GET /api/runs/{id} | 任务详情及执行事件 |
| POST /api/runs/{id}/cancel | 取消未结束任务 |
| GET /api/assets/{id} | 按任务归属读取素材 |

请求头采用 Bearer 方式传入 local-member-key 或 local-admin-key。页面身份切换只是本机体验入口，不是正式账号登录。服务仅监听 127.0.0.1，请勿作为正式鉴权系统使用。

运行实现位于 src/ai_studio/runtime.py 与 server.py，已有 providers、tools、runs、credits 等协议文件保留扩展边界。当前图像适配器是固定布局的本地 SVG 渲染器，不调用真实生图或视频模型；文本工具为本地确定性函数。没有集成 MCP、代码沙箱、持久化队列或完整 Agent。所有状态和素材保存在内存，重启后清空。

## 检查

从仓库根目录：

```powershell
cd src
py -m unittest discover -s ../tests -v
```

采用 [MIT License](LICENSE)，不包含企业代码、原始素材、账号或内部部署配置。
