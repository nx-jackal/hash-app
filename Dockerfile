FROM python:2.7-slim
WORKDIR /app
ADD . /app
RUN pip install -r requirements.txt
EXPOSE 5000
ENV REDIS_ENABLED True
ENV REDIS_SERVER 127.0.0.1
ENV REDIS_PORT 6379
CMD ["python", "main.py"]
