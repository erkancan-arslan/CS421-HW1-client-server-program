"""
CommandParser - Parse console commands

Design Decision: Simple string parsing
Why? - Commands have simple structure
     - No complex grammar needed
     - Easy to understand and debug
"""

from typing import Optional, Tuple, List


class Command:
    """
    Represents a parsed command.
    
    Design Decision: Use dataclass-like object
    Why? - Clear structure
         - Type hints
         - Easy to pass around
    """
    
    def __init__(self, name: str, args: List[str]):
        self.name = name
        self.args = args
    
    def __repr__(self):
        return f"Command({self.name}, {self.args})"


class CommandParser:
    """
    Parses user input into Command objects.
    
    Design Decision: Static methods (no state)
    Why? - Pure function (input -> output)
         - Thread-safe
         - Simple to test
    """
    
    @staticmethod
    def parse(user_input: str) -> Optional[Command]:
        """
        Parse user input into a Command.
        
        Args:
            user_input: Raw string from user
        
        Returns:
            Command object or None if empty/invalid
        
        Design Decision: Return None for invalid (not raise exception)
        Why? - Invalid input is expected (user typos)
             - Caller can handle gracefully
             - Print error message at call site
        
        Examples:
            "login user1 1" -> Command("login", ["user1", "1"])
            "show_list" -> Command("show_list", [])
            "make_res WED 14" -> Command("make_res", ["WED", "14"])
        """
        # Strip and check for empty
        user_input = user_input.strip()
        if not user_input:
            return None
        
        # Split by whitespace
        parts = user_input.split()
        
        if not parts:
            return None
        
        command_name = parts[0].lower()
        args = parts[1:]
        
        # Validate that it's a known command
        valid_commands = [
            'help', 'exit', 'quit', 'login', 'show_list', 
            'show_day', 'show_my_res', 'make_res', 'cancel_res'
        ]
        
        if command_name not in valid_commands:
            return None
        
        return Command(command_name, args)
    
    @staticmethod
    def validate_login(cmd: Command) -> Tuple[bool, Optional[Tuple[str, str]]]:
        """
        Validate login command arguments.
        
        Returns:
            Tuple of (valid, (username, password) or None)
        
        Teaching Point: Input validation at parse time
        Why? - Fail fast
             - Clear error messages
             - Separation from business logic
        """
        if len(cmd.args) != 2:
            return False, None
        
        username, password = cmd.args[0], cmd.args[1]
        return True, (username, password)
    
    @staticmethod
    def validate_show_day(cmd: Command) -> Tuple[bool, Optional[str]]:
        """
        Validate show_day command.
        
        Returns:
            Tuple of (valid, day_name or None)
        """
        if len(cmd.args) != 1:
            return False, None
        
        day = cmd.args[0].upper()
        
        valid_days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
        if day not in valid_days:
            return False, None
        
        return True, day
    
    @staticmethod
    def validate_make_res(cmd: Command) -> Tuple[bool, Optional[Tuple[str, int]]]:
        """
        Validate make_res command.
        
        Returns:
            Tuple of (valid, (day, hour) or None)
        
        Examples:
            make_res WED 14 -> (True, ("WED", 14))
            make_res MON nine -> (False, None)
        """
        if len(cmd.args) != 2:
            return False, None
        
        day = cmd.args[0].upper()
        
        valid_days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
        if day not in valid_days:
            return False, None
        
        try:
            hour = int(cmd.args[1])
        except ValueError:
            return False, None
        
        # Basic range check (server will do full validation)
        if not (0 <= hour <= 23):
            return False, None
        
        return True, (day, hour)
    
    @staticmethod
    def validate_cancel_res(cmd: Command) -> Tuple[bool, Optional[str]]:
        """
        Validate cancel_res command.
        
        Returns:
            Tuple of (valid, day_name or None)
        """
        if len(cmd.args) != 1:
            return False, None
        
        day = cmd.args[0].upper()
        
        valid_days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
        if day not in valid_days:
            return False, None
        
        return True, day
