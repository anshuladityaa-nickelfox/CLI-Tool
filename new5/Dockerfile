Here's a sample Dockerfile based on your requirements:

```dockerfile
# Use the official Python 3.11 slim image as the base
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Collect static files
RUN python manage.py collectstatic --no-input

# Expose the port the application will run on
EXPOSE 8000

# Run the command to start the development server when the container launches
CMD ["gunicorn", "new5.wsgi:application", "--workers", "3"]
```

This Dockerfile does the following:

1. Uses the official Python 3.11 slim image as the base.
2. Sets the working directory in the container to `/app`.
3. Copies the `requirements.txt` file into the container and installs the dependencies.
4. Copies the application code into the container.
5. Collects static files using the `collectstatic` command.
6. Exposes port 8000, which is the default port for the Gunicorn server.
7. Sets the default command to run when the container launches, which starts the Gunicorn server with the `new5` application.

Note: Replace `new5.wsgi:application` with the actual path to your WSGI application. 

Also, make sure to create a `requirements.txt` file in the same directory as your Dockerfile, listing all the dependencies required by your application. 

You can build the Docker image by running the following command in the terminal, from the directory containing your Dockerfile:
```bash
docker build -t my-python-app .
```
And you can run the Docker container using:
```bash
docker run -p 8000:8000 my-python-app
```