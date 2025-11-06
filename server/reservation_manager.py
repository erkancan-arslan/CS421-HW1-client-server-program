"""
ReservationManager - Business logic for tennis court reservations

Design Decision: Separate business rules from data storage
Why? - Business logic changes more often than storage
     - Can test rules without database/storage
     - Single Responsibility Principle
     
Teaching Point: This is the "domain layer" in clean architecture
It contains the RULES of the system, not how data is stored or displayed
"""

from typing import Optional, Tuple, Any
from server.schedule_store import ScheduleStore
from server.models import Reservation, is_valid_day, is_valid_hour, DAYS


class ReservationError(Exception):
    """
    Custom exception for reservation business rule violations.
    
    Design Decision: Create custom exception class
    Why? - Distinguish business errors from system errors
         - Can catch specifically: except ReservationError
         - Can add error codes/types later
    
    Teaching Point: Exception hierarchy is powerful
    - Exception (base)
      |- ReservationError (our custom)
         |- SlotTakenError (could add)
         |- DailyLimitError (could add)
    """
    pass


class ReservationManager:
    """
    Manages reservation business logic and constraints.
    
    Design Decision: Depends on ScheduleStore (dependency injection)
    Why? - Separation of concerns
         - Can swap storage implementation
         - Easy to mock for testing
    
    Business Rules Enforced:
    1. One reservation per user per day
    2. No double-booking of slots
    3. Valid day/hour only
    """
    
    def __init__(self, schedule_store: ScheduleStore):
        """
        Initialize reservation manager.
        
        Args:
            schedule_store: Data storage layer
        
        Design Decision: Pass store as parameter (dependency injection)
        Why? - Flexible: can use different store implementations
             - Testable: can inject mock store
             - Follows SOLID principles (Dependency Inversion)
        
        Alternative (rejected): Create store internally
        Why not? - Hard to test
                 - Tight coupling
                 - Less flexible
        """
        self.store = schedule_store
    
    def make_reservation(
        self,
        username: str,
        day: str,
        hour: int
    ) -> Tuple[bool, str]:
        """
        Attempt to make a reservation.
        
        Args:
            username: User making the reservation
            day: Day of week (MON, TUE, etc.)
            hour: Hour (9-22)
        
        Returns:
            Tuple of (success: bool, message: str)
        
        Design Decision: Return (bool, str) instead of raising exception
        Why? - Business rule violations are expected scenarios
             - Caller can easily handle success/failure
             - Message provides user-friendly feedback
        
        Alternative: Raise ReservationError with message
        Why not chosen? - Would require try/catch everywhere
                        - Success case is common, not exceptional
        
        Teaching Point: When to use exceptions vs return values?
        - Use exceptions: Unexpected errors (file I/O, network)
        - Use return values: Expected business outcomes (validation)
        """
        # Validate input format
        day = day.upper()  # Accept lowercase input
        
        if not is_valid_day(day):
            return False, f"Invalid day: {day}. Must be MON, TUE, WED, THU, FRI, SAT, or SUN."
        
        if not is_valid_hour(hour):
            return False, f"Invalid hour: {hour}. Must be between 9 and 22 (09:00-23:00)."
        
        # Business Rule 1: Check if user already has reservation that day
        existing = self.store.get_user_reservation_for_day(username, day)
        if existing:
            return False, (
                f"You already have a reservation on {day} at {existing.hour}:00. "
                f"You can only make one reservation per day."
            )
        
        # Business Rule 2: Check if slot is available
        if not self.store.is_slot_available(day, hour):
            occupant = self.store.get_slot(day, hour)
            return False, (
                f"Slot {day} {hour}:00-{hour+1}:00 is already reserved by {occupant}."
            )
        
        # All checks passed - make the reservation
        success = self.store.reserve_slot(day, hour, username)
        
        if success:
            return True, f"Reservation successful: {day} {hour}:00-{hour+1}:00"
        else:
            # This shouldn't happen (we checked availability)
            return False, "Unexpected error: Could not complete reservation."
    
    def cancel_reservation(
        self,
        username: str,
        day: str
    ) -> Tuple[bool, str]:
        """
        Cancel a user's reservation for a specific day.
        
        Args:
            username: User canceling the reservation
            day: Day of the reservation
        
        Returns:
            Tuple of (success: bool, message: str)
        
        Design Decision: Cancel by day (not hour)
        Why? - Requirement: "cancel_res [DAY_NAME]"
             - User can only have one per day anyway
             - Simpler interface
        """
        day = day.upper()
        
        if not is_valid_day(day):
            return False, f"Invalid day: {day}"
        
        # Find user's reservation for that day
        reservation = self.store.get_user_reservation_for_day(username, day)
        
        if reservation is None:
            return False, f"You have no reservation on {day}."
        
        # Cancel it
        success = self.store.cancel_reservation(day, reservation.hour)
        
        if success:
            return True, f"Cancelled reservation: {day} {reservation.hour}:00-{reservation.hour+1}:00"
        else:
            return False, "Unexpected error: Could not cancel reservation."
    
    def get_user_reservations(self, username: str) -> list[Reservation]:
        """
        Get all reservations for a user.
        
        Args:
            username: User to look up
        
        Returns:
            List of Reservation objects
        
        Design Decision: Simple pass-through to store
        Why? - No business logic needed here
             - Keep interface consistent (go through manager)
             - Could add filtering/sorting later
        """
        return self.store.get_user_reservations(username)
    
    def get_weekly_schedule(self) -> dict:
        """
        Get the full weekly schedule.
        
        Returns:
            Dict mapping days to schedules
        
        Teaching Point: Manager layer can transform data
        Could add: - Highlighting of prime-time slots
                  - Usage statistics
                  - Recommendations
        For now, just pass through from store.
        """
        return self.store.get_weekly_schedule()
    
    def get_day_schedule(self, day: str) -> Tuple[bool, Any]:
        """
        Get schedule for a specific day.
        
        Args:
            day: Day name
        
        Returns:
            Tuple of (success: bool, schedule or error_message)
        
        Design Decision: Validate day and return structured response
        Why? - Consistent error handling pattern
             - Caller knows if request was valid
        """
        day = day.upper()
        
        if not is_valid_day(day):
            return False, f"Invalid day: {day}"
        
        schedule = self.store.get_day_schedule(day)
        return True, schedule
    
    def reset_weekly_schedule(self):
        """
        Reset all reservations (weekly refresh).
        
        Teaching Point: This implements requirement
        "at the beginning of each week, the server refreshes the schedule"
        
        In production, this would be a scheduled task (cron job)
        For this assignment, can be manual or automatic
        """
        self.store.reset_schedule()
