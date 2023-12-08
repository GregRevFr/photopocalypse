# Use Python 3.10.6 image as a base image
FROM python:3.10.6

RUN apt-get update \
    && apt-get install -y libgl1-mesa-glx \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Copy the requirements file and install the required packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Command to run the application using Uvicorn on port 8080
CMD ["uvicorn", "photopocalypse.api.fast:app", "--host", "0.0.0.0", "--port", "8080"]
