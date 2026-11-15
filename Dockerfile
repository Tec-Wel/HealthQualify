FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY healthqualify ./healthqualify
COPY examples ./examples
COPY tests ./tests
RUN mkdir -p /data && chown -R 65532:65532 /data
USER 65532:65532
CMD ["python", "-m", "healthqualify.appcli", "--help"]
