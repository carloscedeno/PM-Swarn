# RPC Core Quick Reference

**Version:** 2.0.0  
**One-page cheat sheet for developers**

---

## Base URL

```
http://localhost:3000/rpc/v1
```

---

## Authentication

### API Key/Secret
```http
x-api-key: <key>
x-api-secret: <secret>
```

### OAuth 2.0
```http
Authorization: Bearer <token>
```

**Get Token:**
```bash
POST /oauth/token
{
  "client_id": "...",
  "client_secret": "...",
  "grant_type": "client_credentials"
}
```

---

## Purchase Orders

### Create
```http
POST /rpc/v1/purchase-orders
x-idempotency-key: <unique-key>
```

### Get by ID
```http
GET /rpc/v1/purchase-orders/:id
```

### Get by PO Number
```http
GET /rpc/v1/purchase-orders/by-po-number/:poNumber
```

### List
```http
GET /rpc/v1/purchase-orders?page=1&limit=50&status=Active
```

### Update
```http
PUT /rpc/v1/purchase-orders/:id
```

### Delete
```http
DELETE /rpc/v1/purchase-orders/:id
```

---

## Acknowledgments

### Create
```http
POST /rpc/v1/purchase-orders/acks
```

### Get by ID
```http
GET /rpc/v1/purchase-orders/acks/:id
```

### Get by ACK Number
```http
GET /rpc/v1/purchase-orders/acks/by-ack-number/:ackNumber
```

### List
```http
GET /rpc/v1/purchase-orders/acks?page=1&limit=50
```

### Update
```http
PUT /rpc/v1/purchase-orders/acks/:id
```

---

## Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| 400 | Bad Request | Check data format |
| 401 | Unauthorized | Verify credentials |
| 404 | Not Found | Check ID/Number |
| 409 | Conflict | Duplicate (idempotency) |
| 429 | Rate Limited | Slow down, retry |
| 500 | Server Error | Retry with backoff |

---

## Headers

```http
Content-Type: application/json
x-api-key: <key>
x-api-secret: <secret>
x-idempotency-key: <unique-key>  # Optional but recommended
```

---

## Sample Request

```bash
curl -X POST http://localhost:3000/rpc/v1/purchase-orders \
  -H "Content-Type: application/json" \
  -H "x-api-key: your-key" \
  -H "x-api-secret: your-secret" \
  -H "x-idempotency-key: unique-123" \
  -d '{
    "poNumber": "PO-2025-001",
    "orderDate": "2025-01-15",
    "vendor": {
      "name": "Acme Corp"
    },
    "lineItems": [{
      "productNumber": "PROD-123",
      "quantity": 10,
      "productSell": 99.99
    }]
  }'
```

---

## Features

- ✅ **Retry Logic**: Automatic 3 retries with exponential backoff
- ✅ **Idempotency**: 24-hour cache window
- ✅ **Rate Limiting**: 100 req/min per tenant
- ✅ **Telemetry**: CloudWatch logging

---

## Documentation

- **API Reference**: `docs/API_REFERENCE.md`
- **Integration Guide**: `docs/INTEGRATION_GUIDE.md`
- **Swagger UI**: `/docs`

---

## Support

- **Technical Support**: Contact your integration team
- **Swagger**: `http://localhost:3000/docs`

---

*Version: 2.0.0 | Last Updated: 2025-01-15*

