"""
Server - Main server orchestration with TCP sockets and routing

Design Decision: Bring all modules together
This is the "glue code" that:
- Opens TCP socket
- Accepts client connections
- Routes requests to appropriate handlers
- Returns responses

Teaching Point: This is where networking happens!
We're using raw TCP sockets (not HTTP library)
"""

import socket
import threading
import sys
from server.auth_manager import AuthenticationManager
from server.reservation_manager import ReservationManager
from server.schedule_store import ScheduleStore
from server.http_handler import HTTPHandler, HTTPRequest
import json


class TennisCourtServer:
    """
    Main server class - orchestrates all components.
    
    Design Decision: Single class to manage server lifecycle
    Why? - Clear entry point
         - Manages all dependencies
         - Controls socket lifecycle
    """
    
    def __init__(self, host: str, port: int):
        """
        Initialize server components.
        
        Args:
            host: IP address to bind to (e.g., '127.0.0.1')
            port: Port number (e.g., 60000)
        
        Design Decision: Pass host/port as parameters
        Why? - Flexible deployment
             - Can test on different ports
             - Required by assignment spec
        """
        self.host = host
        self.port = port
        self.socket = None
        
        # Initialize all components
        # Design Decision: Create components here (composition pattern)
        # Why? - Server controls lifecycle
        #      - Single instance of each
        #      - Can pass persistence file path if needed
        self.store = ScheduleStore(persistence_file="court_schedule.json")
        self.auth_manager = AuthenticationManager()
        self.reservation_manager = ReservationManager(self.store)
        
        print(f"[Server] Initialized on {host}:{port}")
    
    def start(self):
        """
        Start the server and listen for connections.
        
        Teaching Point: This is the main server loop!
        1. Create socket
        2. Bind to address
        3. Listen for connections
        4. Accept clients in loop
        5. Handle each client in separate thread
        """
        try:
            # Create TCP socket
            # Design Decision: SOCK_STREAM = TCP (reliable, ordered)
            # Alternative: SOCK_DGRAM = UDP (unreliable, faster)
            # Why TCP? - HTTP requires reliable delivery
            #           - Must guarantee packet order
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Set socket options
            # SO_REUSEADDR: Allow reusing address immediately after close
            # Why? - Can restart server quickly during development
            #      - Prevents "Address already in use" error
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Bind to address
            self.socket.bind((self.host, self.port))
            
            # Listen for connections
            # Backlog=5: Queue up to 5 pending connections
            # Design Decision: 5 is reasonable for this application
            # Why? - Small server, not expecting high load
            #      - Can increase if needed
            self.socket.listen(5)
            
            print(f"[Server] Listening on {self.host}:{self.port}")
            print("[Server] Press Ctrl+C to stop")
            
            # Main accept loop
            while True:
                # Accept incoming connection
                # This blocks until a client connects
                client_socket, client_address = self.socket.accept()
                print(f"[Server] New connection from {client_address}")
                
                # Handle client in separate thread
                # Design Decision: Multi-threaded (one thread per client)
                # Why? - Handle multiple clients concurrently
                #      - Don't block while processing one client
                # Alternative: async/await (more complex)
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_address),
                    daemon=True  # Thread dies when main program exits
                )
                client_thread.start()
                
        except KeyboardInterrupt:
            print("\n[Server] Shutting down...")
        except Exception as e:
            print(f"[Server] Error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Clean shutdown of server."""
        if self.socket:
            self.socket.close()
            print("[Server] Socket closed")
    
    def handle_client(self, client_socket: socket.socket, client_address):
        """
        Handle a single client connection.
        
        Args:
            client_socket: Socket connected to client
            client_address: Client's (host, port) tuple
        
        Teaching Point: This runs in a separate thread for each client!
        Multiple clients can be handled simultaneously.
        """
        try:
            # Receive data from client
            # Buffer size: 4096 bytes (4 KB)
            # Design Decision: 4KB is usually enough for HTTP headers + small body
            # Why? - HTTP requests are typically small
            #      - Can receive in chunks if needed
            data = client_socket.recv(4096)
            
            if not data:
                return  # Client closed connection
            
            # Parse HTTP request
            request = HTTPHandler.parse_request(data)
            
            if request is None:
                # Malformed request
                response = HTTPHandler.build_response(
                    400,
                    message="Malformed HTTP request"
                )
                client_socket.sendall(response.to_bytes())
                return
            
            print(f"[Server] {client_address}: {request.method} {request.path}")
            
            # Route request to appropriate handler
            response = self.route_request(request)
            
            # Send response
            client_socket.sendall(response.to_bytes())
            
        except Exception as e:
            print(f"[Server] Error handling client {client_address}: {e}")
            try:
                error_response = HTTPHandler.build_response(
                    500,
                    message="Internal server error"
                )
                client_socket.sendall(error_response.to_bytes())
            except:
                pass  # Can't even send error response
        finally:
            client_socket.close()
    
    def route_request(self, request: HTTPRequest):
        """
        Route request to appropriate handler based on method and path.
        
        Design Decision: Manual routing (no framework)
        Why? - Educational: see how routing works
             - No third-party libraries allowed
             - Simple enough for this application
        
        Routes:
          POST   /login              -> login()
          GET    /schedule           -> get_weekly_schedule()
          GET    /schedule/day       -> get_day_schedule()
          GET    /reservations       -> get_my_reservations()
          POST   /reservations       -> make_reservation()
          DELETE /reservations       -> cancel_reservation()
        """
        
        # Login (no auth required)
        if request.method == "POST" and request.path == "/login":
            return self.handle_login(request)
        
        # Reset endpoint for testing (no auth required - only use in dev!)
        if request.method == "POST" and request.path == "/reset":
            self.reservation_manager.reset_weekly_schedule()
            self.auth_manager.clear_all_sessions()
            return HTTPHandler.build_response(
                200,
                message="Server reset: all reservations and sessions cleared"
            )
        
        # All other endpoints require authentication
        token = HTTPHandler.extract_token(request)
        if not token:
            return HTTPHandler.build_response(
                401,
                message="Missing authentication token. Please login first."
            )
        
        username = self.auth_manager.validate_token(token)
        if not username:
            return HTTPHandler.build_response(
                401,
                message="Invalid or expired token. Please login again."
            )
        
        # Route authenticated requests
        if request.method == "GET" and request.path == "/schedule":
            return self.handle_get_weekly_schedule(request, username)
        
        elif request.method == "GET" and request.path == "/schedule/day":
            return self.handle_get_day_schedule(request, username)
        
        elif request.method == "GET" and request.path == "/reservations":
            return self.handle_get_my_reservations(request, username)
        
        elif request.method == "POST" and request.path == "/reservations":
            return self.handle_make_reservation(request, username)
        
        elif request.method == "DELETE" and request.path.startswith("/reservations"):
            return self.handle_cancel_reservation(request, username)
        
        else:
            # Unknown endpoint
            return HTTPHandler.build_response(
                404,
                message=f"Endpoint not found: {request.method} {request.path}"
            )
    
    # ========== Endpoint Handlers ==========
    
    def handle_login(self, request: HTTPRequest):
        """Handle POST /login"""
        body = HTTPHandler.parse_json_body(request)
        
        if not body or 'username' not in body or 'password' not in body:
            return HTTPHandler.build_response(
                400,
                message="Missing username or password"
            )
        
        username = body['username']
        password = body['password']
        
        token = self.auth_manager.authenticate(username, password)
        
        if token:
            return HTTPHandler.build_response(
                200,
                data={"token": token, "username": username},
                message=f"Login successful. Welcome, {username}!"
            )
        else:
            return HTTPHandler.build_response(
                401,
                message="Invalid username or password"
            )
    
    def handle_get_weekly_schedule(self, request: HTTPRequest, username: str):
        """Handle GET /schedule"""
        schedule = self.reservation_manager.get_weekly_schedule()
        return HTTPHandler.build_response(
            200,
            data={"schedule": schedule},
            message="Weekly schedule retrieved"
        )
    
    def handle_get_day_schedule(self, request: HTTPRequest, username: str):
        """Handle GET /schedule/day?day=MON"""
        day = request.query_params.get('day', '').upper()
        
        if not day:
            return HTTPHandler.build_response(
                400,
                message="Missing 'day' query parameter"
            )
        
        success, result = self.reservation_manager.get_day_schedule(day)
        
        if success:
            return HTTPHandler.build_response(
                200,
                data={"day": day, "schedule": result},
                message=f"Schedule for {day} retrieved"
            )
        else:
            return HTTPHandler.build_response(
                400,
                message=result  # Error message
            )
    
    def handle_get_my_reservations(self, request: HTTPRequest, username: str):
        """Handle GET /reservations"""
        reservations = self.reservation_manager.get_user_reservations(username)
        
        # Convert to dict format
        res_data = [res.to_dict() for res in reservations]
        
        return HTTPHandler.build_response(
            200,
            data={"reservations": res_data},
            message=f"Found {len(reservations)} reservation(s)"
        )
    
    def handle_make_reservation(self, request: HTTPRequest, username: str):
        """Handle POST /reservations"""
        body = HTTPHandler.parse_json_body(request)
        
        if not body or 'day' not in body or 'hour' not in body:
            return HTTPHandler.build_response(
                400,
                message="Missing 'day' or 'hour' in request body"
            )
        
        day = str(body['day']).upper()
        try:
            hour = int(body['hour'])
        except (ValueError, TypeError):
            return HTTPHandler.build_response(
                400,
                message="Invalid hour format. Must be an integer (9-22)"
            )
        
        success, message = self.reservation_manager.make_reservation(
            username, day, hour
        )
        
        if success:
            return HTTPHandler.build_response(200, message=message)
        else:
            # Determine appropriate status code
            if "already have a reservation" in message:
                status = 403  # Forbidden
            elif "already reserved" in message:
                status = 409  # Conflict
            else:
                status = 400  # Bad Request
            
            return HTTPHandler.build_response(status, message=message)
    
    def handle_cancel_reservation(self, request: HTTPRequest, username: str):
        """Handle DELETE /reservations?day=MON or DELETE /reservations/MON"""
        # Support both query param and path param
        day = request.query_params.get('day', '')
        
        if not day:
            # Try to extract from path: /reservations/MON
            parts = request.path.split('/')
            if len(parts) >= 3:
                day = parts[2]
        
        day = day.upper()
        
        if not day:
            return HTTPHandler.build_response(
                400,
                message="Missing 'day' parameter"
            )
        
        success, message = self.reservation_manager.cancel_reservation(
            username, day
        )
        
        if success:
            return HTTPHandler.build_response(200, message=message)
        else:
            # Check if it's invalid day (validation error) vs no reservation found
            if "Invalid day" in message:
                return HTTPHandler.build_response(400, message=message)
            else:
                return HTTPHandler.build_response(404, message=message)


def main():
    """
    Main entry point for server.
    
    Teaching Point: Command-line argument parsing
    Format: python3 Server.py <host> <port>
    """
    if len(sys.argv) != 3:
        print("Usage: python3 Server.py <host> <port>")
        print("Example: python3 Server.py 127.0.0.1 60000")
        sys.exit(1)
    
    host = sys.argv[1]
    try:
        port = int(sys.argv[2])
    except ValueError:
        print("Error: Port must be an integer")
        sys.exit(1)
    
    # Create and start server
    server = TennisCourtServer(host, port)
    server.start()


if __name__ == "__main__":
    main()
