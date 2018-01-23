# Use an official Python runtime as a parent image
FROM python:3.6

# Copy the current directory contents into the container at /app
COPY ./abi /abi
COPY ./src /src
COPY ./pynode.ini /pynode.ini
COPY ./requirements.txt /requirements.txt

# Set the working directory to /app
WORKDIR /src

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r ../requirements.txt

EXPOSE 7545 8545 5001

# Run app.py when the container launches
CMD ["python", "pynoded.py"]