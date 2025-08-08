# Use an official Python runtime as a base image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port your Django app runs on
EXPOSE 8000

# Command to run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
# # Use a specific Python version as the base image
# FROM python:3.10

# # Set the working directory inside the container
# WORKDIR /app

# # Copy the requirements file and install dependencies
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy the entire app code into the container
# COPY . .

# COPY wait-for-db.sh /usr/local/bin/
# RUN chmod +x /usr/local/bin/wait-for-db.sh

# # Expose the default port for Django
# EXPOSE 8000

# # Command to run the Django development server
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]""""