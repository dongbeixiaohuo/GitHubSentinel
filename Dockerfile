# 使用 Python 3.10 作为基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置环境变量
ENV PYTHONPATH=/app

# 创建必要的目录和文件
RUN mkdir -p config && \
    mkdir -p daily_progress && \
    mkdir -p logs

# 创建默认配置文件
RUN echo '{\
    "github_token": "",\
    "openai_api_key": "",\
    "repositories": []\
}' > config/config.json

# 暴露端口(用于 Gradio 界面)
EXPOSE 7860

# 添加调试信息
RUN echo "Current directory structure:" && ls -R

# 设置启动命令
CMD ["python", "-u", "src/main.py"]