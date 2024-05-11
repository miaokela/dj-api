# 使用官方 Python 镜像作为基础镜像
FROM python:3.8-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libc6-dev \
    libffi-dev \
    libssl-dev \
    make \
    # Add any other package dependencies you need
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 将依赖文件复制到容器中
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -U pip
RUN pip install --no-cache-dir -r requirements.txt

# 拷贝项目代码到容器中
COPY . /app

# 收集静态文件
RUN python manage.py collectstatic --noinput

# 暴露端口
EXPOSE 8000 5555

# 启动脚本
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
