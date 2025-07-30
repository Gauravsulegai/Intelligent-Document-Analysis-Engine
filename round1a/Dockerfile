# Dockerfile in round1a/

# 1. Start with a lightweight version of Python.
# The '--platform' flag ensures it's compatible with the required amd64 architecture.
FROM --platform=linux/amd64 python:3.9-slim

# 2. Set the working directory inside the container.
# All subsequent commands will be run from /app.
WORKDIR /app

# 3. Copy the requirements file into the container.
COPY requirements.txt .

# 4. Install the Python libraries listed in requirements.txt.
# '--no-cache-dir' keeps the image size smaller.
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the application's code (main.py) into the container.
COPY . .

# 6. Specify the command to run when the container starts.
# This will execute our Python script.
CMD ["python", "main.py"]