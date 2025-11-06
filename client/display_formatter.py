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
        
        Design Decision: Privacy-focused display
        Why? - Users don't need to see who reserved slots
             - Only show Available/Unavailable status
             - Cleaner, more readable table
        
        Enhanced UI:
        - Fixed-width columns for proper alignment
        - Color-coded status (green=available, red=unavailable)
        - Clean ASCII borders
        """
        days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
        hours = list(range(9, 23))  # 9 to 22
        
        bold = DisplayFormatter.COLORS['bold']
        green = DisplayFormatter.COLORS['green']
        red = DisplayFormatter.COLORS['red']
        reset = DisplayFormatter.COLORS['reset']
        
        # Header
        print(f"\n{bold}{'='*100}{reset}")
        print(f"{bold}{'WEEKLY SCHEDULE':^100}{reset}")
        print(f"{bold}{'='*100}{reset}\n")
        
        # Top border - 7 days * 12 chars + time column 7 + borders
        print("┌───────┬────────────┬────────────┬────────────┬────────────┬────────────┬────────────┬────────────┐")
        
        # Header row
        print(f"│ Time  │    MON     │    TUE     │    WED     │    THU     │    FRI     │    SAT     │    SUN     │")
        
        # Separator after header
        print("├───────┼────────────┼────────────┼────────────┼────────────┼────────────┼────────────┼────────────┤")
        
        # Print each hour row
        for hour in hours:
            time_str = f"{hour:02d}:00"
            cells = [f" {time_str:<5} │"]
            
            for day in days:
                # Find slot for this day and hour
                day_schedule = schedule.get(day, [])
                slot = next((s for s in day_schedule if int(s['hour']) == hour), None)
                
                if slot and slot['available']:
                    # Available - 9 chars, need 12 total (3 spaces padding)
                    cells.append(f" {green}Available{reset}  │")
                elif slot and not slot['available']:
                    # Reserved - 8 chars, need 12 total (4 spaces padding)
                    cells.append(f"  {red}Reserved{reset}  │")
                else:
                    # No data - centered
                    cells.append(f"    ---     │")
            
            print("│" + "".join(cells))
        
        # Bottom border
        print("└───────┴────────────┴────────────┴────────────┴────────────┴────────────┴────────────┴────────────┘")
        print()
    
    @staticmethod
    def format_day_schedule(day: str, schedule: List[Dict]):
        """
        Format and print schedule for a specific day.
        
        Args:
            day: Day name (MON, TUE, etc.)
            schedule: List of time slots with availability
            
        Enhanced UI:
        - Privacy: Don't show other users' names
        - Clean table format
        - Color-coded status
        """
        bold = DisplayFormatter.COLORS['bold']
        green = DisplayFormatter.COLORS['green']
        red = DisplayFormatter.COLORS['red']
        cyan = DisplayFormatter.COLORS['cyan']
        reset = DisplayFormatter.COLORS['reset']
        
        print(f"\n{bold}{'='*50}{reset}")
        print(f"{bold}{f'SCHEDULE FOR {day}':^50}{reset}")
        print(f"{bold}{'='*50}{reset}\n")
        
        print("┌────────────────┬──────────────────┐")
        print("│  Time Slot     │      Status      │")
        print("├────────────────┼──────────────────┤")
        
        for slot in schedule:
            time_slot = slot['time_slot']
            
            if slot['available']:
                status = f"{green}✓ Available{reset}"
            else:
                status = f"{red}✗ Reserved{reset}"
            
            # Center-align for better readability
            print(f"│ {cyan}{time_slot:^14}{reset} │ {status:^16} │")
        
        print("└────────────────┴──────────────────┘")
        print()
    
    @staticmethod
    def format_reservations(reservations: List[Dict]):
        """
        Format and print user's own reservations.
        
        Args:
            reservations: List of reservation dicts
            
        Enhanced UI:
        - Shows only user's own reservations
        - Clean, readable format
        - Color highlights
        """
        bold = DisplayFormatter.COLORS['bold']
        cyan = DisplayFormatter.COLORS['cyan']
        green = DisplayFormatter.COLORS['green']
        reset = DisplayFormatter.COLORS['reset']
        
        if not reservations:
            DisplayFormatter.info("You have no reservations.")
            return
        
        print(f"\n{bold}{'='*50}{reset}")
        print(f"{bold}{'YOUR RESERVATIONS':^50}{reset}")
        print(f"{bold}{'='*50}{reset}\n")
        
        print("┌──────────┬────────────────────────┐")
        print("│   Day    │      Time Slot         │")
        print("├──────────┼────────────────────────┤")
        
        for res in reservations:
            day = res['day']
            time_slot = res['time_slot']
            print(f"│ {cyan}{day:^8}{reset} │ {green}{time_slot:^22}{reset} │")
        
        print("└──────────┴────────────────────────┘")
        print(f"\n{bold}Total: {len(reservations)} reservation(s){reset}\n")
    
    @staticmethod
    def print_help():
        """Print available commands with enhanced formatting."""
        bold = DisplayFormatter.COLORS['bold']
        cyan = DisplayFormatter.COLORS['cyan']
        green = DisplayFormatter.COLORS['green']
        yellow = DisplayFormatter.COLORS['yellow']
        reset = DisplayFormatter.COLORS['reset']
        
        print(f"\n{bold}{'='*70}{reset}")
        print(f"{bold}{'AVAILABLE COMMANDS':^70}{reset}")
        print(f"{bold}{'='*70}{reset}\n")
        
        # Group commands by category
        auth_cmds = [
            ("login <username> <password>", "Login to the system", "login user1 1")
        ]
        
        view_cmds = [
            ("show_list", "Show weekly schedule for all days", "show_list"),
            ("show_day <DAY>", "Show schedule for specific day", "show_day WED"),
            ("show_my_res", "Show your reservations", "show_my_res")
        ]
        
        manage_cmds = [
            ("make_res <DAY> <HOUR>", "Make a new reservation", "make_res WED 14"),
            ("cancel_res <DAY>", "Cancel your reservation", "cancel_res MON")
        ]
        
        other_cmds = [
            ("help", "Show this help message", "help"),
            ("exit", "Exit the program", "exit")
        ]
        
        # Print Authentication
        print(f"{yellow}▶ Authentication:{reset}")
        for cmd, desc, example in auth_cmds:
            print(f"  {cyan}{cmd:<30}{reset} {desc}")
            print(f"    {green}Example: {example}{reset}\n")
        
        # Print View Commands
        print(f"{yellow}▶ View Schedule:{reset}")
        for cmd, desc, example in view_cmds:
            print(f"  {cyan}{cmd:<30}{reset} {desc}")
            print(f"    {green}Example: {example}{reset}\n")
        
        # Print Management Commands
        print(f"{yellow}▶ Manage Reservations:{reset}")
        for cmd, desc, example in manage_cmds:
            print(f"  {cyan}{cmd:<30}{reset} {desc}")
            print(f"    {green}Example: {example}{reset}\n")
        
        # Print Other Commands
        print(f"{yellow}▶ Other:{reset}")
        for cmd, desc, example in other_cmds:
            print(f"  {cyan}{cmd:<30}{reset} {desc}")
            print(f"    {green}Example: {example}{reset}\n")
        
        print(f"{bold}{'─'*70}{reset}")
        print(f"{bold}Note:{reset} Days are: MON, TUE, WED, THU, FRI, SAT, SUN")
        print(f"{bold}Note:{reset} Hours are: 9-22 (e.g., 9 = 09:00-10:00, 14 = 14:00-15:00)")
        print(f"{bold}{'─'*70}{reset}\n")
