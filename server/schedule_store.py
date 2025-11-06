"""
ScheduleStore - Data persistence layer for tennis court reservations

Design Decision: Single Responsibility Principle
This module ONLY handles data storage/retrieval, NO business logic
Why? - Testable in isolation
     - Easy to swap storage backend (file, database, etc.)
     - Clear separation of concerns
"""

import json
from typing import Optional, Dict, List
from server.models import Reservation, DAYS, HOURS


class ScheduleStore:
    """
    Manages the tennis court schedule data.
    
    Design Decision: Use nested dictionary for O(1) lookups
    Structure: {day: {hour: username or None}}
    
    Why this structure?
    - Fast lookup: schedule[day][hour] is O(1)
    - Easy iteration: Can list all slots or filter by day
    - Simple state: None = available, username = occupied
    """
    
    def __init__(self, persistence_file: Optional[str] = None):
        """
        Initialize the schedule store.
        
        Args:
            persistence_file: Optional file path for saving/loading schedule
        
        Design Decision: Optional file persistence
        Why? - Can run without file for testing
             - Production can enable persistence
        """
        self.persistence_file = persistence_file
        self.schedule: Dict[str, Dict[int, Optional[str]]] = {}
        self._initialize_schedule()
        
        # Try to load from file if it exists
        if self.persistence_file:
            self._load_from_file()
    
    def _initialize_schedule(self):
        """
        Create empty schedule with all slots available.
        
        Design Decision: Initialize all slots explicitly
        Why? - Easier to check availability (check None vs KeyError)
             - Clear state representation
             - Simpler iteration over all slots
        """
        for day in DAYS:
            self.schedule[day] = {hour: None for hour in HOURS}
    
    def reset_schedule(self):
        """
        Reset all reservations (for weekly refresh).
        
        Teaching Point: This implements the requirement that
        "at the beginning of each week, the server refreshes the schedule"
        """
        self._initialize_schedule()
        if self.persistence_file:
            self._save_to_file()
    
    def get_slot(self, day: str, hour: int) -> Optional[str]:
        """
        Get the username occupying a slot, or None if available.
        
        Args:
            day: Day name (MON, TUE, etc.)
            hour: Hour (9-22)
        
        Returns:
            Username if slot is reserved, None if available
        
        Design Decision: Return None for available (not False or "")
        Why? - None is Pythonic for "absence of value"
             - Truthy/falsy checks work correctly
             - Type hint Optional[str] is clear
        """
        return self.schedule.get(day, {}).get(hour)
    
    def is_slot_available(self, day: str, hour: int) -> bool:
        """Check if a slot is available for reservation."""
        return self.get_slot(day, hour) is None
    
    def reserve_slot(self, day: str, hour: int, username: str) -> bool:
        """
        Reserve a slot for a user.
        
        Args:
            day: Day name
            hour: Hour
            username: User making the reservation
        
        Returns:
            True if successfully reserved, False if already taken
        
        Design Decision: Return boolean for success/failure
        Why? - Caller can decide how to handle failure
             - No exceptions for business logic (reserved vs available)
             - Exceptions only for actual errors (invalid input)
        """
        if not self.is_slot_available(day, hour):
            return False
        
        self.schedule[day][hour] = username
        if self.persistence_file:
            self._save_to_file()
        return True
    
    def cancel_reservation(self, day: str, hour: int) -> bool:
        """
        Cancel a reservation.
        
        Returns:
            True if reservation was cancelled, False if slot was already empty
        """
        if self.is_slot_available(day, hour):
            return False
        
        self.schedule[day][hour] = None
        if self.persistence_file:
            self._save_to_file()
        return True
    
    def get_day_schedule(self, day: str) -> List[Dict]:
        """
        Get all slots for a specific day.
        
        Returns:
            List of dicts with slot info: {hour, time_slot, status, username}
        
        Design Decision: Return structured data, not strings
        Why? - Caller can format as needed
             - Easier to test
             - More flexible for different display formats
        """
        result = []
        for hour in HOURS:
            username = self.get_slot(day, hour)
            result.append({
                "hour": hour,
                "time_slot": f"{hour:02d}:00-{hour+1:02d}:00",
                "available": username is None,
                "reserved_by": username
            })
        return result
    
    def get_weekly_schedule(self) -> Dict[str, List[Dict]]:
        """
        Get the entire weekly schedule.
        
        Returns:
            Dict mapping day names to their schedules
        """
        return {day: self.get_day_schedule(day) for day in DAYS}
    
    def get_user_reservations(self, username: str) -> List[Reservation]:
        """
        Get all reservations for a specific user.
        
        Returns:
            List of Reservation objects
        
        Design Decision: Return Reservation objects, not dicts
        Why? - Type safety
             - Consistent with our data model
             - Can use Reservation methods
        """
        reservations = []
        for day in DAYS:
            for hour in HOURS:
                if self.get_slot(day, hour) == username:
                    reservations.append(Reservation(username, day, hour))
        return reservations
    
    def get_user_reservation_for_day(self, username: str, day: str) -> Optional[Reservation]:
        """
        Check if user has a reservation on a specific day.
        
        Returns:
            Reservation object if exists, None otherwise
        
        Teaching Point: This implements the constraint
        "a user can make at most one reservation per day"
        """
        for hour in HOURS:
            if self.get_slot(day, hour) == username:
                return Reservation(username, day, hour)
        return None
    
    def _save_to_file(self):
        """
        Save schedule to file.
        
        Design Decision: Use JSON for human-readability
        Why? - Easy to inspect/debug
             - Standard format
             - Built-in Python support
        Alternative: Pickle - faster but binary, not readable
        """
        if not self.persistence_file:
            return
        
        try:
            with open(self.persistence_file, 'w') as f:
                json.dump(self.schedule, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save schedule to file: {e}")
    
    def _load_from_file(self):
        """Load schedule from file if it exists."""
        if not self.persistence_file:
            return
        
        try:
            with open(self.persistence_file, 'r') as f:
                loaded = json.load(f)
                # Validate loaded data structure
                for day in DAYS:
                    if day in loaded:
                        for hour in HOURS:
                            if str(hour) in loaded[day]:  # JSON keys are strings
                                self.schedule[day][hour] = loaded[day][str(hour)]
        except FileNotFoundError:
            # First run, no file yet - that's fine
            pass
        except Exception as e:
            print(f"Warning: Could not load schedule from file: {e}")
            print("Starting with empty schedule.")
