"""Tests for the egg timer API."""

import time

import pytest
from fastapi.testclient import TestClient

from egg_timer.app import app, timer


@pytest.fixture(autouse=True)
def fresh_timer():
    """Each test starts from a stopped timer, so order never matters."""
    timer._started_at = None
    timer.duration_seconds = None
    yield
    timer._started_at = None
    timer.duration_seconds = None


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_status_when_never_started(client):
    response = client.get("/timer/status")

    assert response.status_code == 200
    assert response.json() == {
        "running": False,
        "elapsed_seconds": 0.0,
        "duration_seconds": None,
        "remaining_seconds": None,
        "finished": False,
    }


def test_start_as_stopwatch(client):
    response = client.post("/timer/start")

    assert response.status_code == 200
    body = response.json()
    assert body["running"] is True
    assert body["duration_seconds"] is None


def test_start_without_a_body_counts_up(client):
    client.post("/timer/start")
    time.sleep(0.01)

    elapsed = client.get("/timer/status").json()["elapsed_seconds"]
    assert elapsed > 0


def test_start_with_a_duration_counts_down(client):
    response = client.post("/timer/start", json={"duration_seconds": 300})

    body = response.json()
    assert body["duration_seconds"] == 300.0
    assert body["remaining_seconds"] == pytest.approx(300.0, abs=0.5)
    assert body["finished"] is False


def test_elapsed_never_passes_the_duration(client):
    client.post("/timer/start", json={"duration_seconds": 0.01})
    time.sleep(0.05)

    body = client.get("/timer/status").json()
    assert body["elapsed_seconds"] == 0.01
    assert body["remaining_seconds"] == 0.0
    assert body["finished"] is True
    assert body["running"] is True  # counting down to zero does not stop the timer


def test_stop_freezes_elapsed_time(client):
    client.post("/timer/start")
    time.sleep(0.01)
    stopped = client.post("/timer/stop").json()

    assert stopped["running"] is False
    assert stopped["elapsed_seconds"] > 0

    # Reading status twice must give the same frozen number.
    assert client.get("/timer/status").json()["elapsed_seconds"] == stopped[
        "elapsed_seconds"
    ]


def test_stop_when_not_running_is_conflict(client):
    response = client.post("/timer/stop")

    assert response.status_code == 409
    assert response.json()["detail"] == "Timer is not running"


def test_start_rejects_a_duration_that_is_too_long(client):
    response = client.post("/timer/start", json={"duration_seconds": 10**9})

    assert response.status_code == 422


@pytest.mark.parametrize("bad", [0, -5])
def test_start_rejects_a_duration_that_is_not_positive(client, bad):
    response = client.post("/timer/start", json={"duration_seconds": bad})

    assert response.status_code == 422
    assert client.get("/timer/status").json()["running"] is False


def test_restarting_replaces_the_previous_timer(client):
    client.post("/timer/start", json={"duration_seconds": 600})

    body = client.post("/timer/start", json={"duration_seconds": 60}).json()

    assert body["duration_seconds"] == 60.0
    assert body["remaining_seconds"] == pytest.approx(60.0, abs=0.5)
