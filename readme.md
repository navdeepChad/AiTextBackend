Virtual Environment Setup

Prerequisites
Python installed on your system.
pip (Python package installer) installed.
Docker: To run the app in a containerized environment


To run Locally :

Useful Commands

1. Create the virtual environment:

python -m venv venv

2 . Activate the Virtual Environment
To start using the virtual environment, you need to activate it.

On Windows:
venv\Scripts\activate

On macOS/Linux:
source venv/bin/activate

2. Install Dependencies
With the virtual environment activated, you can install project-specific dependencies using pip.

Install dependencies from requirements.txt:

pip install -r requirements.txt

3. Run the FastAPI app using Uvicorn:

uvicorn app.main:app --reload

Your FastAPI app should now be running locally at http://127.0.0.1:8000. You can access the Swagger UI at http://127.0.0.1:8000/docs.

Running with Docker

1. Build the Docker image:

From the root directory of the project, run the following command to build the Docker image (if it's not already):

docker build -t <name of image> .

2. Run the Docker container:

Once the image is built, you can run the container using the following command:

docker run -d -p 8000:8000 fastapi_template:latest
-d: Runs the container in detached mode.
-p 8000:8000: Maps port 8000 inside the container to port 8000 on your host machine.

3. Verify that the Docker container is running:

You can check the running containers with:

docker ps

4. To stop the running Docker container, use the following steps:

Find the container ID:

If you don't already know the container ID, you can find it by listing the running containers:

docker ps

5. Stop the container:

Replace <container_id> with the actual container ID you found:

docker stop <container_id>
This will stop the running container.

