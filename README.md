# Web Text Board

一个极简的网页临时文本板，用于粘贴、编辑和保存纯文本。专为单用户设计，使用 Redis 持久化存储。

## 功能特点

- 纯文本编辑器
- 手动保存（无自动保存）
- 字体大小控制（A-/A+）和移动端双指缩放
- 7 天会话保持
- Redis 持久化存储
- 移动端优先的响应式设计

## 技术栈

- **后端**: Python 3.12 + FastAPI
- **模板**: Jinja2
- **前端**: 纯 HTML + CSS + JavaScript（无框架）
- **数据库**: Redis
- **会话**: 签名 Cookie（itsdangerous）
- **容器**: Docker

## 环境变量

| 变量 | 必填 | 描述 |
|------|------|------|
| `EDIT_USER` | 是 | 登录用户名 |
| `EDIT_PASSWORD` | 是 | 登录密码 |
| `REDIS_URL` | 是 | Redis 连接地址（如 `redis://localhost:6379`） |
| `SESSION_SECRET` | 是 | 会话 Cookie 签名密钥 |

### 可选变量

| 变量 | 默认值 | 描述 |
|------|--------|------|
| `SESSION_LIFETIME_DAYS` | 7 | 会话 Cookie 有效期 |
| `DEFAULT_FONT_SIZE_PX` | 18 | 默认编辑器字体大小 |
| `MIN_FONT_SIZE_PX` | 12 | 最小字体大小 |
| `MAX_FONT_SIZE_PX` | 40 | 最大字体大小 |

## 本地开发

### 前置要求

- Python 3.12
- Redis 服务运行中

### 安装步骤

1. 克隆仓库
2. 创建 `.env` 文件并配置必填变量：

```env
EDIT_USER=myuser
EDIT_PASSWORD=mypassword
REDIS_URL=redis://localhost:6379
SESSION_SECRET=your-super-secret-key-here
```

3. 安装依赖：

```bash
cd web-text-board
pip install -r requirements.txt
```

4. 启动开发服务器：

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. 在浏览器中打开 http://localhost:8000

## 运行测试

### 前置要求

- Redis 服务运行中
- 测试 Redis 数据库（默认使用 DB 15 进行隔离）

### 运行测试

```bash
cd web-text-board
pytest -v
```

## Docker 部署

### 构建镜像

```bash
cd web-text-board
docker build -t web-text-board .
```

### 运行容器

```bash
docker run -d \
  --name web-text-board \
  -p 8000:8000 \
  -e EDIT_USER=myuser \
  -e EDIT_PASSWORD=mypassword \
  -e REDIS_URL=redis://redis-server:6379 \
  -e SESSION_SECRET=your-secret-key \
  web-text-board
```

## Zeabur 部署

Zeabur 支持 Docker 容器部署，可使用其 Redis 服务。

### 部署步骤

1. 将代码推送到 GitHub
2. 连接仓库到 Zeabur
3. 在 Zeabur 面板中添加环境变量：
   - `EDIT_USER`
   - `EDIT_PASSWORD`
   - `REDIS_URL`（使用 Zeabur 的 Redis 服务绑定）
   - `SESSION_SECRET`（生成随机字符串）
4. 部署

### Zeabur Redis 要求

Zeabur 提供 Redis 作为服务绑定，使用 Redis 服务中提供的 `REDIS_URL` 环境变量。

## API 接口

### 页面路由

| 路径 | 方法 | 描述 |
|------|------|------|
| `/` | GET | 重定向到 `/editor` 或 `/login` |
| `/login` | GET | 渲染登录页面 |
| `/login` | POST | 处理登录提交 |
| `/editor` | GET | 渲染编辑器页面（需认证） |

### API 路由

| 路径 | 方法 | 描述 |
|------|------|------|
| `/api/document` | GET | 获取当前文档内容和字体大小 |
| `/api/save` | POST | 保存文档内容和字体大小 |
| `/api/clear` | POST | 清空文档（保存空内容） |

### API 示例

```bash
# 获取文档
curl -b "session=YOUR_SESSION_TOKEN" http://localhost:8000/api/document

# 保存文档
curl -b "session=YOUR_SESSION_TOKEN" -X POST \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello world", "font_size_px": 18}' \
  http://localhost:8000/api/save

# 清空文档
curl -b "session=YOUR_SESSION_TOKEN" -X POST \
  -H "Content-Type: application/json" \
  -d '{"font_size_px": 18}' \
  http://localhost:8000/api/clear
```

## 项目结构

```
web-text-board/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI 应用
│   ├── config.py        # 配置和环境变量
│   ├── auth.py          # 认证工具
│   ├── redis_store.py   # Redis 操作
│   ├── schemas.py       # Pydantic 模型
│   ├── templates/
│   │   ├── login.html
│   │   └── editor.html
│   └── static/
│       ├── app.css
│       └── app.js
├── tests/
│   ├── test_auth.py
│   ├── test_document_api.py
│   └── test_editor_page.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .gitignore
├── pytest.ini
└── README.md
```

## 许可证

MIT
