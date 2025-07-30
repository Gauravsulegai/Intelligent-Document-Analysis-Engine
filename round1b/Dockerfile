# round1b/Dockerfile

# 1. Start with a Python version compatible with the libraries
FROM --platform=linux/amd64 python:3.9-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy the requirements file
COPY requirements.txt .

# 4. Install system dependencies that PyTorch might need
RUN apt-get update && apt-get install -y libgl1-mesa-glx

# 5. Install the Python libraries
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the locally saved model into the container
COPY model/ /app/model/

# 7. Copy the main application script
COPY main.py .

# 8. Set the command to run the script
CMD ["python", "main.py"]