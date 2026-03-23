FROM python:3.11-slim

WORKDIR /app

# 复制整个项目
COPY . .

# 安装依赖
RUN pip install --no-cache-dir -r backend/requirements.txt

# Railway会自动将外部端口映射到PORT环境变量
# gunicorn绑定到0.0.0.0:PORT（Railway要求绑定0.0.0.0）
CMD ["sh", "-c", "cd /app/backend && python -c 'import time; time.sleep(3)' && gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 1 --timeout 120 --access-logfile - app:app"]
