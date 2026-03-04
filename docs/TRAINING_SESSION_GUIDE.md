# RPC Core Training Session Guide

**Duration:** 2 hours  
**Target Audience:** Integration developers, API consumers  
**Version:** 2.0.0

---

## Session Overview

This training session provides hands-on experience with the RPC Core API, covering authentication, creating Purchase Orders, handling errors, and best practices.

---

## Agenda

| Time | Topic | Duration |
|------|-------|-----------|
| 0:00 | Introduction & Overview | 15 min |
| 0:15 | Authentication Setup | 20 min |
| 0:35 | API Usage & Examples | 30 min |
| 1:05 | Hands-on Exercise | 30 min |
| 1:35 | Error Handling & Best Practices | 20 min |
| 1:55 | Q&A | 15 min |

---

## Section 1: Introduction & Overview (15 min)

### What is RPC Core?

RPC Core is an integration layer that:
- Connects COR ERP to OrderBahn microservices
- Translates data between formats automatically
- Provides RESTful API for Purchase Orders and Acknowledgments
- Handles authentication, retries, and error handling

### Key Features

- ✅ Dual authentication (OAuth 2.0 + API Key/Secret)
- ✅ Automatic retry with exponential backoff
- ✅ Idempotency support
- ✅ Comprehensive logging and telemetry
- ✅ Rate limiting

### Use Cases

1. **Create Purchase Orders** from COR ERP
2. **Retrieve Acknowledgments** from OrderBahn
3. **Update Purchase Orders** with changes
4. **List and filter** Purchase Orders

---

## Section 2: Authentication Setup (20 min)

### Option 1: API Key/Secret

**Step 1:** Obtain credentials from administrator

**Step 2:** Include in request headers
```http
x-api-key: your-api-key
x-api-secret: your-api-secret
```

**Demo:**
```bash
curl -X GET http://localhost:3000/rpc/v1/purchase-orders \
  -H "x-api-key: demo-key" \
  -H "x-api-secret: demo-secret"
```

### Option 2: OAuth 2.0

**Step 1:** Get access token
```bash
curl -X POST http://localhost:3000/oauth/token \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "grant_type": "client_credentials"
  }'
```

**Step 2:** Use Bearer token
```http
Authorization: Bearer <access_token>
```

**Demo:**
```bash
curl -X GET http://localhost:3000/rpc/v1/purchase-orders \
  -H "Authorization: Bearer <token>"
```

### Hands-on: Try Both Methods

1. Test API Key/Secret authentication
2. Test OAuth 2.0 authentication
3. Compare responses

---

## Section 3: API Usage & Examples (30 min)

### Creating a Purchase Order

**Request:**
```bash
curl -X POST http://localhost:3000/rpc/v1/purchase-orders \
  -H "Content-Type: application/json" \
  -H "x-api-key: demo-key" \
  -H "x-api-secret: demo-secret" \
  -H "x-idempotency-key: unique-123" \
  -d '{
    "poNumber": "PO-2025-001",
    "orderDate": "2025-01-15",
    "vendor": {
      "name": "Acme Corp",
      "code": "ACME001"
    },
    "lineItems": [
      {
        "productNumber": "PROD-123",
        "quantity": 10,
        "productSell": 99.99
      }
    ]
  }'
```

**Response:**
```json
{
  "id": 12345,
  "poNumber": "PO-2025-001",
  "status": "Active",
  ...
}
```

### Retrieving a Purchase Order

**By ID:**
```bash
curl -X GET http://localhost:3000/rpc/v1/purchase-orders/12345 \
  -H "x-api-key: demo-key" \
  -H "x-api-secret: demo-secret"
```

**By PO Number:**
```bash
curl -X GET http://localhost:3000/rpc/v1/purchase-orders/by-po-number/PO-2025-001 \
  -H "x-api-key: demo-key" \
  -H "x-api-secret: demo-secret"
```

### Listing Purchase Orders

```bash
curl -X GET "http://localhost:3000/rpc/v1/purchase-orders?page=1&limit=50&status=Active" \
  -H "x-api-key: demo-key" \
  -H "x-api-secret: demo-secret"
```

### Updating a Purchase Order

```bash
curl -X PUT http://localhost:3000/rpc/v1/purchase-orders/12345 \
  -H "Content-Type: application/json" \
  -H "x-api-key: demo-key" \
  -H "x-api-secret: demo-secret" \
  -d '{
    "status": "Completed"
  }'
```

---

## Section 4: Hands-on Exercise (30 min)

### Exercise 1: Create a Purchase Order

**Task:**
1. Create a Purchase Order with:
   - PO Number: `PO-TRAINING-001`
   - Order Date: Today's date
   - Vendor: Your choice
   - At least 2 line items

2. Save the returned ID

3. Retrieve the PO using the ID

**Solution:**
[Provide solution after exercise]

### Exercise 2: Handle Errors

**Task:**
1. Try to create a PO without required fields
2. Observe the error response
3. Fix and retry

**Expected Error:**
```json
{
  "statusCode": 400,
  "error": "Bad Request",
  "message": "Purchase Order validation failed: poNumber is required"
}
```

### Exercise 3: Use Idempotency

**Task:**
1. Create a PO with idempotency key: `training-exercise-123`
2. Create the same PO again with the same idempotency key
3. Observe the 409 Conflict response with cached data

---

## Section 5: Error Handling & Best Practices (20 min)

### Common Errors

| Code | Error | Solution |
|------|-------|----------|
| 400 | Bad Request | Check required fields, validate data |
| 401 | Unauthorized | Verify credentials |
| 404 | Not Found | Check ID/PO Number |
| 409 | Conflict | Duplicate idempotency key |
| 429 | Rate Limited | Slow down requests, implement backoff |
| 500 | Server Error | Retry with exponential backoff |

### Best Practices

1. **Always use idempotency keys**
   ```javascript
   headers: {
     'x-idempotency-key': `${poNumber}-${timestamp}`
   }
   ```

2. **Handle errors gracefully**
   ```javascript
   if (response.status === 409) {
     // Duplicate - use cached response
   } else if (response.status === 429) {
     // Rate limited - retry after delay
   }
   ```

3. **Use pagination for lists**
   ```javascript
   GET /rpc/v1/purchase-orders?page=1&limit=50
   ```

4. **Monitor rate limits**
   ```javascript
   const remaining = response.headers.get('X-RateLimit-Remaining');
   ```

5. **Validate data before sending**
   ```javascript
   if (!poData.poNumber || !poData.orderDate) {
     throw new Error('Missing required fields');
   }
   ```

---

## Section 6: Q&A (15 min)

### Common Questions

**Q: How long are idempotency keys cached?**  
A: 24 hours

**Q: What's the rate limit?**  
A: 100 requests/minute per tenant (configurable)

**Q: Does retry logic apply to all requests?**  
A: Yes, automatically for all HTTP calls to microservices

**Q: How do I get OAuth credentials?**  
A: Contact your administrator

**Q: Can I use both authentication methods?**  
A: Yes, but use one per request

---

## Resources

- **API Reference:** `docs/API_REFERENCE.md`
- **Integration Guide:** `docs/INTEGRATION_GUIDE.md`
- **Swagger UI:** `http://localhost:3000/docs`
- **Postman Collections:** `postman-collections/` directory

---

## Follow-up

After the training:
1. Review the documentation
2. Try the exercises again
3. Integrate into your application
4. Contact support if needed

---

*Training Guide Version: 2.0.0*  
*Last Updated: January 15, 2025*

