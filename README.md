# Web Text Board

极简网页临时文本板，纯文本编辑，Redis 持久化。

## Docker 部署

```bash
docker build -t web-text-board .
docker run -d -p 8000:8000 \
  -e EDIT_USER=youruser \
  -e EDIT_PASSWORD=yourpass \
  -e REDIS_URL=redis://redis-server:6379 \
  -e SESSION_SECRET=your-secret-key \
  web-text-board
```

## Zeabur 部署

### 镜像地址
```
ghcr.io/kumacoolgo/web-text-board:latest
```

### 必需环境变量

| 变量 | 说明 |
|------|------|
| `EDIT_USER` | 登录用户名 |
| `EDIT_PASSWORD` | 登录密码 |
| `REDIS_URL` | Redis 连接地址 |
| `SESSION_SECRET` | 会话签名密钥 |

### 端口
- 容器内/外部：`8000`

### 步骤

1. Zeabur 连接 GitHub 仓库 `kumacoolgo/NullPage`
2. 添加 **Redis** 服务
3. 部署 `web-text-board` 服务，填入环境变量
4. 访问分配的域名
