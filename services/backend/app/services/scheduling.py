from __future__ import annotations

from datetime import datetime, timedelta, timezone


def build_appointment_payload(preferred_iso: str | None = None) -> dict[str, str]:
    start = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0) + timedelta(days=2)
    if preferred_iso:
        try:
            start = datetime.fromisoformat(preferred_iso)
        except ValueError:
            pass

    end = start + timedelta(minutes=30)
    return {
        'scheduled_at': start.isoformat(),
        'ends_at': end.isoformat(),
        'meeting_url': 'https://meet.google.com/placeholder-meet-link',
        'calendar_event_id': f'evt_{start.timestamp():.0f}',
    }
