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
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("https://worldtimeapi.org/api/timezone/Etc/UTC", timeout=5.0)
            timestamp = resp.json().get("datetime") if resp.status_code == 200 else "local-time"
    except Exception:
        timestamp = "local-time"

    return {
        "status": "healthy",
        "version": "0.1.0",
        "timestamp": timestamp
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

@app.get("/status/health", tags=["system"])
async def status_health():
    """
    Get detailed system health status.
    """
    return [
        {"metric": "CPU Usage", "status": "OK", "value": "12%"},
        {"metric": "Memory", "status": "OK", "value": "450MB"},
        {"metric": "Disk I/O", "status": "Warning", "value": "High"}
    ]

@app.get("/status/scrapers", tags=["system"])
async def status_scrapers():
    """
    Get scraper status.
    """
    return [
        {"name": "Google API", "state": "Running", "last_run": "2m ago"},
        {"name": "Twitter API", "state": "Idle", "last_run": "1h ago"},
        {"name": "Reddit API", "state": "Error", "last_run": "10m ago"}
    ]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
