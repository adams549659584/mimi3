# mimi3 (mimo2api)

小米 AI Studio 自动化控制网关，将 MIMO 模型进行转发并兼容。

## 功能

- OpenAI 兼容 API 中转（支持 `/v1/chat/completions`, `/v1/responses`, `/anthropic/v1/messages`）
- Web 控制面板（实时监控、日志查看）
- 多账号轮询负载均衡
- 流式响应支持

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 复制并配置环境变量
cp env.example .env

# 启动服务
python main.py
```

## ngrok 内网穿透配置

本项目需要一个公网可达的 WebSocket 地址。推荐使用 [ngrok](https://ngrok.com) 进行内网穿透。

### 方式一：自动启动（推荐）

```bash
# 安装 ngrok（Windows）
scoop install ngrok

# 添加 authtoken（仅需执行一次）
ngrok config add-authtoken <YOUR_AUTHTOKEN>

# 自动启动（会自动启动 ngrok、检测隧道地址、启动服务）
python start.py
```

脚本会自动：
1. 启动 ngrok（如果尚未运行）
2. 查询本地 API 获取公网地址
3. 设置 `WS_TUNNEL_URL` 环境变量
4. 启动 mimo2api 网关服务

### 方式二：手动配置

```bash
# 终端 1：启动 ngrok
ngrok http 8000

# 终端 2：复制并编辑环境变量
cp env.example .env
# 在 .env 中配置 ngrok 提供的公网地址：
# WS_TUNNEL_URL=wss://your-random-id.ngrok-free.app/ws

python main.py
```

### 方式三：Docker Compose

```bash
# 在 .env 中配置 NGROK_AUTHTOKEN
cp env.example .env

# 构建并启动
docker compose up --build

# 后台运行
docker compose up -d --build

# 查看日志
docker compose logs -f

# 停止
docker compose down
```

容器内自动启动 ngrok 并检测隧道地址，无需手动配置 `WS_TUNNEL_URL`。ngrok Web UI 可通过 `http://localhost:4040` 访问。

## 前置条件

- Python 3.10+
- 公网可达的 WebSocket 地址（通过 ngrok 或直接公网 IP）
- ngrok authtoken（从 https://dashboard.ngrok.com 获取）

## 免责声明

1. **本项目仅供学习交流使用，禁止一切商业/滥用行为。**
2. 本项目为个人独立开发的开源项目，与小米公司及其关联方**无任何隶属、授权或合作关系**。
3. MIMO、Xiaomi AI Studio 等名称及商标归小米公司所有，本项目不主张任何权利。
4. 本项目不提供任何小米账号、密钥或付费服务的破解，仅作为技术研究用途。
5. 使用者应遵守所在地法律法规及小米服务条款，因使用本项目产生的一切后果由使用者自行承担。
6. 本项目代码随缘更新，作者不提供任何保证或技术支持。
7. **建议优先使用小米官方 API**，本项目仅为技术研究备选方案。
8. 如有任何权益问题，请联系删除。

## 致谢
[linux.do](https://linux.do)