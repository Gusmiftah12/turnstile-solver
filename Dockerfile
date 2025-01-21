FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y \
    libxcb-shm0 \
    libx11-xcb1 \
    libx11-6 \
    libxcb1 \
    libxext6 \
    libxrandr2 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxfixes3 \
    libxi6 \
    libxtst6 \
    libgtk-3-0 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libcairo-gobject2 \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    libasound2 \
    libxrender1 \
    libfreetype6 \
    libfontconfig1 \
    libdbus-glib-1-2 \
    libdbus-1-3 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

RUN python -m playwright install

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
