FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m playwright install
COPY . .
EXPOSE 8000
CMD ["python", "main.py"]
