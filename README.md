# Nexus Backend

The Nexus backend is a high-performance, asynchronous FastAPI service powered by MongoDB (Motor)[cite: 2].

**Live Deployment:** Frontend — [Vercel URL]. Backend: not deployed (see Week 3 documentation for details); run locally via instructions below[cite: 2].

## Local Setup

1. **Environment**: Ensure Python 3.11+ is installed[cite: 2].
2. **Setup .env**: Copy `.env.example` to `.env` and fill in the required `MONGODB_URL`[cite: 2].
3. **Install Dependencies**: `pip install -r requirements.txt`[cite: 2].
4. **Run Server**: `python -m uvicorn src.server.main:app --reload`[cite: 2].

## API Endpoints

### Authentication (`/api/v1/auth`)
- `POST /register`: Register a new Entrepreneur or Investor[cite: 2].
- `POST /login`: Authenticate and receive a JWT[cite: 2].
- `GET /me`: Retrieve current user profile[cite: 2].

### Collaboration (`/api/v1/collaboration`)
- `POST /request`: Send collaboration request[cite: 2].
- `PATCH /request/{id}/status`: Accept or reject requests[cite: 2].
- `GET /requests/incoming`: Fetch received requests[cite: 2].
- `GET /requests/outgoing`: Fetch sent requests[cite: 2].

### Meetings (`/api/v1/meetings`)
- `POST /`: Schedule a new meeting (with overlap checks)[cite: 2].
- `PATCH /{id}/status`: Accept/Reject meetings[cite: 2].
- `GET /my-calendar`: View user schedule[cite: 2].

### Video (`/api/v1/video`)
- `WS /stream/{room_id}?token=<jwt>`: WebSocket signaling server for WebRTC[cite: 2].

### Documents (`/api/v1/documents`)
- `POST /upload`: Upload PDF document[cite: 2].
- `GET /view/{id}`: Secure document stream[cite: 2].
- `POST /{id}/sign`: Append e-signature[cite: 2].

### Payments (`/api/v1/payments`)
- `POST /deposit`, `POST /withdraw`: Fund movements[cite: 2].
- `POST /transfer`: Peer-to-peer transfers[cite: 2].
- `GET /history`: Transaction ledger[cite: 2].

### Security (`/api/v1/security`)
- `POST /2fa/enable`, `POST /2fa/generate`, `POST /2fa/verify`: 2FA management[cite: 2].

## Health Check
- `GET /health`: Returns connection status to MongoDB[cite: 2].
