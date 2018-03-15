# Use an official Python runtime as a parent image
FROM python:3.6

# Copy the current directory contents into the container at /app
COPY ./abi /abi
COPY pynode /src
COPY ./pynode.ini /pynode.tmp.ini
COPY ./requirements.txt /requirements.txt

# Set the working directory to /app
WORKDIR /src

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r ../requirements.txt

# Run app.py when the container launches
CMD ["python", "pynoded.py"]
