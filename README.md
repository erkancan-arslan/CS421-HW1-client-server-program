# Tennis Court Reservation System

A client-server application for managing tennis court reservations using TCP sockets and HTTP protocol.

## 📋 Project Overview

This is a CS421 Computer Networks course assignment implementing a reservation system for a single tennis court with:
- **7 days** (MON-SUN) 
- **14 hourly slots** per day (09:00-23:00)
- **10 predefined users** (user1-user10 with passwords 1-10)
- **Token-based authentication**
- **HTTP communication over TCP sockets**

## 🏗️ Architecture

### Server Components
- `Server.py` - Main server with TCP socket management
- `server/models.py` - Data structures and constants
- `server/auth_manager.py` - Authentication and session management
- `server/schedule_store.py` - Schedule data persistence
- `server/reservation_manager.py` - Business logic and constraints
- `server/http_handler.py` - HTTP protocol implementation

### Client Components
- `Client.py` - Main client with REPL interface
- `client/http_client.py` - HTTP communication layer
- `client/session_manager.py` - Client-side session state
- `client/command_parser.py` - Command parsing and validation
- `client/display_formatter.py` - Console output formatting

## 🚀 Running the System

### Prerequisites
- Python 3.7 or higher
- No third-party libraries required (uses only standard library)

### Start the Server
```bash
python3 Server.py <host> <port>
```

Example:
```bash
python3 Server.py 127.0.0.1 60000
```

### Start the Client
```bash
python3 Client.py <host> <port>
```

Example:
```bash
python3 Client.py 127.0.0.1 60000
```

## 💻 Client Commands

Once connected, use these commands:

### Authentication
```
login <username> <password>
```
Example: `login user1 1`

### View Schedule
```
show_list                    # Show weekly schedule (all 7 days)
show_day <DAY>              # Show specific day (MON, TUE, WED, etc.)
show_my_res                 # Show your reservations
```

### Manage Reservations
```
make_res <DAY> <HOUR>       # Make a reservation
cancel_res <DAY>            # Cancel your reservation for a day
```
Example: `make_res WED 14` (reserves Wednesday 14:00-15:00)

### Other
```
help                        # Show available commands
exit                        # Exit the program
```

## 📜 Reservation Rules

1. **One reservation per user per day** - You cannot make multiple reservations on the same day
2. **No double-booking** - If a slot is taken, another user cannot reserve it
3. **Authentication required** - Must login before performing any operations
4. **One-hour slots** - Each reservation is exactly one hour (e.g., 14:00-15:00)

## 🏛️ System Design

### Multi-threaded Server
- Each client connection runs in a separate thread
- Thread-safe data structures for concurrent access
- Persistent schedule data (optional JSON file backup)

### Modular Architecture
- Clear separation of concerns
- Testable components
- Comprehensive error handling

### HTTP Protocol
- Manual HTTP implementation (no libraries)
- RESTful-style endpoints
- JSON request/response bodies
- Bearer token authentication

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/login` | Authenticate user |
| GET | `/schedule` | Get weekly schedule |
| GET | `/schedule/{day}` | Get daily schedule |
| GET | `/reservations` | Get user's reservations |
| POST | `/reservations` | Create reservation |
| DELETE | `/reservations/{day}` | Cancel reservation |

## 🛠️ Development

### Project Structure
```
CS421-HW1-client-server-program/
├── Server.py              # Server entry point
├── Client.py              # Client entry point
├── server/                # Server modules
│   ├── __init__.py
│   ├── models.py
│   ├── auth_manager.py
│   ├── schedule_store.py
│   ├── reservation_manager.py
│   └── http_handler.py
├── client/                # Client modules
│   ├── __init__.py
│   ├── http_client.py
│   ├── session_manager.py
│   ├── command_parser.py
│   └── display_formatter.py
└── README.md
```

## 📝 Features

### ✅ Implemented
- [x] TCP socket-based communication
- [x] Manual HTTP protocol implementation
- [x] Token-based authentication
- [x] Multi-threaded server
- [x] All required client commands
- [x] Comprehensive error handling
- [x] Beautiful console UI with colors
- [x] Table-formatted schedule display
- [x] Business rule enforcement

### 🎯 Bonus Features
- ANSI color-coded output
- ASCII table formatting
- Comprehensive input validation
- Detailed error messages
- Session persistence
- Optional file-based schedule backup

## 🧪 Testing

The project includes comprehensive test suites (not included in submission):
- 32 server integration tests
- 42 client unit tests
- Manual testing scripts

## 👥 Authors

Erkan Can Arslan

## 📚 Course Information

- **Course**: CS421 Computer Networks
- **Assignment**: Programming Assignment 1
- **Institution**: Sabancı University
- **Semester**: Fall 2025

## 📄 License

This project is for educational purposes as part of CS421 coursework.
