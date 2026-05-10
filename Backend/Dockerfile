# 1. Start with a lightweight Python image
FROM python:3.11-slim

# 2. Set the folder inside the container where our code will live
WORKDIR /app

# 3. Copy our requirements file to the container
# Note: We will move your requirements.txt into the backend folder in the next step
COPY requirements.txt .

# 4. Install the libraries
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the backend code
COPY . .

# 6. Tell Docker the app runs on port 8001
EXPOSE 8001

# 7. The final command to start the server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
