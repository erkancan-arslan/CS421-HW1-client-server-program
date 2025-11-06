"""
Data models for the Tennis Court Reservation System

"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Reservation:
    """
    Represents a single reservation.
    
    Design Decision: Store day and hour separately rather than datetime
    Why? - Simpler weekly schedule management (no year/date complications)
         - Direct mapping to user commands (e.g., "WED 14")
         - Easier to display and query
    """
    username: str
    day: str        # MON, TUE, WED, THU, FRI, SAT, SUN
    hour: int       # 9-22 (representing 09:00-10:00, ..., 22:00-23:00)
    
    def __repr__(self):
        return f"Reservation({self.username}, {self.day} {self.hour}:00-{self.hour+1}:00)"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "username": self.username,
            "day": self.day,
            "hour": self.hour,
            "time_slot": f"{self.hour:02d}:00-{self.hour+1:02d}:00"
        }


@dataclass
class Session:
    """
    Represents an active user session.
    
    Design Decision: Include login_time for potential session expiry
    Why? - Could add timeout feature later
         - Useful for debugging/logging
         - Minimal overhead
    """
    username: str
    token: str
    login_time: datetime
    
    def to_dict(self):
        return {
            "username": self.username,
            "token": self.token,
            "login_time": self.login_time.isoformat()
        }


# Constants - Design Decision: Centralize configuration
# Why? - Single source of truth
#      - Easy to modify if requirements change
#      - Clear documentation of constraints

DAYS = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
HOURS = list(range(9, 23))  # 9 to 22 inclusive (09:00-23:00)

# Design Decision: Hardcode users as per specification
# Why? - Requirements explicitly state 10 predefined users
#      - No user registration needed
#      - Simple for teaching purposes
PREDEFINED_USERS = {
    f"user{i}": str(i) for i in range(1, 11)
}

def is_valid_day(day: str) -> bool:
    """Validate day name"""
    return day.upper() in DAYS

def is_valid_hour(hour: int) -> bool:
    """Validate hour is in allowed range"""
    return hour in HOURS

def format_time_slot(hour: int) -> str:
    """Format hour as time slot string (e.g., '14:00-15:00')"""
    return f"{hour:02d}:00-{hour+1:02d}:00"
