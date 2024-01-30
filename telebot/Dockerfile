# Use an official Python runtime as the base image
FROM python:3.11-slim

ENV PIP_REQUIRE_VIRTUALENV=false

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8001

# Run the FastAPI app using Uvicorn
CMD ["python", "./bot_run.py"]
