"""
Client - Main client program for Tennis Court Reservation System

Design Decision: REPL (Read-Eval-Print Loop)
Why? - Interactive command-line interface
     - Standard pattern for console apps
     - Easy to use and understand
"""

import sys
from client.http_client import HTTPClient
from client.session_manager import SessionManager
from client.command_parser import CommandParser
from client.display_formatter import DisplayFormatter


class TennisCourtClient:
    """
    Main client application.
    
    Design Decision: Single class to orchestrate all components
    Why? - Clear entry point
         - Manages dependencies
         - Controls application flow
    """
    
    def __init__(self, host: str, port: int):
        """
        Initialize client.
        
        Args:
            host: Server hostname/IP
            port: Server port
        """
        self.http_client = HTTPClient(host, port)
        self.session = SessionManager()
        self.running = True
        
        print("=" * 60)
        print("Tennis Court Reservation System - Client")
        print("=" * 60)
        DisplayFormatter.info(f"Connected to server at {host}:{port}")
        DisplayFormatter.warning("Type 'help' for available commands")
        print()
    
    def run(self):
        """
        Main REPL loop.
        
        Teaching Point: REPL pattern
        1. Read user input
        2. Evaluate (parse and execute)
        3. Print result
        4. Loop
        
        Design Decision: Continuous loop until exit
        Why? - Keep session alive
             - Multiple operations without reconnecting
             - Standard console app behavior
        """
        while self.running:
            try:
                # Show prompt with username if logged in
                if self.session.is_logged_in():
                    prompt = f"{self.session.get_username()}> "
                else:
                    prompt = "guest> "
                
                # Read input
                user_input = input(prompt).strip()
                
                if not user_input:
                    continue
                
                # Parse command
                cmd = CommandParser.parse(user_input)
                if cmd is None:
                    DisplayFormatter.error("Invalid command")
                    continue
                
                # Execute command
                self.execute_command(cmd)
                
            except KeyboardInterrupt:
                print("\n")
                DisplayFormatter.info("Use 'exit' to quit")
            except EOFError:
                print()
                break
            except Exception as e:
                DisplayFormatter.error(f"Unexpected error: {e}")
        
        print("\nGoodbye!")
    
    def execute_command(self, cmd):
        """
        Execute a parsed command.
        
        Design Decision: Command dispatcher pattern
        Why? - Clean separation of command logic
             - Easy to add new commands
             - Clear control flow
        
        Teaching Point: Dictionary dispatch vs if-elif
        Alternative: command_map = {"login": self.handle_login, ...}
        Current: if-elif chain
        Why current? - More explicit, easier to follow for learning
        """
        
        # Commands that don't require login
        if cmd.name == "help":
            DisplayFormatter.print_help()
            return
        
        elif cmd.name == "exit" or cmd.name == "quit":
            self.running = False
            return
        
        elif cmd.name == "login":
            self.handle_login(cmd)
            return
        
        # Commands that require login
        if not self.session.require_login():
            return
        
        if cmd.name == "show_list":
            self.handle_show_list(cmd)
        
        elif cmd.name == "show_day":
            self.handle_show_day(cmd)
        
        elif cmd.name == "show_my_res":
            self.handle_show_my_res(cmd)
        
        elif cmd.name == "make_res":
            self.handle_make_res(cmd)
        
        elif cmd.name == "cancel_res":
            self.handle_cancel_res(cmd)
        
        else:
            DisplayFormatter.error(f"Unknown command: {cmd.name}")
            DisplayFormatter.info("Type 'help' for available commands")
    
    # ========== Command Handlers ==========
    
    def handle_login(self, cmd):
        """Handle login command."""
        valid, params = CommandParser.validate_login(cmd)
        
        if not valid or params is None:
            DisplayFormatter.error("Usage: login <username> <password>")
            return
        
        username, password = params
        
        DisplayFormatter.info(f"Logging in as {username}...")
        success, message, token = self.http_client.login(username, password)
        
        if success and token:
            self.session.login(username, token)
            DisplayFormatter.success(message)
        else:
            DisplayFormatter.error(message)
    
    def handle_show_list(self, cmd):
        """Handle show_list command (weekly schedule)."""
        token = self.session.get_token()
        if not token:
            return
        
        success, message, schedule = self.http_client.get_weekly_schedule(token)
        
        if success and schedule:
            DisplayFormatter.format_weekly_schedule(schedule)
        else:
            DisplayFormatter.error(message)
    
    def handle_show_day(self, cmd):
        """Handle show_day command."""
        valid, day = CommandParser.validate_show_day(cmd)
        
        if not valid or day is None:
            DisplayFormatter.error("Usage: show_day <DAY>")
            DisplayFormatter.info("Valid days: MON, TUE, WED, THU, FRI, SAT, SUN")
            return
        
        token = self.session.get_token()
        if not token:
            return
        
        success, message, schedule = self.http_client.get_day_schedule(token, day)
        
        if success and schedule:
            DisplayFormatter.format_day_schedule(day, schedule)
        else:
            DisplayFormatter.error(message)
    
    def handle_show_my_res(self, cmd):
        """Handle show_my_res command."""
        token = self.session.get_token()
        if not token:
            return
        
        success, message, reservations = self.http_client.get_my_reservations(token)
        
        if success and reservations is not None:
            DisplayFormatter.format_reservations(reservations)
        else:
            DisplayFormatter.error(message)
    
    def handle_make_res(self, cmd):
        """Handle make_res command."""
        valid, params = CommandParser.validate_make_res(cmd)
        
        if not valid or params is None:
            DisplayFormatter.error("Usage: make_res <DAY> <HOUR>")
            DisplayFormatter.info("Example: make_res WED 14")
            DisplayFormatter.info("Valid hours: 9-22")
            return
        
        day, hour = params
        token = self.session.get_token()
        if not token:
            return
        
        DisplayFormatter.info(f"Making reservation for {day} at {hour}:00...")
        success, message = self.http_client.make_reservation(token, day, hour)
        
        if success:
            DisplayFormatter.success(message)
        else:
            DisplayFormatter.error(message)
    
    def handle_cancel_res(self, cmd):
        """Handle cancel_res command."""
        valid, day = CommandParser.validate_cancel_res(cmd)
        
        if not valid or day is None:
            DisplayFormatter.error("Usage: cancel_res <DAY>")
            DisplayFormatter.info("Example: cancel_res MON")
            return
        
        token = self.session.get_token()
        if not token:
            return
        
        DisplayFormatter.info(f"Cancelling reservation for {day}...")
        success, message = self.http_client.cancel_reservation(token, day)
        
        if success:
            DisplayFormatter.success(message)
        else:
            DisplayFormatter.error(message)


def main():
    """
    Main entry point for client.
    
    Teaching Point: Command-line argument parsing
    Format: python3 Client.py <host> <port>
    """
    if len(sys.argv) != 3:
        print("Usage: python3 Client.py <host> <port>")
        print("Example: python3 Client.py 127.0.0.1 60000")
        sys.exit(1)
    
    host = sys.argv[1]
    try:
        port = int(sys.argv[2])
    except ValueError:
        print("Error: Port must be an integer")
        sys.exit(1)
    
    # Create and run client
    client = TennisCourtClient(host, port)
    client.run()


if __name__ == "__main__":
    main()
