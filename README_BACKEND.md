# Nexus Backend

The Nexus backend is a high-performance, asynchronous FastAPI service powered by MongoDB (Motor).

## Local Setup

1. **Environment**: Ensure Python 3.11+ is installed.
2. **Setup .env**: Copy `.env.example` to `.env` and fill in the required `MONGODB_URL`.
3. **Install Dependencies**: `pip install -r requirements.txt`
4. **Run Server**: `python -m uvicorn src.server.main:app --reload`

## API Endpoints

### Authentication (`/api/v1/auth`)
- `POST /register`: Register a new Entrepreneur or Investor.
- `POST /login`: Authenticate and receive a JWT.
- `GET /me`: Retrieve current user profile.

### Collaboration (`/api/v1/collaboration`)
- `POST /request`: Send collaboration request.
- `PATCH /request/{id}/status`: Accept or reject requests.
- `GET /requests/incoming`: Fetch received requests.
- `GET /requests/outgoing`: Fetch sent requests.

### Meetings (`/api/v1/meetings`)
- `POST /`: Schedule a new meeting (with overlap checks).
- `PATCH /{id}/status`: Accept/Reject meetings.
- `GET /my-calendar`: View user schedule.

### Video (`/api/v1/video`)
- `WS /stream/{room_id}?token=<jwt>`: WebSocket signaling server for WebRTC.

### Documents (`/api/v1/documents`)
- `POST /upload`: Upload PDF document.
- `GET /view/{id}`: Secure document stream.
- `POST /{id}/sign`: Append e-signature.

### Payments (`/api/v1/payments`)
- `POST /deposit`, `POST /withdraw`: Fund movements.
- `POST /transfer`: Peer-to-peer transfers.
- `GET /history`: Transaction ledger.

### Security (`/api/v1/security`)
- `POST /2fa/enable`, `POST /2fa/generate`, `POST /2fa/verify`: 2FA management.

## Health Check
- `GET /health`: Returns connection status to MongoDB.
