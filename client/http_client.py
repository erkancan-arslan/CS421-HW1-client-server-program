"""
HTTPClient - HTTP communication with server

Design Decision: Reusable client for all API calls
Why? - Consistent error handling
     - Automatic token inclusion
     - Clean separation from UI logic
"""

import socket
import json
from typing import Dict, Tuple, Optional, Any


class HTTPClient:
    """
    HTTP client for communicating with tennis court server.
    
    Design Decision: Stateless client (token passed per request)
    Why? - Thread-safe
         - Simple to reason about
         - Token managed by SessionManager
    """
    
    def __init__(self, host: str, port: int):
        """
        Initialize HTTP client.
        
        Args:
            host: Server hostname/IP
            port: Server port
        """
        self.host = host
        self.port = port
    
    def send_request(
        self,
        method: str,
        path: str,
        body: Optional[Dict] = None,
        token: Optional[str] = None
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Send HTTP request to server.
        
        Args:
            method: HTTP method (GET, POST, DELETE)
            path: URL path
            body: Optional JSON body
            token: Optional authentication token
        
        Returns:
            Tuple of (status_code, response_body_dict)
        
        Design Decision: Return parsed response
        Why? - Caller doesn't deal with HTTP parsing
             - Consistent error handling
             - Type-safe return value
        """
        try:
            # Build request
            request_lines = [
                f"{method} {path} HTTP/1.1",
                f"Host: {self.host}:{self.port}"
            ]
            
            # Add authentication header if token provided
            if token:
                request_lines.append(f"Authorization: Bearer {token}")
            
            # Add body if present
            if body:
                body_json = json.dumps(body)
                request_lines.append("Content-Type: application/json")
                request_lines.append(f"Content-Length: {len(body_json)}")
                request_lines.append("")  # Blank line before body
                request_lines.append(body_json)
            else:
                request_lines.append("")  # Blank line
            
            request_str = "\r\n".join(request_lines)
            
            # Create socket and connect
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(10)  # 10 second timeout
            
            try:
                client_socket.connect((self.host, self.port))
            except ConnectionRefusedError:
                return -1, {
                    "success": False,
                    "message": "Connection refused. Is the server running?"
                }
            except socket.timeout:
                return -1, {
                    "success": False,
                    "message": "Connection timeout. Server not responding."
                }
            
            # Send request
            client_socket.sendall(request_str.encode('utf-8'))
            
            # Receive response
            response_data = b""
            client_socket.settimeout(5)  # 5 second timeout for response
            
            try:
                while True:
                    chunk = client_socket.recv(4096)
                    if not chunk:
                        break
                    response_data += chunk
                    
                    # Check if we have complete headers
                    if b'\r\n\r\n' in response_data:
                        header_end = response_data.find(b'\r\n\r\n')
                        headers = response_data[:header_end].decode('utf-8')
                        
                        # Extract Content-Length
                        content_length = None
                        for line in headers.split('\r\n'):
                            if line.lower().startswith('content-length:'):
                                content_length = int(line.split(':')[1].strip())
                                break
                        
                        # Check if we have all the body
                        if content_length is not None:
                            body_received = len(response_data) - header_end - 4
                            if body_received >= content_length:
                                break
                        else:
                            # No content-length, assume done
                            break
            except socket.timeout:
                # Timeout means we got all data
                pass
            
            client_socket.close()
            
            # Parse response
            if not response_data:
                return -1, {
                    "success": False,
                    "message": "No response from server"
                }
            
            response_str = response_data.decode('utf-8')
            
            # Extract status code
            status_line = response_str.split('\r\n')[0]
            status_parts = status_line.split(' ')
            
            if len(status_parts) < 2:
                return -1, {
                    "success": False,
                    "message": "Invalid response format"
                }
            
            status_code = int(status_parts[1])
            
            # Extract body
            body_start = response_str.find('\r\n\r\n') + 4
            body_str = response_str[body_start:]
            
            if body_str:
                try:
                    body_dict = json.loads(body_str)
                except json.JSONDecodeError:
                    return status_code, {
                        "success": False,
                        "message": f"Invalid JSON response: {body_str[:100]}"
                    }
            else:
                body_dict = {"success": True, "message": "No content"}
            
            return status_code, body_dict
            
        except Exception as e:
            return -1, {
                "success": False,
                "message": f"Error: {str(e)}"
            }
    
    def login(self, username: str, password: str) -> Tuple[bool, str, Optional[str]]:
        """
        Attempt to login to server.
        
        Returns:
            Tuple of (success, message, token)
        
        Design Decision: Specialized method for login
        Why? - Common operation deserves convenience method
             - Clear return type
             - Hides HTTP details from caller
        """
        status, body = self.send_request(
            "POST",
            "/login",
            body={"username": username, "password": password}
        )
        
        if status == 200 and body.get('success'):
            token = body.get('data', {}).get('token')
            message = body.get('message', 'Login successful')
            return True, message, token
        else:
            message = body.get('message', 'Login failed')
            return False, message, None
    
    def get_weekly_schedule(self, token: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Get weekly schedule.
        
        Returns:
            Tuple of (success, message, schedule_data)
        """
        status, body = self.send_request("GET", "/schedule", token=token)
        
        if status == 200 and body.get('success'):
            schedule = body.get('data', {}).get('schedule')
            message = body.get('message', 'Schedule retrieved')
            return True, message, schedule
        else:
            message = body.get('message', 'Failed to get schedule')
            return False, message, None
    
    def get_day_schedule(self, token: str, day: str) -> Tuple[bool, str, Optional[list]]:
        """
        Get schedule for specific day.
        
        Returns:
            Tuple of (success, message, day_schedule_list)
        """
        status, body = self.send_request(
            "GET",
            f"/schedule/day?day={day}",
            token=token
        )
        
        if status == 200 and body.get('success'):
            schedule = body.get('data', {}).get('schedule')
            message = body.get('message', f'Schedule for {day} retrieved')
            return True, message, schedule
        else:
            message = body.get('message', f'Failed to get schedule for {day}')
            return False, message, None
    
    def get_my_reservations(self, token: str) -> Tuple[bool, str, Optional[list]]:
        """
        Get user's reservations.
        
        Returns:
            Tuple of (success, message, reservations_list)
        """
        status, body = self.send_request("GET", "/reservations", token=token)
        
        if status == 200 and body.get('success'):
            reservations = body.get('data', {}).get('reservations', [])
            message = body.get('message', f'Found {len(reservations)} reservation(s)')
            return True, message, reservations
        else:
            message = body.get('message', 'Failed to get reservations')
            return False, message, None
    
    def make_reservation(
        self,
        token: str,
        day: str,
        hour: int
    ) -> Tuple[bool, str]:
        """
        Make a reservation.
        
        Returns:
            Tuple of (success, message)
        """
        status, body = self.send_request(
            "POST",
            "/reservations",
            body={"day": day, "hour": hour},
            token=token
        )
        
        success = status == 200 and body.get('success')
        message = body.get('message', 'Reservation failed')
        return success, message
    
    def cancel_reservation(self, token: str, day: str) -> Tuple[bool, str]:
        """
        Cancel a reservation.
        
        Returns:
            Tuple of (success, message)
        """
        status, body = self.send_request(
            "DELETE",
            f"/reservations/{day}",
            token=token
        )
        
        success = status == 200 and body.get('success')
        message = body.get('message', 'Cancellation failed')
        return success, message
