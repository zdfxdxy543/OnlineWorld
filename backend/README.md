# Backend

`backend/` 负责 `OnlineWorld` 的服务端能力，目标是为前端、多网站模拟系统和后续 AI 叙事引擎提供稳定基础。

## 当前技术方向

- `FastAPI`：主要 Web API 框架
- `Uvicorn`：本地开发服务器
- 分层结构：`API -> Services -> Domain -> Repositories -> Infrastructure`

## 设计原则

- 先创建事实，再生成文本
- 路由层不直接操作数据库
- `LLM` 不直接写世界状态
- 所有跨站行为都形成事件链
- 目录按职责拆分，避免单目录堆叠 `Python` 文件

## 目录结构

```text
backend/
├─ app/
│  ├─ api/                  # 对前端暴露的 HTTP API
│  ├─ consistency/          # 一致性校验
│  ├─ core/                 # 配置与应用级基础设施
│  ├─ domain/               # 核心实体与事件模型
│  ├─ infrastructure/       # 数据库、LLM 等外部依赖适配
│  ├─ repositories/         # 仓储抽象与最小实现
│  ├─ schemas/              # API 请求/响应模型
│  ├─ services/             # 业务用例编排
│  ├─ simulation/           # 世界推进与内容草稿生成
│  ├─ container.py          # 依赖装配
│  └─ main.py               # FastAPI 入口
├─ tests/
│  └─ smoke_check.py        # 最小导入验证
└─ requirements.txt
```

## 已提供的最小能力

- `GET /api/v1/health`：健康检查
- `GET /api/v1/world/summary`：世界摘要示例
- `POST /api/v1/world/demo-post`：演示“事实先行、文本后生成”的帖子创建流程

`demo-post` 的行为链：

1. 创建行为意图
2. 执行业务动作，例如生成文件资源
3. 将事实整理为结构化数据
4. 调用 `LLM` 适配器生成文字草稿
5. 进行一致性校验
6. 返回可发布内容与事件链

## 本地启动

在 Windows PowerShell 中：

```powershell
cd D:\Else\OnlineWorld\backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

启动后可访问：

- `http://127.0.0.1:8000/api/v1/health`
- `http://127.0.0.1:8000/docs`

## 最小验证

```powershell
cd D:\Else\OnlineWorld\backend
.\venv\Scripts\python.exe tests\smoke_check.py
```

## 下一步建议

1. 补充真实数据库模型与迁移工具
2. 将 `mock` LLM 客户端替换为真实供应商适配器
3. 为论坛、商店、私信分别建立服务层用例
4. 引入统一事件表与事实表，支撑故事链追踪
