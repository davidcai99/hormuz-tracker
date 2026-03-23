FROM python:3.11-slim

WORKDIR /app

# 复制整个项目（保持目录结构）
COPY . .

# 安装依赖
RUN pip install --no-cache-dir -r backend/requirements.txt

# Railway需要监听 $PORT 环境变量
# 启动命令：从backend目录运行（因为app.py里用到了相对路径 ../frontend）
CMD ["sh", "-c", "cd /app/backend && gunicorn --bind 0.0.0.0:${PORT:-5000} app:app"]
