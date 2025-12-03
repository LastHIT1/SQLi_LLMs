# SQLi_IPS_With_LLMs

A Modular LLM-Driven HTTP Request Gatekeeper for Dynamic SQL-Injection Detection and Mitigation

## Overview

This project implements a multi-layered security architecture for detecting and preventing SQL injection attacks in web applications. It combines:

- **LLM-based detection** (GPT-4.1-nano via OpenAI API)
- **ML-based detection** (MobileBERT fine-tuned for SQLi classification)
- **Response filtering** (prevents SQL error information leakage)
- **Gateway-level enforcement** (OpenResty/Nginx with Lua scripting)

## Architecture

```
┌─────────────┐     ┌─────────────────────────────────────────────────────────┐
│   Client    │────▶│                      Gateway                            │
│  (Browser)  │     │              (OpenResty + Lua)                          │
└─────────────┘     │  ┌─────────────┐              ┌──────────────────┐      │
                    │  │ guardrail   │              │ response_filter  │      │
                    │  │    .lua     │              │      .lua        │      │
                    │  └──────┬──────┘              └────────┬─────────┘      │
                    └─────────┼──────────────────────────────┼────────────────┘
                              │                              │
              ┌───────────────┼──────────────────────────────┼───────────────┐
              │               ▼                              ▼               │
              │    ┌─────────────────┐            ┌─────────────────────┐    │
              │    │    Guardrail    │            │   Response Filter   │    │
              │    │   (GPT-4.1)     │            │   (Pattern Match)   │    │
              │    │   Port: 5000    │            │     Port: 5002      │    │
              │    └─────────────────┘            └─────────────────────┘    │
              │                                                              │
              │    ┌─────────────────┐            ┌─────────────────────┐    │
              │    │   Guardrail V2  │            │      Test App       │    │
              │    │  (MobileBERT)   │◀──────────▶│     (Django)        │    │
              │    │   Port: 5001    │            │     Port: 8000      │    │
              │    └─────────────────┘            └─────────────────────┘    │
              │                                                              │
              │    ┌─────────────────┐            ┌─────────────────────┐    │
              │    │      Redis      │            │     PostgreSQL      │    │
              │    │   Port: 6379    │            │     Port: 5432      │    │
              │    └─────────────────┘            └─────────────────────┘    │
              │                         Docker Network                       │
              └──────────────────────────────────────────────────────────────┘
```

## Components

### 1. Gateway (OpenResty/Nginx)
- **Location**: `gateway/`
- **Port**: 8080 (external)
- **Purpose**: Entry point for all HTTP requests
- **Features**:
  - Proxies requests to the test application
  - Executes Lua scripts for request/response filtering
  - `guardrail.lua`: Sends requests to Guardrail service for SQLi detection
  - `response_filter.lua`: Filters responses containing SQL error messages

### 2. Guardrail (LLM-based Detection)
- **Location**: `guardrail/`
- **Port**: 5000
- **Technology**: FastAPI + OpenAI GPT-4.1-nano
- **Purpose**: Analyzes HTTP requests using LLM to detect SQL injection patterns
- **Detection capabilities**:
  - SQL keywords (SELECT, UNION, DROP, INSERT, UPDATE, DELETE)
  - SQL comments (--, /*, #)
  - Quote manipulation (' or ")
  - Boolean injection (OR 1=1, AND 1=1)
  - Time-based attacks (SLEEP, WAITFOR)

### 3. Guardrail V2 (ML-based Detection)
- **Location**: `guardrailv2/`
- **Port**: 5001
- **Technology**: FastAPI + PyTorch + HuggingFace Transformers
- **Model**: `cssupport/mobilebert-sql-injection-detect`
- **Purpose**: Local ML-based SQLi detection without external API calls
- **Features**:
  - Configurable confidence threshold (default: 70%)
  - GPU acceleration support (falls back to CPU)
  - Lower latency than LLM-based detection

### 4. Response Filter
- **Location**: `response-filter/`
- **Port**: 5002
- **Technology**: FastAPI
- **Purpose**: Prevents SQL error information leakage in responses
- **Detects patterns for**: PostgreSQL, MySQL, SQLite, and Django ORM errors

### 5. Test Application
- **Location**: `test-app/`
- **Port**: 8000 (internal)
- **Technology**: Django
- **Purpose**: Intentionally vulnerable application for testing SQLi detection
- **Features**:
  - Vulnerable book search functionality
  - Vulnerable login form
  - Security control panel for toggling protections
  - Integration with Guardrail V2 via Django middleware

### 6. Supporting Services
- **Redis** (Port 6379): Stores security component states (enabled/disabled)
- **PostgreSQL** (Port 5432): Application database

## Prerequisites

- Docker and Docker Compose
- OpenAI API key (for Guardrail LLM-based detection)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd SQLi_LLMs
   ```

2. **Configure environment variables**:
   ```bash
   # Create .env file in guardrail directory
   echo "OPENAI_API_KEY=your-openai-api-key" > guardrail/.env
   ```

3. **Build and start all services**:
   ```bash
   docker compose up --build
   ```

   For development with hot-reload:
   ```bash
   docker compose watch
   ```

4. **Access the application**:
   - Web Application: http://localhost:8080
   - Security Control Panel: http://localhost:8080/security/

## Usage

### Accessing the Web Application

Navigate to http://localhost:8080 to access the FIU BookStore test application.

### Testing SQL Injection Detection

#### 1. Search Field (GET request)
Try these payloads in the book search field:

```sql
# Basic SQLi
' OR '1'='1

# UNION-based
' UNION SELECT * FROM auth_user --

# Comment injection
admin'--

# Boolean-based
' OR 1=1 --
```

#### 2. Login Form (POST request)
Try these payloads in the username field:

```sql
# Authentication bypass
admin' --

# Union injection
' UNION SELECT 1,password FROM auth_user WHERE username='admin' --
```

#### 3. URL Parameter Injection
Access book details with injected IDs:

```
http://localhost:8080/book/1 OR 1=1
http://localhost:8080/book/1; DROP TABLE core_book --
```

### Managing Security Controls

#### Via Web Interface
Navigate to http://localhost:8080/security/ to access the security control panel where you can toggle:
- Guardrail (LLM-based detection)
- Guardrail V2 (ML-based detection)
- SQL Error Filter (Response filtering)

#### Via API Endpoints

**Guardrail (LLM)**:
```bash
# Check status
curl http://localhost:5000/status

# Activate
curl http://localhost:5000/activate

# Deactivate
curl http://localhost:5000/deactivate
```

**Guardrail V2 (ML)**:
```bash
# Check status
curl http://localhost:5001/status

# Activate
curl http://localhost:5001/activate

# Deactivate
curl http://localhost:5001/deactivate
```

**Response Filter**:
```bash
# Check status
curl http://localhost:5002/status

# Activate
curl http://localhost:5002/activate

# Deactivate
curl http://localhost:5002/deactivate
```

### Direct API Testing

Test the guardrail services directly:

**Guardrail (LLM)**:
```bash
curl -X POST http://localhost:5000/ \
  -H "Content-Type: text/plain" \
  -H "X-Original-URI: /search?q=' OR '1'='1" \
  -H "X-Original-Method: GET"
```

**Guardrail V2 (ML)**:
```bash
curl -X POST http://localhost:5001/ \
  -H "Content-Type: text/plain" \
  -H "X-Original-URI: /search" \
  -H "X-Original-Method: POST" \
  -d "username=' OR '1'='1&password=test"
```

## Configuration

### Guardrail V2 Settings

Edit `guardrailv2/main.py` to adjust:
```python
CONFIDENCE_THRESHOLD: Final[float] = 0.7  # Minimum confidence for blocking
```

### Django Guardrail Client Settings

In `test-app/config/settings.py`:
```python
GUARDRAIL_SERVICE_URL = "http://guardrailv2:5001"
GUARDRAIL_TIMEOUT = 5.0
GUARDRAIL_ENABLED = True
GUARDRAIL_FAIL_OPEN = False  # If True, allows requests when service is down
```

### Gateway Timeouts

Edit `gateway/guardrail.lua`:
```lua
local TIMEOUT_MS = 10000  -- Request timeout in milliseconds
```

## Development

### Project Structure
```
SQLi_LLMs/
├── docker-compose.yml      # Service orchestration
├── gateway/                # OpenResty gateway
│   ├── Dockerfile
│   ├── nginx.conf          # Main nginx configuration
│   ├── default.conf        # Server block configuration
│   ├── guardrail.lua       # Request filtering logic
│   └── response_filter.lua # Response filtering logic
├── guardrail/              # LLM-based detection service
│   ├── Dockerfile
│   ├── main.py
│   └── pyproject.toml
├── guardrailv2/            # ML-based detection service
│   ├── Dockerfile
│   ├── main.py
│   └── pyproject.toml
├── response-filter/        # Response filtering service
│   ├── Dockerfile
│   ├── main.py
│   └── pyproject.toml
├── test-app/               # Vulnerable Django application
│   ├── Dockerfile
│   ├── manage.py
│   ├── config/             # Django settings
│   ├── core/               # Main application
│   └── django_guardrail/   # Guardrail integration
└── database/               # PostgreSQL initialization
    ├── Dockerfile
    └── create.sql
```

### Running Individual Services

```bash
# Start only specific services
docker compose up gateway guardrailv2 test-app database cache

# View logs for a specific service
docker compose logs -f guardrailv2

# Rebuild a specific service
docker compose build guardrailv2
docker compose up -d guardrailv2
```

### Local Development (without Docker)

For each Python service:
```bash
cd <service-directory>
uv venv
uv pip install -e .
uv run uvicorn main:app --reload --host 0.0.0.0 --port <port>
```

## Security Layers Explained

### Layer 1: Gateway-Level Request Filtering
The OpenResty gateway intercepts all incoming requests and forwards them to the Guardrail service. If an attack is detected, the request is blocked before reaching the application.

### Layer 2: Application-Level Query Validation
The Django application integrates with Guardrail V2 via a custom database wrapper. SQL queries are validated before execution, providing defense-in-depth.

### Layer 3: Response Filtering
Even if an attack bypasses request filtering, the response filter prevents SQL error messages from being exposed to attackers, limiting information disclosure.

## Blocked Request Response

When a SQL injection attempt is detected, users see a branded security alert page with:
- Threat type classification
- Target URL and method
- Detected payload (sanitized)

## Troubleshooting

### Service won't start
```bash
# Check service logs
docker compose logs <service-name>

# Verify all containers are running
docker compose ps
```

### Guardrail not detecting attacks
1. Check if the service is enabled: `curl http://localhost:5000/status`
2. Verify OpenAI API key is set correctly
3. Check service logs for errors

### High latency
- Consider using Guardrail V2 (ML-based) instead of Guardrail (LLM-based) for faster response times
- Adjust timeout settings in `gateway/guardrail.lua`

### Model download issues (Guardrail V2)
The MobileBERT model is downloaded on first startup. Ensure the container has internet access and sufficient disk space.

## License

This project is for educational and research purposes. The intentionally vulnerable components should never be deployed in production environments.
