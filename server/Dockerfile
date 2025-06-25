# Dockerfile for a the server application
# Based on Python 3.11 Alpine image for a lightweight container
FROM python:3.11.0-alpine

# Make a directory for the application
RUN mkdir /app

# Set it as the working directory
WORKDIR /app

# copy the files from the current directory to the /app directory in the container
COPY . /app/

RUN pip install -r requirements.txt

# Run the server on the start of the container
CMD [ "python", "-u", "main.py" ]
