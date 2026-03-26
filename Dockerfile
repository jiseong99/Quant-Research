FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY .env .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

그 다음 `quant-research` 폴더 바로 아래에 `.dockerignore` 파일 새로 만들고 아래 내용 붙여넣고 **Ctrl+S** 저장하세요.
```
venv/
frontend/
__pycache__/
*.pyc
*.pyo
.git/
notebooks/