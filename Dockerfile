FROM python:3.12-slim

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV DOCKER_ENV=true
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y gcc g++ curl && rm -rf /var/lib/apt/lists/*

# 复制并安装Python依赖
COPY requirements-base.txt .
RUN pip install --no-cache-dir -r requirements-base.txt

# 复制应用代码
COPY emotional_companion/ ./emotional_companion/
COPY web_api/ ./web_api/
COPY configs/ ./configs/
COPY setup.py .

# 安装项目
RUN pip install -e .

# 创建必要目录
RUN mkdir -p /app/logs /app/memory_db

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "web_api/start_web_api.py"]