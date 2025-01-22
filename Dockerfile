FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONOPTIMIZE=1
WORKDIR /app
COPY . /app/

# Install necessary packages and dependencies
# Install dependencies
RUN apt-get update && apt-get install -y \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libgbm1 \
    libxshmfence1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libcups2 \
    libxrandr2 \
    libxdamage1 \
    libxcomposite1 \
    libxrender1 \
    libxcursor1 \
    libxi6 \
    libxtst6 \
    libpango-1.0-0 \
    libx11-xcb1
RUN apt-get update && apt-get install -y xvfb
RUN pip install --no-cache-dir xvfbwrapper patchright fastapi[standard]
RUN python -m patchright install-deps chromium
RUN python -m patchright install chromium
RUN pip install logmagix
# Expose port 5000
EXPOSE 5000
CMD ["python", "main.py"]
