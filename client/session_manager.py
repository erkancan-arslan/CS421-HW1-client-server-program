"""
SessionManager - Manages user session state

Design Decision: Simple in-memory session storage
Why? - Client is single-user
     - No need for persistence across restarts
     - Simple and clear
"""

from typing import Optional


class SessionManager:
    """
    Manages user session (login state and token).
    
    Design Decision: Single active session
    Why? - Console app has one user at a time
         - No concurrent session needs
         - Simple state management
    """
    
    def __init__(self):
        """Initialize session manager with no active session."""
        self.token: Optional[str] = None
        self.username: Optional[str] = None
    
    def login(self, username: str, token: str):
        """
        Store session information after successful login.
        
        Args:
            username: Logged in user's username
            token: Authentication token from server
        
        Teaching Point: This is client-side session management
        Token is stored in memory and sent with each request
        """
        self.token = token
        self.username = username
    
    def logout(self):
        """Clear session information."""
        self.token = None
        self.username = None
    
    def is_logged_in(self) -> bool:
        """Check if user is currently logged in."""
        return self.token is not None and self.username is not None
    
    def get_token(self) -> Optional[str]:
        """Get current session token."""
        return self.token
    
    def get_username(self) -> Optional[str]:
        """Get current logged in username."""
        return self.username
    
    def require_login(self) -> bool:
        """
        Check if logged in and print error if not.
        
        Returns:
            True if logged in, False otherwise
        
        Design Decision: Convenience method for command handlers
        Why? - Reduces boilerplate in each command
             - Consistent error message
             - Single responsibility
        """
        if not self.is_logged_in():
            print("❌ You must login first. Use: login <username> <password>")
            return False
        return True
