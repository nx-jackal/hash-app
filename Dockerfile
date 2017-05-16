FROM python:2.7-slim
WORKDIR /app
ADD . /app
RUN pip install -r requirements.txt
EXPOSE 5000
ENV REDIS_ENABLED False
ENV REDIS_SERVER 10.0.0.6
ENV REDIS_PORT 6379
CMD ["python", "main.py"]
