"""Small helpers shared across the package."""

import socket
import time
from typing import Callable, TypeVar

T = TypeVar("T")

# Hosts an ingest genuinely needs. Checked by TCP connect rather than ping,
# because ICMP is often blocked while HTTPS is fine.
_PROBE_HOSTS = [("www.youtube.com", 443), ("1.1.1.1", 53), ("8.8.8.8", 53)]


def network_up(timeout: float = 4.0) -> bool:
    """True if any probe host is reachable."""
    for host, port in _PROBE_HOSTS:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except OSError:
            continue
    return False


def wait_for_network(
    max_wait_seconds: float = 6 * 3600,
    poll_seconds: float = 30.0,
    on_wait: Callable[[str], None] | None = None,
) -> bool:
    """Block until the network comes back. Returns False if it never does.

    An overnight ingest should sit out a router reboot or an ISP blip rather
    than burning through the remaining playlist failing instantly. Six hours
    is deliberately generous: waiting costs nothing but time, whereas giving
    up costs a manual restart the next morning.
    """
    if network_up():
        return True

    waited = 0.0
    say = on_wait or (lambda m: print(f"[network] {m}"))
    say("connection lost — pausing until it returns")

    while waited < max_wait_seconds:
        time.sleep(poll_seconds)
        waited += poll_seconds
        if network_up():
            say(f"connection restored after {waited / 60:.0f} min — resuming")
            return True
        if waited % 300 == 0:
            say(f"still offline after {waited / 60:.0f} min, still waiting")

    say(f"gave up after {max_wait_seconds / 3600:.1f}h offline")
    return False


def with_retry(
    fn: Callable[[], T],
    attempts: int = 5,
    base_delay: float = 3.0,
    max_delay: float = 60.0,
    label: str = "operation",
    on_retry: Callable[[str], None] | None = None,
    is_rate_limit: Callable[[Exception], bool] | None = None,
    rate_limit_delay: float = 300.0,
) -> T:
    """Run fn, retrying transient failures with exponential backoff.

    For the network steps in a long ingest — a YouTube download or a Qdrant
    upsert. A flaky connection during a multi-hour unattended run should cost
    a few seconds of waiting, not the rest of the playlist.

    Both call sites are idempotent, so a retry can never double-apply.
    """
    delay = base_delay
    for attempt in range(1, attempts + 1):
        try:
            return fn()
        except Exception as exc:
            if attempt == attempts:
                raise
            # A dead connection is not a transient error to back off from —
            # it is something to sit and wait out. Burning the remaining
            # attempts against an offline router just wastes them.
            if not network_up():
                wait_for_network(on_wait=on_retry)

            # A rate limit is the opposite of a transient blip: retrying
            # quickly makes it worse. Back off hard, and grow the wait each
            # time, so a run that gets throttled slows down rather than dying.
            this_delay = delay
            if is_rate_limit and is_rate_limit(exc):
                this_delay = rate_limit_delay * attempt
                reason = f"rate limited — waiting {this_delay / 60:.0f} min"
            else:
                reason = f"retrying in {this_delay:.0f}s"

            message = (
                f"{label} failed (attempt {attempt}/{attempts}): "
                f"{type(exc).__name__}: {str(exc)[:90]} — {reason}"
            )
            if on_retry:
                on_retry(message)
            else:
                print(f"[retry] {message}")
            time.sleep(this_delay)
            delay = min(delay * 2, max_delay)
    raise RuntimeError("unreachable")
