# 构建与安装指南

## 前置要求

| 工具 | 版本 | 说明 |
|------|------|------|
| [uv](https://docs.astral.sh/uv/) | >= 0.7 | Python 包管理器 |
| Node.js | >= 18 | 前端运行时 |
| npm | >= 9 | 随 Node.js 附带 |

> 如果尚未安装 uv，请参照 [官方文档](https://docs.astral.sh/uv/getting-started/installation/) 安装。

---

## 1. 克隆仓库

```bash
git clone <repo-url>
cd Account-Book
```

---

## 2. 后端（Python / FastAPI）

### 2.1 创建虚拟环境并安装依赖

```bash
# 创建并激活虚拟环境（Python 3.10+）
uv venv --python 3.10
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 安装生产依赖
uv pip install -r backend/requirements.txt

# （可选）安装开发依赖（含 ruff 代码检查）
uv pip install -r backend/requirements-dev.txt
```

### 2.2 启动后端

```bash
uv run uvicorn backend.main:app --reload --port 8000
```

启动后可访问 http://127.0.0.1:8000/docs 查看 API 文档。

---

## 3. 前端（React / Vite）

### 3.1 安装依赖

```bash
cd frontend
npm install
```

### 3.2 启动前端开发服务器

```bash
npm run dev
```

默认运行在 http://localhost:5173，`/api` 请求会由 Vite 代理转发到后端 `8000` 端口。

---

## 4. 一键启动（Windows）

项目根目录提供了 `start-dev.bat`，双击即可同时启动前后端：

```bash
start-dev.bat
```

---

## 5. 旧数据迁移（可选）

如果从旧版（PyQt5 + CSV）迁移，将 `spending.csv` 和 `classifier.csv` 放到项目根目录，然后运行：

```bash
uv run python -m backend.migrate
```

---

## 6. 代码检查

```bash
# 运行 ruff lint
uv run ruff check backend/

# 自动修复可修复的问题
uv run ruff check backend/ --fix
```

---

## 7. 生产构建（前端）

```bash
cd frontend
npm run build
```

构建产物输出到 `frontend/dist/` 目录，可部署到任意静态文件服务器。
