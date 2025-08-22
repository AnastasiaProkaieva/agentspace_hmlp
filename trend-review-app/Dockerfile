# Dockerfile

# Use an official lightweight Python image.
FROM python:3.11-slim

# Set the environment to be non-interactive
#ENV DEBIAN_FRONTEND=noninteractive

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy all the application files and folders (including static/ and templates/)
# The .dockerignore file will prevent unnecessary files from being copied.
COPY . .

# The PORT environment variable is automatically set by Cloud Run.
# We'll use 8080 as a default if PORT is not set.
ENV PORT 8080

# Expose the port the app runs on. This is good practice for documentation.
EXPOSE 8080

# Use the shell form of CMD to allow shell variable substitution for $PORT.
# This command runs the application and makes it available outside the container.
CMD uvicorn main:app --host 0.0.0.0 --port $PORT