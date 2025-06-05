# 安装说明

## 获取项目代码

```powershell
# 克隆项目
git clone https://github.com/yourusername/emotional-companion.git
cd emotional-companion
```

## 使用 uv 安装（推荐）

```powershell
# 安装 uv (如果还没安装)
# Windows PowerShell 安装命令
iwr -useb https://astral.sh/uv/install.ps1 | iex

# 方法1：一键安装（推荐）
uv sync

# 方法2：分步安装
# 创建虚拟环境
uv venv

# 激活虚拟环境
.venv\Scripts\Activate.ps1

# 安装项目依赖（开发模式）
uv add --editable .
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
#激活虚拟环境（在项目根目录下执行）
.\venv\Scripts\activate  

# 使用命令行接口运行
companion

# 或者使用Python脚本运行
python scripts/start_companion.py

#或直接运行命令行启动文件
python emotional_companion\cli.py

# 或者使用uv运行
uv run companion
```

## 其他设置

### ChromaDB 存储

默认情况下，情感记忆存储在 `./memory_db` 目录中。如果你想更改存储位置，请在`.env`文件中修改 `CHROMA_DB_DIR` 变量。

### 验证安装

安装完成后，你可以通过以下命令验证安装是否成功：

```powershell
# 检查依赖是否正确安装
python -c "import emotional_companion; print('安装成功！')"
```
