# 安装说明

## 使用 uv 安装（推荐）

```powershell
# 安装 uv (如果还没安装)
# Windows PowerShell 安装命令
iwr -useb https://astral.sh/uv/install.ps1 | iex

# 创建虚拟环境并安装依赖
uv venv
uv pip install -e .
```

## 使用 pip 安装

```powershell
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 安装项目依赖
pip install -e .
```

## 配置

1. 复制`.env.example`到`.env`并填写你的配置：

```powershell
Copy-Item .env.example .env
```

2. 编辑`.env`文件，填写以下必要配置：
   - `OPENAI_API_KEY`: 你的OpenAI API密钥
   - `OPENAI_MODEL`: 使用的模型（默认gpt-4）
   - `USER_NAME`: 你的名字
   - `COMPANION_NAME`: 你希望AI助手使用的名字

3. 编辑`configs/OAI_CONFIG_LIST.json`文件，填写你的OpenAI API密钥

## 运行项目

```powershell
# 使用命令行接口运行
companion start

# 或者使用Python脚本运行
python scripts/start_companion.py
```

## 其他设置

### ChromaDB 存储

默认情况下，情感记忆存储在 `./memory_db` 目录中。如果你想更改存储位置，请在`.env`文件中修改 `CHROMA_DB_DIR` 变量。
