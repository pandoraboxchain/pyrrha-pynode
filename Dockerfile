# Use an official Python runtime as a parent image
FROM python:3.6

# Copy the current directory contents into the container at /app
COPY ./abi /abi
COPY ./pynode /pynode
COPY ./requirements.txt /requirements.txt

# Set the working directory to /app
WORKDIR /pynode

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r ../requirements.txt

# Run app.py when the container launches
CMD ["python",  "./pynode.py", "-p","<customer_vault_pass>", "-c", "core/config/pynode.ini", "-i", "pandora", "-e", "remote", "-a", "../abi/"]
