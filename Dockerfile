# Use a Python 3.10 base image to match the project requirement
FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

# Create and switch to the working directory
WORKDIR /app

# Install system dependencies needed to compile Python packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency metadata first to leverage Docker layer caching
COPY pyproject.toml ./

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Copy the rest of the application code
COPY . .

# Install the project (and its dependencies) via the pyproject metadata
RUN pip install --no-cache-dir .

# Expose the port the app runs on
EXPOSE 80

# Define the command to run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
