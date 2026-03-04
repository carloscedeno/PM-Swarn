# RPC Core Integration Guide

**Version:** 2.0.0  
**Target Audience:** Integration developers, API consumers

## Table of Contents

1. [Getting Started](#getting-started)
2. [Authentication Setup](#authentication-setup)
3. [First API Call](#first-api-call)
4. [Common Integration Patterns](#common-integration-patterns)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)
7. [Support Resources](#support-resources)

---

## Getting Started

### Prerequisites

- API credentials (API Key/Secret or OAuth Client ID/Secret)
- HTTP client library (curl, Postman, or your preferred HTTP client)
- Understanding of REST APIs and JSON

### Base URL

```
Production: https://api.your-domain.com/rpc/v1
Development: http://localhost:3000/rpc/v1
```

---

## Authentication Setup

### Option 1: API Key/Secret (Recommended for Server-to-Server)

1. **Obtain Credentials**
   - Contact your administrator for API Key and Secret
   - Credentials are tenant-specific

2. **Include in Headers**
   ```http
   x-api-key: your-api-key-here
   x-api-secret: your-api-secret-here
   ```

### Option 2: OAuth 2.0 (Recommended for Client Applications)

1. **Obtain OAuth Credentials**
   - Client ID
   - Client Secret

2. **Get Access Token**
   ```bash
   curl -X POST http://localhost:3000/oauth/token \
     -H "Content-Type: application/json" \
     -d '{
       "client_id": "your_client_id",
       "client_secret": "your_client_secret",
       "grant_type": "client_credentials"
     }'
   ```

3. **Use Bearer Token**
   ```http
   Authorization: Bearer <access_token>
   ```

---

## First API Call

### Example: Create a Purchase Order

```bash
curl -X POST http://localhost:3000/rpc/v1/purchase-orders \
  -H "Content-Type: application/json" \
  -H "x-api-key: your-api-key" \
  -H "x-api-secret: your-api-secret" \
  -H "x-idempotency-key: unique-request-123" \
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

### Response

```json
{
  "id": 12345,
  "poNumber": "PO-2025-001",
  "orderDate": "2025-01-15",
  "status": "Active",
  "vendor": {
    "name": "Acme Corp",
    "code": "ACME001"
  },
  "lineItems": [
    {
      "id": 67890,
      "productNumber": "PROD-123",
      "quantity": 10,
      "productSell": 99.99
    }
  ],
  "createdAt": "2025-01-15T10:30:00.000Z"
}
```

---

## Common Integration Patterns

### Pattern 1: Create and Retrieve

```javascript
// 1. Create PO
const createResponse = await fetch('/rpc/v1/purchase-orders', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'x-api-key': apiKey,
    'x-api-secret': apiSecret,
    'x-idempotency-key': generateIdempotencyKey()
  },
  body: JSON.stringify(poData)
});

const po = await createResponse.json();

// 2. Retrieve PO by ID
const getResponse = await fetch(`/rpc/v1/purchase-orders/${po.id}`, {
  headers: {
    'x-api-key': apiKey,
    'x-api-secret': apiSecret
  }
});

const retrievedPo = await getResponse.json();
```

### Pattern 2: List with Pagination

```javascript
let page = 1;
const limit = 50;
let allPos = [];

while (true) {
  const response = await fetch(
    `/rpc/v1/purchase-orders?page=${page}&limit=${limit}`,
    {
      headers: {
        'x-api-key': apiKey,
        'x-api-secret': apiSecret
      }
    }
  );
  
  const data = await response.json();
  allPos = allPos.concat(data.data);
  
  if (data.data.length < limit) break; // Last page
  page++;
}
```

### Pattern 3: Update with Retry

```javascript
async function updateWithRetry(poId, updateData, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetch(`/rpc/v1/purchase-orders/${poId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': apiKey,
          'x-api-secret': apiSecret
        },
        body: JSON.stringify(updateData)
      });
      
      if (response.ok) {
        return await response.json();
      }
      
      // Don't retry on client errors
      if (response.status >= 400 && response.status < 500) {
        throw new Error(`Client error: ${response.status}`);
      }
      
      // Retry on server errors
      if (attempt < maxRetries) {
        await sleep(1000 * attempt); // Exponential backoff
        continue;
      }
      
      throw new Error(`Server error: ${response.status}`);
    } catch (error) {
      if (attempt === maxRetries) throw error;
      await sleep(1000 * attempt);
    }
  }
}
```

### Pattern 4: Idempotent Creation

```javascript
// Generate a unique idempotency key
function generateIdempotencyKey(poNumber, timestamp) {
  return `${poNumber}-${timestamp}`;
}

// Create PO with idempotency
const idempotencyKey = generateIdempotencyKey('PO-2025-001', Date.now());

const response = await fetch('/rpc/v1/purchase-orders', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'x-api-key': apiKey,
    'x-api-secret': apiSecret,
    'x-idempotency-key': idempotencyKey
  },
  body: JSON.stringify(poData)
});

// If duplicate, returns 409 with cached response
if (response.status === 409) {
  const cached = await response.json();
  console.log('Duplicate request, using cached response');
}
```

---

## Best Practices

### 1. Always Use Idempotency Keys

```javascript
// ✅ Good
headers: {
  'x-idempotency-key': `${poNumber}-${timestamp}`
}

// ❌ Bad
// Missing idempotency key - risk of duplicates
```

### 2. Handle Errors Gracefully

```javascript
try {
  const response = await fetch('/rpc/v1/purchase-orders', { ... });
  
  if (!response.ok) {
    const error = await response.json();
    console.error('API Error:', error.message);
    
    // Handle specific errors
    if (response.status === 409) {
      // Duplicate - use cached response
    } else if (response.status === 429) {
      // Rate limited - retry after delay
    }
  }
} catch (error) {
  console.error('Network error:', error);
  // Implement retry logic
}
```

### 3. Use Pagination for Large Lists

```javascript
// ✅ Good - Use pagination
GET /rpc/v1/purchase-orders?page=1&limit=50

// ❌ Bad - Don't fetch all at once
GET /rpc/v1/purchase-orders?limit=10000
```

### 4. Validate Data Before Sending

```javascript
// ✅ Good - Validate required fields
if (!poData.poNumber || !poData.orderDate) {
  throw new Error('Missing required fields');
}

// ❌ Bad - Send invalid data
fetch('/rpc/v1/purchase-orders', {
  body: JSON.stringify({}) // Missing required fields
});
```

### 5. Monitor Rate Limits

```javascript
const response = await fetch('/rpc/v1/purchase-orders', { ... });

// Check rate limit headers
const remaining = response.headers.get('X-RateLimit-Remaining');
if (parseInt(remaining) < 10) {
  console.warn('Rate limit low, slowing down requests');
}
```

---

## Troubleshooting

### Common Issues

#### 1. Authentication Errors (401)

**Problem:** `401 Unauthorized`

**Solutions:**
- Verify API key/secret are correct
- Check token hasn't expired (OAuth)
- Ensure credentials match the tenant

#### 2. Validation Errors (400)

**Problem:** `400 Bad Request` with validation message

**Solutions:**
- Check required fields are present
- Verify date formats (ISO 8601)
- Ensure numeric fields are numbers, not strings

#### 3. Not Found (404)

**Problem:** `404 Not Found` when retrieving PO

**Solutions:**
- Verify PO ID is correct
- Check PO belongs to your tenant
- Ensure PO wasn't deleted

#### 4. Rate Limit Exceeded (429)

**Problem:** `429 Too Many Requests`

**Solutions:**
- Implement exponential backoff
- Reduce request frequency
- Use batch operations where possible

#### 5. Service Unavailable (503)

**Problem:** `503 Service Unavailable`

**Solutions:**
- Retry with exponential backoff (automatic)
- Check system status
- Contact support if persistent

---

## Support Resources

### Documentation
- **API Reference**: See `API_REFERENCE.md`
- **Swagger UI**: `http://localhost:3000/docs`
- **Architecture**: See `ARCHITECTURE.md`

### Tools
- **Postman Collections**: See `postman-collections/` directory
- **Swagger Test Guide**: See `SWAGGER_TEST_GUIDE.md`

### Getting Help
- **Technical Support**: Contact your integration team
- **Issues**: Report via your support channel
- **Feature Requests**: Submit through your product team

---

*Last Updated: 2025-01-15*  
*Version: 2.0.0*

