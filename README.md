# FastAPI Project

This is a FastAPI project that includes Docker setup for easy deployment. The project allows users to manage and import calendar data, handle authentication, and interact with a database.

## Prerequisites

Before you begin, make sure you have the following installed:

## Installation

### 1. Clone the Repository

Clone the repository to your local machine:

```bash
git clone [<repository_url>](https://github.com/YodaBikarbona/kalendar_ciscenja.git)
cd <project_folder>
```

### 2. Install Dependencies (pip or poetry)

Pip

```bash
pip install -r requirements.txt
```

Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
```
```bash
poetry install
```


### 3. Set Up Environment Variables

```bash
touch .env
```
Add the enviroment values
```bash
DATABASE=DB_NAME
HOST=DB_HOST
JWT_ACCESS_SECRET_KEY=JWT_SECRET
JWT_REFRESH_SECRET_KEY=JWT_REFRESH_SECRET
PASSWORD=DB_PASSWORD
PORT=DB_PORT
SERVER_TYPE=SERVER_TYPE
USERNAME=DB_USERNAME
```

### Run the app

```bash
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8080
```
or
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```
This would make the FastAPI app accessible at [http://localhost:8080](http://localhost:8080)

## Docker Setup

## Prerequisites

Before you begin, make sure you have the following installed:

- **Docker**
- **Docker Compose**

You can download and install Docker and Docker Compose from the official websites:

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

Run the app

```bash
docker-compose up --build
```
