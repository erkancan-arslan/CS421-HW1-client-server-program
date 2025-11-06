"""
AuthenticationManager - Handles user authentication and session management

Design Decision: Separate authentication from business logic
Why? - Security concerns isolated in one place
     - Easy to upgrade (e.g., add password hashing, JWT tokens)
     - Testable without network layer
"""

import uuid
from datetime import datetime
from typing import Optional, Dict
from server.models import Session, PREDEFINED_USERS


class AuthenticationManager:
    """
    Manages user authentication and active sessions.
    
    Design Decision: Token-based authentication (stateful)
    Why? - Simple to implement
         - Server maintains session state
         - Suitable for single-server deployment
    
    Alternative (not chosen): JWT tokens (stateless)
    Why not? - More complex for learning purposes
             - Requires crypto libraries
             - Overkill for this scale
    
    Security Note: This is simplified for educational purposes.
    Production would need:
    - Password hashing (bcrypt, argon2)
    - Token expiration
    - HTTPS for transport security
    - Rate limiting on login attempts
    """
    
    def __init__(self):
        """
        Initialize authentication manager.
        
        Design Decision: In-memory session storage
        Why? - Fast lookup O(1)
             - Simple for single-server
             - Sessions lost on restart (acceptable per requirements)
        """
        self.active_sessions: Dict[str, Session] = {}
    
    def authenticate(self, username: str, password: str) -> Optional[str]:
        """
        Authenticate user and create session.
        
        Args:
            username: User's username
            password: User's password
        
        Returns:
            Session token if authentication successful, None otherwise
        
        Design Decision: Return token (not Session object)
        Why? - Token is what client needs
             - Don't expose internal Session structure
             - Principle of least privilege
        
        Teaching Point: This implements HTTP "stateful" session pattern
        Server remembers who you are via token in subsequent requests
        """
        # Validate credentials
        if username not in PREDEFINED_USERS:
            return None
        
        if PREDEFINED_USERS[username] != password:
            return None
        
        # Generate unique session token
        # Design Decision: UUID4 for token generation
        # Why? - Cryptographically random
        #      - Extremely low collision probability
        #      - Standard Python library
        token = str(uuid.uuid4())
        
        # Create session
        session = Session(
            username=username,
            token=token,
            login_time=datetime.now()
        )
        
        self.active_sessions[token] = session
        
        return token
    
    def validate_token(self, token: str) -> Optional[str]:
        """
        Validate a session token and return the username.
        
        Args:
            token: Session token to validate
        
        Returns:
            Username if token is valid, None otherwise
        
        Design Decision: Return username (not full Session)
        Why? - Caller usually just needs to know who the user is
             - Less coupling to Session internal structure
        
        Teaching Point: This is called on EVERY request after login
        to verify the user is authenticated
        """
        session = self.active_sessions.get(token)
        if session is None:
            return None
        return session.username
    
    def logout(self, token: str) -> bool:
        """
        End a user session.
        
        Args:
            token: Session token to invalidate
        
        Returns:
            True if session was active and terminated, False otherwise
        
        Design Decision: Allow logout even if token is invalid
        Why? - Idempotent operation (safe to call multiple times)
             - Client doesn't need to check before logging out
        """
        if token in self.active_sessions:
            del self.active_sessions[token]
            return True
        return False
    
    def get_session_info(self, token: str) -> Optional[Dict]:
        """
        Get information about an active session.
        
        Args:
            token: Session token
        
        Returns:
            Dictionary with session info, or None if invalid
        
        Design Decision: Return dict (not Session object)
        Why? - Easy to serialize to JSON for API responses
             - Don't expose internal objects
        """
        session = self.active_sessions.get(token)
        if session is None:
            return None
        return session.to_dict()
    
    def get_active_session_count(self) -> int:
        """
        Get number of active sessions.
        
        Teaching Point: Useful for monitoring/debugging
        """
        return len(self.active_sessions)
    
    def clear_all_sessions(self):
        """
        Clear all active sessions (for testing or maintenance).
        
        Design Decision: Provide admin function to reset state
        Why? - Useful for testing
             - Could be used for "logout all users" feature
        """
        self.active_sessions.clear()
