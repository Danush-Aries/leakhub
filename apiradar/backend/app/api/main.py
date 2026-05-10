from fastapi import FastAPI
from fastapi.responses import JSONResponse
import httpx
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("apiradar")

app = FastAPI(title="APIRadar Backend", version="0.1.0")

@app.get("/health", tags=["system"])
async def health_check():
    """
    Verify that the API is up and running.
    """
    return {
        "status": "healthy",
        "version": "0.1.0",
        "timestamp": httpx.get("https://worldtimeapi.org/api/timezone/Etc/UTC").json().get("datetime") if False else "local-time"
    }

@app.get("/ping", tags=["system"])
async def ping():
    """
    Quick heartbeat check.
    """
    return {"message": "pong"}

@app.get("/dependencies", tags=["system"])
async def check_dependencies():
    """
    Check connectivity to external dependencies.
    """
    results = {}
    # Example check for GitHub API connectivity
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("https://api.github.com", timeout=5.0)
            results["github_api"] = "reachable" if resp.status_code == 200 else f"error_{resp.status_code}"
    except Exception as e:
        results["github_api"] = f"unreachable: {str(e)}"

    # Example check for APIs.guru
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("https://api.apis.guru", timeout=5.0)
            results["apis_guru"] = "reachable" if resp.status_code == 200 else f"error_{resp.status_code}"
    except Exception as e:
        results["apis_guru"] = f"unreachable: {str(e)}"

    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
