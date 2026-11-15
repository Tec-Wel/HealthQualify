FROM python:3.12-slim
WORKDIR /app
COPY healthqualify ./healthqualify
COPY examples ./examples
COPY tests ./tests
USER 65532:65532
CMD ["python", "-m", "healthqualify.cli", "--help"]
