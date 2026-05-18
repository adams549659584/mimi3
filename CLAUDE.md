# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

mimo2api 是一个将小米 AI Studio (MIMO) 模型转换为 OpenAI/Anthropic 兼容 API 的网关服务。它通过 WebSocket 隧道连接内网节点，实现多账号轮询负载均衡。

## 常用命令

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py

# 使用 uv 管理依赖（可选）
uv pip install -r requirements.txt
uv run main.py
```

## 架构设计

### 核心组件

- **main.py**: 统一入口，配置服务器地址/端口，启动 uvicorn
- **mimo2api/web_service.py**: FastAPI 应用主体，定义所有 API 路由，处理请求转发和流式响应
- **mimo2api/manager.py**: 多账号生命周期管理，控制每个账号的 Claw 实例创建/销毁/轮换（55分钟周期）
- **mimo2api/bridge.py**: 运行在内网节点上的桥接脚本，通过 WebSocket 接收请求并转发到小米 API
- **mimo2api/gateway_state.py**: 全局状态管理，维护活跃节点、待处理队列、冷却状态等
- **mimo2api/responses_converter.py**: OpenAI Responses API 与 Chat Completions 格式的双向转换器
- **mimo2api/auth.py**: 鉴权逻辑，支持 AI API Key 和 WebUI 登录认证
- **mimo2api/metrics_store.py**: 指标存储，记录请求成功率、延迟等统计数据

### 请求流程

1. 客户端发送 OpenAI/Anthropic 兼容请求到网关
2. 网关从活跃节点池中选择可用节点（轮询策略）
3. 通过 WebSocket 将请求转发到内网节点
4. 内网节点调用小米 API 并流式返回结果
5. 网关将响应转换为客户端期望的格式

### 关键 API 端点

- `/v1/chat/completions`: OpenAI Chat Completions 格式
- `/v1/responses`: OpenAI Responses 格式（自动转换为 Chat Completions）
- `/anthropic/v1/messages`: Anthropic Messages 格式
- `/v1/audio/speech`: TTS 语音合成
- `/v1/models` 和 `/anthropic/v1/models`: 模型列表

## 配置说明

配置通过 `.env` 文件或环境变量：

- `WS_TUNNEL_URL`: **必需**，内网节点连接的 WebSocket 桥接地址
- `MIMO_RELAY_OPENAI_KEY`: AI API Bearer 密钥（可选，不设则不鉴权）
- `MIMO_WEBUI_USERNAME` / `MIMO_WEBUI_PASSWORD`: WebUI 登录凭据（可选）
- `SERVER_HOST` / `SERVER_PORT`: 服务绑定地址（默认 0.0.0.0:8000）

## 数据文件

- `users/`: 存放用户凭证 JSON 文件（`user_*.json`），包含 `userId`、`serviceToken`、`xiaomichatbot_ph`
- `model_mapping.json`: 模型名称映射（如将 `claude-opus-4-7` 映射到 `mimo-v2.5-pro`）

## 开发注意事项

1. 项目使用 Python 3.10+，依赖 fastapi、uvicorn、httpx、websockets、pydantic
2. 所有协程任务通过 `_track_task()` 注册以防止被垃圾回收
3. 流式响应使用 keep-alive 机制防止连接超时（25秒间隔）
4. 节点冷却机制：401 错误会导致节点冷却 15 分钟（可通过 `MIMO_NODE_401_COOLDOWN_SECONDS` 配置）
5. 单进程锁文件机制防止重复启动（`mimo2api.lock`）
