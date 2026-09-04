import uuid
from typing import List

def parse_time(time_str: str) -> int:
    """Parse 'HH:MM' to integer hour."""
    if not time_str:
        return 0
    return int(time_str.split(":")[0])

def format_time(hour: int) -> str:
    """Format hour to 'HH:00'."""
    return f"{hour:02d}:00"

def generate_run_id() -> str:
    """Generate a UUID4 based run ID."""
    return str(uuid.uuid4())

def hours_overlap(start1: int, end1: int, start2: int, end2: int) -> bool:
    """Check if two hour ranges overlap."""
    return max(start1, start2) < min(end1, end2)

def get_hour_range(start_str: str, end_str: str) -> List[int]:
    """Get list of hours between start_str and end_str."""
    if not start_str or not end_str:
        return list(range(24))
    start_h = parse_time(start_str)
    end_h = parse_time(end_str)
    return list(range(start_h, end_h))
