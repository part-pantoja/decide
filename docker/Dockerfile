# Use the python:3.10-alpine image as the base image
FROM python:3.10-alpine

# Install system dependencies
RUN apk add --no-cache git postgresql-dev gcc libc-dev chromium chromium-chromedriver libffi-dev python3-dev build-base

# Install Python dependencies
RUN pip install gunicorn psycopg2 ipdb ipython

# Set the working directory to /app
WORKDIR /app

# Clone the repository
RUN git clone -b develop https://github.com/part-pantoja/decide.git .

# Install Python requirements
RUN pip install -r requirements.txt

# Set the working directory to /app/decide
WORKDIR /app/decide

# Copy the local settings.py
ADD docker-settings.py /app/decide/local_settings.py

# Command to run the application using gunicorn
CMD ["gunicorn", "-w", "5", "decide.wsgi", "--timeout=500", "-b", "0.0.0.0:5000"]
