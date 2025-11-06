"""
DisplayFormatter - Format output for console display

Design Decision: Separate presentation from logic
Why? - Easy to change display format
     - Testable independently
     - Clean separation of concerns
"""

from typing import List, Dict, Any


class DisplayFormatter:
    """
    Formats data for console display.
    
    Design Decision: Static methods (no state needed)
    Why? - Pure functions (input -> output)
         - No configuration needed
         - Simple to use
    """
    
    # ANSI color codes for pretty output
    COLORS = {
        'green': '\033[92m',
        'red': '\033[91m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'cyan': '\033[96m',
        'reset': '\033[0m',
        'bold': '\033[1m'
    }
    
    @staticmethod
    def success(message: str):
        """Print success message in green."""
        color = DisplayFormatter.COLORS['green']
        reset = DisplayFormatter.COLORS['reset']
        print(f"{color}✓ {message}{reset}")
    
    @staticmethod
    def error(message: str):
        """Print error message in red."""
        color = DisplayFormatter.COLORS['red']
        reset = DisplayFormatter.COLORS['reset']
        print(f"{color}✗ {message}{reset}")
    
    @staticmethod
    def info(message: str):
        """Print info message in blue."""
        color = DisplayFormatter.COLORS['blue']
        reset = DisplayFormatter.COLORS['reset']
        print(f"{color}ℹ {message}{reset}")
    
    @staticmethod
    def warning(message: str):
        """Print warning message in yellow."""
        color = DisplayFormatter.COLORS['yellow']
        reset = DisplayFormatter.COLORS['reset']
        print(f"{color}⚠ {message}{reset}")
    
    @staticmethod
    def format_weekly_schedule(schedule: Dict[str, List[Dict]]):
        """
        Format and print weekly schedule as a table.
        
        Design Decision: ASCII table format
        Why? - Clear visual representation
             - Works in any terminal
             - No external dependencies
        
        Format:
          ┌──────┬──────────────┬──────────────┬─────
          │ Time │ MON          │ TUE          │ WED ...
          ├──────┼──────────────┼──────────────┼─────
          │ 09:00│ Available    │ Available    │ user1
          │ 10:00│ user2        │ Available    │ Available
          ...
        """
        days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
        hours = list(range(9, 23))  # 9 to 22
        
        bold = DisplayFormatter.COLORS['bold']
        green = DisplayFormatter.COLORS['green']
        red = DisplayFormatter.COLORS['red']
        reset = DisplayFormatter.COLORS['reset']
        
        # Header
        print(f"\n{bold}Weekly Schedule:{reset}\n")
        
        # Print header row
        header = f"│ {'Time':<6} │"
        for day in days:
            header += f" {day:<12} │"
        
        separator = "├─" + "─" * 8 + "┼"
        for _ in days:
            separator += "─" * 14 + "┼"
        
        top_border = "┌─" + "─" * 8 + "┬"
        for _ in days:
            top_border += "─" * 14 + "┬"
        top_border = top_border[:-1] + "┐"
        
        print(top_border)
        print(header)
        print(separator)
        
        # Print each hour row
        for hour in hours:
            time_str = f"{hour:02d}:00"
            row = f"│ {time_str:<6} │"
            
            for day in days:
                # Find slot for this day and hour
                day_schedule = schedule.get(day, [])
                slot = next((s for s in day_schedule if s['hour'] == hour), None)
                
                if slot:
                    if slot['available']:
                        status = f"{green}Available{reset}"
                    else:
                        status = f"{red}{slot['reserved_by']}{reset}"
                else:
                    status = "N/A"
                
                row += f" {status:<12} │"
            
            print(row)
        
        # Bottom border
        bottom_border = "└─" + "─" * 8 + "┴"
        for _ in days:
            bottom_border += "─" * 14 + "┴"
        bottom_border = bottom_border[:-1] + "┘"
        print(bottom_border)
        print()
    
    @staticmethod
    def format_day_schedule(day: str, schedule: List[Dict]):
        """
        Format and print schedule for a specific day.
        
        Args:
            day: Day name (MON, TUE, etc.)
            schedule: List of time slots with availability
        """
        bold = DisplayFormatter.COLORS['bold']
        green = DisplayFormatter.COLORS['green']
        red = DisplayFormatter.COLORS['red']
        reset = DisplayFormatter.COLORS['reset']
        
        print(f"\n{bold}Schedule for {day}:{reset}\n")
        print("┌──────────────┬─────────────────┬─────────────┐")
        print("│ Time Slot    │ Status          │ Reserved By │")
        print("├──────────────┼─────────────────┼─────────────┤")
        
        for slot in schedule:
            time_slot = slot['time_slot']
            
            if slot['available']:
                status = f"{green}Available{reset}"
                reserved_by = "-"
            else:
                status = f"{red}Reserved{reset}"
                reserved_by = slot['reserved_by']
            
            print(f"│ {time_slot:<12} │ {status:<15} │ {reserved_by:<11} │")
        
        print("└──────────────┴─────────────────┴─────────────┘")
        print()
    
    @staticmethod
    def format_reservations(reservations: List[Dict]):
        """
        Format and print user's reservations.
        
        Args:
            reservations: List of reservation dicts
        """
        bold = DisplayFormatter.COLORS['bold']
        cyan = DisplayFormatter.COLORS['cyan']
        reset = DisplayFormatter.COLORS['reset']
        
        if not reservations:
            DisplayFormatter.info("You have no reservations.")
            return
        
        print(f"\n{bold}Your Reservations:{reset}\n")
        print("┌─────┬──────────────┬──────────┐")
        print("│ Day │ Time Slot    │ Username │")
        print("├─────┼──────────────┼──────────┤")
        
        for res in reservations:
            day = res['day']
            time_slot = res['time_slot']
            username = res['username']
            print(f"│ {cyan}{day:<3}{reset} │ {time_slot:<12} │ {username:<8} │")
        
        print("└─────┴──────────────┴──────────┘")
        print()
    
    @staticmethod
    def print_help():
        """Print available commands."""
        bold = DisplayFormatter.COLORS['bold']
        cyan = DisplayFormatter.COLORS['cyan']
        reset = DisplayFormatter.COLORS['reset']
        
        print(f"\n{bold}Available Commands:{reset}\n")
        
        commands = [
            ("login <username> <password>", "Login to the system"),
            ("show_list", "Show weekly schedule"),
            ("show_day <DAY>", "Show schedule for specific day (MON, TUE, etc.)"),
            ("show_my_res", "Show your reservations"),
            ("make_res <DAY> <HOUR>", "Make a reservation (e.g., make_res WED 14)"),
            ("cancel_res <DAY>", "Cancel your reservation for a day"),
            ("help", "Show this help message"),
            ("exit", "Exit the program"),
        ]
        
        for cmd, desc in commands:
            print(f"  {cyan}{cmd:<30}{reset} - {desc}")
        
        print()
