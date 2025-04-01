# Azure Agent API

* [Local Setup](#local-setup)
* [Deploy to Azure](#deploy-to-azure)

## Local Setup
1. Start Docker Desktop

1. Clone Repo & change directory:
    ```
    git clone <GITHUB_URL>
    cd azure-agent-api
    ```

1. Setup virtual environment:
    ```
    python -m venv .venv
    ```

    * Mac/Linux activation:
        ```
        source .venv/bin/activate
        ```
    * Windows activation:
        ```
        .venv\Scripts\activate
        ```

1. Install FastAPI and Uvicorn:
    ```
    pip install -r requirements.txt
    ```

1. Test running API:
    ```
    uvicorn main:app --host 127.0.0.1 --port 8000 --reload
    ```
    * API: http://127.0.0.1:8000
    * Docs: http://127.0.0.1:8000/docs

1. Build and run Docker:
    ```
    docker build -t azure-agent-api .
    ```
    ```
    docker run -p 127.0.0.1:8000:8000 --env-file .env azure-agent-api
    ```

## Initial Deploy to Azure
1. Run the deploy script:
    ```
    ./deploy.ps1
    ```
1. In Azure Portal, navigate to App > Settings > Identity
    * Enable system assigned identity
    * Add `Azure AI Developer` role assignments

## Deploy Updates
```
./deploy_updates.ps1
```
