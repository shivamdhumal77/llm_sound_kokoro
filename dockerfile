# Use Python 3.8 on Alpine 3.11 as the base image
FROM python:3.8-alpine3.11

# Set environment variables to ensure Python behaves as expected
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies needed for the application
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    make \
    espeak \
    git \
    git-lfs \
    g++ \
    libc-dev \
    bash

# Install Git LFS (Large File Storage) support
RUN git lfs install

# Set the working directory inside the container
WORKDIR /app

# Clone the repository and handle file setup
RUN git clone https://huggingface.co/hexgrad/Kokoro-82M && \
    cd Kokoro-82M && \
    apk add --no-cache espeak-ng && \
    pip install -q phonemizer torch transformers scipy munch

# Copy the requirements.txt to the container
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy all Python files (your application code) into the container
COPY . /app/

# Expose port 8000 for the FastAPI app
EXPOSE 8000

# Start the FastAPI application with Uvicorn
CMD ["uvicorn", "main_file:app", "--host", "0.0.0.0", "--port", "8000"]
