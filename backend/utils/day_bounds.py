from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo


def utc_range_for_local_calendar_day(
    tz_name: str,
    *,
    now: datetime | None = None,
) -> tuple[datetime, datetime]:
    """Return [start, end) in UTC for the current calendar day in the given IANA timezone."""
    tz = ZoneInfo(tz_name)
    if now is None:
        local_now = datetime.now(tz)
    elif now.tzinfo is None:
        local_now = now.replace(tzinfo=timezone.utc).astimezone(tz)
    else:
        local_now = now.astimezone(tz)

    local_start = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
    local_end = local_start + timedelta(days=1)
    return local_start.astimezone(timezone.utc), local_end.astimezone(timezone.utc)


def format_in_timezone(dt: datetime, tz_name: str, fmt: str = "%d/%m/%Y %H:%M") -> str:
    tz = ZoneInfo(tz_name)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(tz).strftime(fmt)
