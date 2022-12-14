import os


def get_postgres_uri():
    host = "localhost"
    port = 5432
    password = "password"
    user, db_name = "postgres", "allocation"
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"


def get_api_url():
    host = os.environ.get("API_HOST", "localhost")
    port = 5000
    return f"http://{host}:{port}"
