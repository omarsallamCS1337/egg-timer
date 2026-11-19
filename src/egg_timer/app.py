"""FastAPI app exposing the egg timer over HTTP."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .timer import MAX_DURATION_SECONDS, EggTimer

app = FastAPI(title="Egg Timer", version="0.1.0")

# One timer per process. Deliberately in memory: restart the app, lose the egg.
timer = EggTimer()


class StartRequest(BaseModel):
    """Body for /timer/start. Leave out `duration_seconds` to count up instead."""

    duration_seconds: float | None = Field(
        default=None,
        gt=0,
        le=MAX_DURATION_SECONDS,
        description="Count down from this many seconds. Omit to run as a stopwatch.",
    )


@app.post("/timer/start")
def start(request: StartRequest | None = None) -> dict:
    """Start the timer. Accepts no body, {}, or a duration to count down from."""
    duration = request.duration_seconds if request else None
    timer.start(duration)
    return timer.status()


@app.post("/timer/stop")
def stop() -> dict:
    """Stop the timer. 409 if it was already stopped."""
    if not timer.stop():
        raise HTTPException(status_code=409, detail="Timer is not running")
    return timer.status()


@app.get("/timer/status")
def status() -> dict:
    """Current state of the timer."""
    return timer.status()


def run() -> None:
    """Serve the API. Registered as the `egg-timer` console script."""
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
