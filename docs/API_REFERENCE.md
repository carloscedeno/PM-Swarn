# RPC Core API Reference

**Version:** 2.0.0  
**Base URL:** `http://localhost:3000` (default)  
**API Version:** `/rpc/v1`

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Base URLs & Endpoints](#base-urls--endpoints)
4. [Purchase Order Endpoints](#purchase-order-endpoints)
5. [Acknowledgment Endpoints](#acknowledgment-endpoints)
6. [Request/Response Formats](#requestresponse-formats)
7. [Error Handling](#error-handling)
8. [Rate Limiting](#rate-limiting)
9. [Idempotency](#idempotency)
10. [Retry Logic](#retry-logic)

---

## Overview

RPC Core provides a RESTful API for integrating COR ERP with OrderBahn microservices. It handles Purchase Order (PO) and Acknowledgment (ACK) operations with automatic translation between COR ERP format and OrderBahn format.

### Key Features

- **Dual Authentication**: OAuth 2.0 Bearer tokens or API Key/Secret
- **Automatic Translation**: Converts between COR ERP and OrderBahn data formats
- **Idempotency**: Prevents duplicate processing with idempotency keys
- **Retry Logic**: Automatic retries with exponential backoff (3 attempts)
- **Rate Limiting**: Configurable rate limits per tenant
- **Comprehensive Logging**: Audit logs and telemetry for all operations

---

## Authentication

RPC Core supports two authentication methods:

### 1. OAuth 2.0 Bearer Token

```http
Authorization: Bearer <access_token>
```

**Getting a Token:**
```http
POST /oauth/token
Content-Type: application/json

{
  "client_id": "your_client_id",
  "client_secret": "your_client_secret",
  "grant_type": "client_credentials"
}
```

### 2. API Key/Secret

```http
x-api-key: <your_api_key>
x-api-secret: <your_api_secret>
```

**Note:** Both methods authenticate the tenant and extract tenant ID automatically.

---

## Base URLs & Endpoints

### Base URL
```
http://localhost:3000/rpc/v1
```

### Swagger Documentation
- **Interactive UI**: `http://localhost:3000/docs`
- **OpenAPI JSON**: `http://localhost:3000/docs-json`

---

## Purchase Order Endpoints

### Create Purchase Order

```http
POST /rpc/v1/purchase-orders
```

**Request Headers:**
```http
Authorization: Bearer <token>
# OR
x-api-key: <key>
x-api-secret: <secret>

x-idempotency-key: <optional_unique_key>
Content-Type: application/json
```

**Request Body:** See `CreatePurchaseOrderDto` in Swagger

**Response:** `201 Created`
```json
{
  "id": 12345,
  "poNumber": "PO-2025-001",
  "orderDate": "2025-01-15",
  "vendor": { ... },
  "lineItems": [ ... ],
  ...
}
```

**Error Responses:**
- `400 Bad Request` - Invalid data
- `401 Unauthorized` - Invalid credentials
- `409 Conflict` - Duplicate (idempotency check)

---

### Get Purchase Order by ID

```http
GET /rpc/v1/purchase-orders/:id
```

**Response:** `200 OK` with `PurchaseOrderResponseDto`

**Error Responses:**
- `404 Not Found` - PO not found
- `401 Unauthorized` - Invalid credentials

---

### Get Purchase Order by PO Number

```http
GET /rpc/v1/purchase-orders/by-po-number/:poNumber
```

**Example:**
```http
GET /rpc/v1/purchase-orders/by-po-number/PO-2025-001
```

**Response:** `200 OK` with `PurchaseOrderResponseDto`

---

### List Purchase Orders

```http
GET /rpc/v1/purchase-orders?page=1&limit=50&status=Active&fromDate=2025-01-01&toDate=2025-01-31
```

**Query Parameters:**
- `page` (optional, default: 1) - Page number
- `limit` (optional, default: 50, max: 100) - Items per page
- `status` (optional) - Filter by order status
- `fromDate` (optional) - Filter by PO date from (ISO 8601)
- `toDate` (optional) - Filter by PO date to (ISO 8601)

**Response:** `200 OK`
```json
{
  "data": [ ... ],
  "total": 150,
  "page": 1,
  "limit": 50
}
```

---

### Update Purchase Order

```http
PUT /rpc/v1/purchase-orders/:id
```

**Request Body:** `UpdatePurchaseOrderDto` (supports partial updates)

**Response:** `200 OK` with updated `PurchaseOrderResponseDto`

---

### Delete Purchase Order

```http
DELETE /rpc/v1/purchase-orders/:id
```

**Response:** `204 No Content`

**Error Responses:**
- `404 Not Found` - PO not found
- `401 Unauthorized` - Invalid credentials

---

## Acknowledgment Endpoints

### Create Acknowledgment

```http
POST /rpc/v1/purchase-orders/acks
```

**Request Body:** `CreateAcknowledgmentDto`

**Response:** `201 Created` with `AcknowledgmentResponseDto`

---

### Get Acknowledgment by ID

```http
GET /rpc/v1/purchase-orders/acks/:id
```

**Response:** `200 OK` with `AcknowledgmentResponseDto`

---

### Get Acknowledgment by ACK Number

```http
GET /rpc/v1/purchase-orders/acks/by-ack-number/:ackNumber
```

**Response:** `200 OK` with `AcknowledgmentResponseDto`

---

### List Acknowledgments

```http
GET /rpc/v1/purchase-orders/acks?page=1&limit=50&fromDate=2025-01-01&toDate=2025-01-31&poNumber=PO-2025-001
```

**Query Parameters:**
- `page` (optional, default: 1)
- `limit` (optional, default: 50, max: 100)
- `fromDate` (optional) - ISO 8601 format
- `toDate` (optional) - ISO 8601 format
- `poNumber` (optional) - Filter by PO Number

**Response:** `200 OK` with paginated list

---

### Update Acknowledgment

```http
PUT /rpc/v1/purchase-orders/acks/:id
```

**Request Body:** `UpdateAcknowledgmentDto`

**Response:** `200 OK` with updated `AcknowledgmentResponseDto`

---

## Request/Response Formats

### Purchase Order DTO Structure

```typescript
{
  poNumber: string;              // Required
  orderDate: string;             // ISO 8601 date
  vendor: {
    name: string;
    code?: string;
    address?: string;
    ...
  };
  lineItems: [{
    productNumber: string;
    quantity: number;
    productSell: number;
    ...
  }];
  shipping?: { ... };
  billing?: { ... };
  financials?: { ... };
  ...
}
```

### Acknowledgment DTO Structure

```typescript
{
  acknowledgmentNumber: string;   // Required
  poNumber: string;              // Required
  acknowledgmentDate: string;    // Required, ISO 8601
  vendor: { ... };
  lineItems: [ ... ];
  ...
}
```

**Full schemas available in Swagger UI at `/docs`**

---

## Error Handling

### Error Response Format

```json
{
  "statusCode": 400,
  "error": "Bad Request",
  "message": "Purchase Order validation failed: poNumber is required",
  "timestamp": "2025-01-15T10:30:00.000Z",
  "correlationId": "abc-123-def-456"
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| `400` | Bad Request - Invalid data or validation failed |
| `401` | Unauthorized - Invalid or missing credentials |
| `403` | Forbidden - Tenant mismatch or insufficient permissions |
| `404` | Not Found - Resource doesn't exist |
| `409` | Conflict - Duplicate request (idempotency) |
| `429` | Too Many Requests - Rate limit exceeded |
| `500` | Internal Server Error - Server-side error |
| `503` | Service Unavailable - Microservice unavailable |

---

## Rate Limiting

Rate limits are configured per tenant. Default limits:
- **100 requests per minute** per tenant
- **1000 requests per hour** per tenant

**Rate Limit Headers:**
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248000
```

**Rate Limit Exceeded Response:**
```json
{
  "statusCode": 429,
  "error": "Too Many Requests",
  "message": "Rate limit exceeded. Please try again later.",
  "retryAfter": 60
}
```

---

## Idempotency

Prevent duplicate processing by including an idempotency key:

```http
x-idempotency-key: unique-request-id-12345
```

**Behavior:**
- First request: Processed normally, response cached
- Duplicate request (same key within 24 hours): Returns cached response
- Idempotency key valid for **24 hours**

**Idempotency Response (Duplicate):**
```json
{
  "statusCode": 409,
  "error": "Conflict",
  "message": "Request already processed with this idempotency key",
  "cachedResponse": { ... }
}
```

---

## Retry Logic

**IN-38: Automatic Retry with Exponential Backoff**

Failed requests are automatically retried up to **3 times** with exponential backoff:

- **Attempt 1**: Immediate
- **Attempt 2**: After ~1 second
- **Attempt 3**: After ~2 seconds
- **Attempt 4**: After ~4 seconds

**Retry Conditions:**
- ✅ Network errors
- ✅ Timeouts (408)
- ✅ Rate limits (429)
- ✅ Server errors (5xx)
- ❌ Client errors (4xx, except 408, 429)

**Dead-Letter Queue:**
After 3 failed retries, the request is logged to the dead-letter queue for manual review.

---

## Additional Resources

- **Swagger UI**: Interactive API documentation at `/docs`
- **Integration Guide**: See `INTEGRATION_GUIDE.md`
- **Developer Guide**: See `DEVELOPER_GUIDE.md`
- **Postman Collections**: See `postman-collections/` directory

---

*Last Updated: 2025-01-15*  
*Version: 2.0.0*

