# Base image with Python
FROM python:3.11-slim

# Install system dependencies required for Tkinter and Matplotlib
RUN apt-get update && apt-get install -y \
    python3-tk \
    libfreetype6-dev \
    libpng-dev \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxft2 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir matplotlib


# Default command to run the Tkinter app
CMD ["python", "app.py"]

