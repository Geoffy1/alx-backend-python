# Use an official Python runtime as a base image
#FROM python:3.10
# Use a slim Python 3.9 image as the base#
FROM python:3.9-slim
# new
ENV PYTHONDONTWRITEBYTECODE=1
# new
ENV PYTHONUNBUFFERED=1
# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port your Django app runs on
EXPOSE 8000

# Run the Django application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "messaging_app.wsgi:application"]
# Command to run the Django development server
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]