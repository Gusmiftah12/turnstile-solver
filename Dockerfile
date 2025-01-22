FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONOPTIMIZE=1
WORKDIR /app
COPY . /app/

# Install necessary packages and dependencies
RUN apt-get update && apt-get install -y xvfb
RUN pip install --no-cache-dir xvfbwrapper patchright fastapi[standard]
RUN python -m patchright install-deps chromium
RUN python -m patchright install chromium

# Expose port 5000
EXPOSE 5000
CMD ["python", "main.py"]
