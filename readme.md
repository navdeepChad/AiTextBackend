## Virtual Environment Setup

### Prerequisites
- Python installed on your system.
- `pip` (Python package installer) installed.
- Docker: To run the app in a containerized environment.


# To run locally

### 1. Create the virtual environment:

```bash
  python -m venv venv
```


### 2. To start using the virtual environment, you need to activate it.

#### On Windows:

```bash
venv\Scripts\activate
```


#### On macOS/Linux:

```bash
source venv/bin/activate
```

#### 2. Install Dependencies

Install dependencies from requirements.txt:

```bash
pip install -r requirements.txt
```

### 3. Run the FastAPI app using Uvicorn:

```bash
uvicorn app.main:app --reload
```

Your FastAPI app should now be running locally at http://127.0.0.1:8000. You can access the Swagger UI at http://127.0.0.1:8000/docs.

# Running with Docker Compose

## 1. Build and run the application using Docker Compose:

From the root directory of the project, where the docker-compose.yml file is located, you can use the following command to build and run your application:

```
docker-compose up --build
```


## 2. Verify that the Docker container is running:

Once the container is running, you can verify it by listing the running containers with:

```bash
docker-compose ps
```
This will show the services defined in your docker-compose.yml file. You should see your app container running and listening on port 8000.

## 3. Access the FastAPI app:
Once the container is running, your FastAPI app should be available at:

```bash
http://127.0.0.1:8000/docs
```
## 4. To stop the running Docker containers:

If you need to stop the application and its containers, run:

```bash
docker-compose down
```

This will stop and remove all containers defined in the docker-compose.yml file.

If you only want to stop the containers without removing them, use:

```bash
docker-compose stop
```

## 5. If you want to rebuild and run the Docker containers again, you can use:

```bash
docker-compose up --build
```

