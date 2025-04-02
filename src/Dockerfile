FROM python:3.12-slim

# Set the working directory inside the container to /app
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Create the src directory and copy all project files into it
RUN mkdir /app/src
COPY main.py /app/src/main.py
COPY schema.py /app/src/schema.py
COPY models.py /app/src/models.py
COPY database.py /app/src/database.py
COPY __init__.py /app/src/__init__.py

# Expose the application port
EXPOSE 8000

CMD ["fastapi", "run", "src/main.py", "--port", "8000"]
