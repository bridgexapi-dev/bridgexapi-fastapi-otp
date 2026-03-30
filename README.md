# BridgeXAPI FastAPI OTP Server

A production-style FastAPI OTP service built on top of BridgeXAPI.

This project demonstrates **programmable SMS routing**, delivery tracking, and authentication flows — without hiding infrastructure behind abstractions.

---

## What this is

This is not just an OTP server.

This is an example of how to build authentication systems when:

* routing is explicit
* pricing is transparent
* delivery is trackable

---

## Programmable Routing vs Messaging APIs

Most SMS providers abstract routing.

You send a message → something happens → you don’t control:

* which route is used
* how pricing is applied
* why delivery changes

This is a black box.

---

BridgeXAPI follows a different model:

**Routing is explicit.**

You choose:

* `route_id`
* pricing profile
* delivery behavior

---

## What this project demonstrates

### 1. Direct control (route_id)

```python
from bridgexapi import BridgeXAPI

client = BridgeXAPI(api_key="YOUR_API_KEY")

client.send_sms(
    route_id=3,
    caller_id="BRIDGEXAPI",
    numbers=["31651860670"],
    message="Your verification code is 4839"
)
```

You decide:

* high-delivery routes (OTP)
* low-cost routes (bulk)

---

### 2. Live transparency

Every OTP response includes real infrastructure identifiers:

```json
{
  "bx_message_id": "BX-22229-1d5e5779b1904695",
  "order_id": "22229",
  "delivery_status_url": "https://hi.bridgexapi.io/api/v1/dlr/BX-22229-1d5e5779b1904695"
}
```

This enables:

* direct delivery tracking
* debugging real message flows
* visibility into the system

---

### 3. Failover logic (application layer)

Routing is no longer controlled by the provider.

You can implement your own logic:

```python
try:
    send_sms(route_id=1)  # premium route
except Exception:
    send_sms(route_id=3)  # fallback route
```

---

## API Endpoints

### Send OTP

```bash
POST /send-otp
```

Request:

```json
{
  "phone_number": "31651860670",
  "purpose": "login",
  "route_id": 3
}
```

Response:

```json
{
  "status": "otp_sent",
  "phone_number": "*******0670",
  "purpose": "login",
  "route_id": 3,
  "expires_in_seconds": 300,
  "cooldown_seconds": 45,
  "debug_code": "816369",
  "bx_message_id": "BX-22229-1d5e5779b1904695",
  "order_id": "22229",
  "delivery_status_url": "https://hi.bridgexapi.io/api/v1/dlr/BX-22229-1d5e5779b1904695"
}
```

---

### Verify OTP

```bash
POST /verify-otp
```

Request:

```json
{
  "phone_number": "31651860670",
  "code": "816369",
  "purpose": "login"
}
```

Response:

```json
{
  "status": "otp_verified",
  "phone_number": "*******0670",
  "purpose": "login",
  "verified": true
}
```

---

## Setup

### 1. Get API key

Go to:

https://dashboard.bridgexapi.io

Navigate to:

**Developer → Console**

---

### 2. Create `.env`

```env
BRIDGEXAPI_API_KEY=your_api_key
BRIDGEXAPI_BASE_URL=https://hi.bridgexapi.io
DEFAULT_CALLER_ID=BRIDGEXAPI

OTP_LENGTH=6
OTP_TTL_SECONDS=300
OTP_SEND_COOLDOWN_SECONDS=45
OTP_MAX_ATTEMPTS=5

DEBUG_OTP=true
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Run server

```bash
uvicorn app.main:app --reload
```

Open:

```
http://127.0.0.1:8000/docs
```

---

## Why in-memory storage?

This project uses an in-memory store intentionally.

The goal is to demonstrate:

* OTP lifecycle
* routing flow
* delivery tracking integration

Not persistence.

---

### Production replacement

Replace with:

* Redis
* database-backed store

---

## Notes

* `debug_code` is only for development
* disable in production (`DEBUG_OTP=false`)
* routing is explicit via `route_id`
* delivery tracking uses `bx_message_id`

---

## Docs

* https://docs.bridgexapi.io
* https://dashboard.bridgexapi.io

---

## What is BridgeXAPI

BridgeXAPI is a messaging infrastructure API.

* one endpoint
* multiple routes
* explicit routing control
* real pricing per destination

Built for systems, not dashboards.
