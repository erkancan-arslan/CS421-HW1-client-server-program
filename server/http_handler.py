"""
HTTPHandler - Manual HTTP protocol implementation

Design Decision: Build HTTP parser from scratch
Why? - Educational: See how HTTP actually works
     - Requirement: No third-party libraries
     - Learn: Request/response structure, headers, body parsing

Teaching Point: HTTP is just text over TCP!
Format:
  REQUEST:
    METHOD /path HTTP/1.1\r\n
    Header1: value1\r\n
    Header2: value2\r\n
    \r\n
    [optional body]
    
  RESPONSE:
    HTTP/1.1 STATUS_CODE Reason\r\n
    Header1: value1\r\n
    \r\n
    [optional body]
"""

import json
from typing import Dict, Tuple, Optional, Any


class HTTPRequest:
    """
    Represents a parsed HTTP request.
    
    Design Decision: Parse into structured object
    Why? - Type safety
         - Easy to access request parts
         - Can validate once at parse time
    """
    
    def __init__(self):
        self.method: str = ""
        self.path: str = ""
        self.version: str = "HTTP/1.1"
        self.headers: Dict[str, str] = {}
        self.body: str = ""
        self.query_params: Dict[str, str] = {}
    
    def __repr__(self):
        return f"HTTPRequest({self.method} {self.path})"


class HTTPResponse:
    """
    Represents an HTTP response to be sent.
    
    Design Decision: Builder pattern for responses
    Why? - Fluent interface
         - Ensures proper formatting
         - Hard to forget headers
    """
    
    def __init__(self, status_code: int, reason: str = ""):
        self.status_code = status_code
        self.reason = reason or self._get_default_reason(status_code)
        self.headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "Connection": "close"
        }
        self.body: str = ""
    
    @staticmethod
    def _get_default_reason(code: int) -> str:
        """
        Get standard HTTP reason phrase for status code.
        
        Teaching Point: These are the standard HTTP status codes
        Memorizing common ones is valuable for web development!
        """
        reasons = {
            200: "OK",
            201: "Created",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            409: "Conflict",
            500: "Internal Server Error"
        }
        return reasons.get(code, "Unknown")
    
    def set_json_body(self, data: Any):
        """
        Set response body as JSON.
        
        Design Decision: Automatic JSON serialization
        Why? - All our APIs use JSON
             - Prevents manual json.dumps() everywhere
             - Sets correct Content-Type header
        """
        self.body = json.dumps(data)
        self.headers["Content-Type"] = "application/json"
        self.headers["Content-Length"] = str(len(self.body.encode('utf-8')))
    
    def to_bytes(self) -> bytes:
        """
        Convert response to bytes for sending over socket.
        
        Teaching Point: HTTP is text protocol, but sockets use bytes
        Must encode strings to bytes (UTF-8)
        
        Format:
          HTTP/1.1 200 OK\r\n
          Content-Type: application/json\r\n
          Content-Length: 42\r\n
          \r\n
          {"message": "success"}
        """
        # Status line
        status_line = f"HTTP/1.1 {self.status_code} {self.reason}\r\n"
        
        # Headers
        header_lines = []
        for key, value in self.headers.items():
            header_lines.append(f"{key}: {value}\r\n")
        
        # Combine: status + headers + blank line + body
        response = status_line + "".join(header_lines) + "\r\n" + self.body
        
        return response.encode('utf-8')


class HTTPHandler:
    """
    Handles HTTP request parsing and response building.
    
    Design Decision: Stateless handler
    Why? - Each request is independent
         - Thread-safe (no shared state)
         - Simple to reason about
    """
    
    @staticmethod
    def parse_request(raw_data: bytes) -> Optional[HTTPRequest]:
        """
        Parse raw HTTP request bytes into HTTPRequest object.
        
        Args:
            raw_data: Raw bytes from socket
        
        Returns:
            HTTPRequest object or None if parsing fails
        
        Teaching Point: This is how web servers parse requests!
        - Split by \r\n to get lines
        - First line is method/path/version
        - Following lines are headers (until blank line)
        - Everything after blank line is body
        
        Design Decision: Return None on parse error (not raise exception)
        Why? - Malformed requests are expected (bad clients, attacks)
             - Caller can send 400 Bad Request
        """
        try:
            # Decode bytes to string
            raw_str = raw_data.decode('utf-8')
            
            # Split request into parts
            # Format: headers\r\n\r\nbody
            parts = raw_str.split('\r\n\r\n', 1)
            header_section = parts[0]
            body = parts[1] if len(parts) > 1 else ""
            
            # Split headers into lines
            lines = header_section.split('\r\n')
            
            if not lines:
                return None
            
            # Parse request line (first line)
            # Format: "GET /path HTTP/1.1"
            request_line = lines[0]
            request_parts = request_line.split(' ')
            
            if len(request_parts) != 3:
                return None
            
            request = HTTPRequest()
            request.method = request_parts[0].upper()
            request.version = request_parts[2]
            
            # Parse path and query parameters
            # Example: "/schedule?day=MON" -> path="/schedule", params={"day": "MON"}
            path_with_query = request_parts[1]
            if '?' in path_with_query:
                path, query_string = path_with_query.split('?', 1)
                request.path = path
                # Parse query parameters: "key1=val1&key2=val2"
                for param in query_string.split('&'):
                    if '=' in param:
                        key, value = param.split('=', 1)
                        request.query_params[key] = value
            else:
                request.path = path_with_query
            
            # Parse headers (remaining lines)
            # Format: "Header-Name: value"
            for line in lines[1:]:
                if ':' in line:
                    key, value = line.split(':', 1)
                    request.headers[key.strip()] = value.strip()
            
            # Store body
            request.body = body
            
            return request
            
        except Exception as e:
            # Parsing failed - return None
            print(f"Error parsing request: {e}")
            return None
    
    @staticmethod
    def build_response(status_code: int, data: Any = None, message: str = "") -> HTTPResponse:
        """
        Build a standard JSON response.
        
        Args:
            status_code: HTTP status code
            data: Optional data to include in response
            message: Optional message to include
        
        Returns:
            HTTPResponse object
        
        Design Decision: Standard response format
        Why? - Consistent API for clients
             - Always includes success/message/data
             - Easy to parse on client side
        
        Response format:
          {
            "success": true/false,
            "message": "...",
            "data": {...}
          }
        """
        response = HTTPResponse(status_code)
        
        # Determine success based on status code
        success = 200 <= status_code < 300
        
        body = {
            "success": success,
            "message": message
        }
        
        if data is not None:
            body["data"] = data
        
        response.set_json_body(body)
        return response
    
    @staticmethod
    def parse_json_body(request: HTTPRequest) -> Optional[Dict]:
        """
        Parse JSON from request body.
        
        Args:
            request: HTTPRequest object
        
        Returns:
            Parsed JSON dict or None if invalid
        
        Design Decision: Separate parsing method
        Why? - Not all requests have JSON body
             - Explicit parsing = clearer code
             - Can handle errors gracefully
        """
        if not request.body:
            return None
        
        try:
            return json.loads(request.body)
        except json.JSONDecodeError:
            return None
    
    @staticmethod
    def extract_token(request: HTTPRequest) -> Optional[str]:
        """
        Extract authentication token from request.
        
        Design Decision: Token in Authorization header
        Why? - Standard HTTP authentication pattern
             - Format: "Authorization: Bearer <token>"
             - Separate from request body
        
        Alternative considered: Token in query parameter
        Why not? - Less secure (URLs logged)
                 - Not standard practice
        """
        auth_header = request.headers.get('Authorization', '')
        
        # Format: "Bearer <token>"
        if auth_header.startswith('Bearer '):
            return auth_header[7:]  # Remove "Bearer " prefix
        
        return None
