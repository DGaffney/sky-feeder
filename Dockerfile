# Use an official Python image as the base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the application port
EXPOSE 8000

# Define environment variables
ENV APP_MODULE="server.app:app"
ENV HOST="0.0.0.0"
ENV PORT="8000"

# Run the application using uvicorn
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]
