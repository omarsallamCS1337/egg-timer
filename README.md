# Egg Timer

A small FastAPI service that keeps one in-memory timer. Handy for an egg,
or for anything else you want to watch the clock on.

State lives in the process, so restarting the app clears the timer.

## Requirements

- [uv](https://docs.astral.sh/uv/)
- Python 3.10+ (uv will fetch one if you don't have it)

## Setup

```bash
uv sync
```

## Run

```bash
uv run egg-timer
```

Or directly:

```bash
uv run uvicorn egg_timer.app:app --reload
```

The API is then on http://127.0.0.1:8000, with interactive docs at
http://127.0.0.1:8000/docs.

## Endpoints

| Method | Path             | Purpose                                            |
| ------ | ---------------- | -------------------------------------------------- |
| POST   | `/timer/start`   | Start. Optional `duration_seconds` to count down.  |
| POST   | `/timer/stop`    | Stop. `409` if it wasn't running.                  |
| GET    | `/timer/status`  | Running flag, plus elapsed and remaining seconds.  |

```bash
# Count up from zero, stopwatch style.
curl -X POST http://127.0.0.1:8000/timer/start

# Count down from three minutes — a soft-boiled egg.
curl -X POST http://127.0.0.1:8000/timer/start \
  -H 'Content-Type: application/json' \
  -d '{"duration_seconds": 180}'

curl http://127.0.0.1:8000/timer/status
curl -X POST http://127.0.0.1:8000/timer/stop
```

A status response looks like this:

```json
{
  "running": true,
  "elapsed_seconds": 12.5,
  "duration_seconds": 180.0,
  "remaining_seconds": 167.5,
  "finished": false
}
```

Without a duration, `duration_seconds` and `remaining_seconds` are `null` and
`elapsed_seconds` keeps climbing until you stop it.

## Tests

```bash
uv run pytest
```

## Build

```bash
uv build --wheel
```

Wheels land in `dist/`.
