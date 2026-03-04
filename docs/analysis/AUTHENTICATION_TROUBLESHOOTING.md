# Authentication Troubleshooting Guide

## Issue: Authentication System Error (500)

**Error Code:** `AUTH_SYSTEM_ERROR`  
**Status:** 500 Internal Server Error  
**Message:** "Authentication system error"

---

## What This Error Means

This error indicates a **database/system issue**, NOT invalid credentials.

The authentication guard (`external-api-auth.guard.ts`) is trying to query the database to validate your API key/secret, but the database query is failing.

---

## Root Causes

1. **Database Connection Problem**
   - RPC Core cannot connect to its database
   - Database connection settings in `.env` are incorrect
   - Database server is not running

2. **Tenant Table Issue**
   - Tenant table doesn't exist
   - Tenant table has wrong schema
   - Database query is failing

3. **Service Not Running**
   - RPC Core service might not be fully started
   - Database connection pool not initialized

---

## How to Fix

### Step 1: Check Database Connection

Verify your `.env` file has correct database settings:

```env
DB_HOST=localhost
DB_PORT=5432
DB_USERNAME=your_username
DB_PASSWORD=your_password
DB_NAME=your_database
DB_SCHEMA=public
```

### Step 2: Check RPC Core Service

Ensure RPC Core is running and can connect to database:

```bash
# Check if service is running
curl http://localhost:3000/

# Check service logs for database errors
# Look for connection errors or query failures
```

### Step 3: Verify Tenant Table

Check if tenant table exists and has data:

```sql
-- Check if table exists
SELECT * FROM tenant LIMIT 1;

-- Check if your API key exists
SELECT id, name, "apiKey", enabled 
FROM tenant 
WHERE "apiKey" = 'SrzczBcbeIhLsT3QQcEBtfhzQWeqo9lmn4K-TI1rHs';
```

### Step 4: Test with Valid Credentials

Use the credentials from the test data (tenant ID 1):

**API Key:**
```
SrzczBcbeIhLsT3QQcEBtfhzQWeqo9lmn4K-TI1rHs
```

**API Secret:**
```
a9VBUUykzIpl0AMWV0YlZpxsNzOzRkqFMXw6-H1VxaRuEPPy1VPSqflyLDWrsFWJS2MjkU4-XWFzzQYgTlRTP2gxfL9ksqljUGZfrOfZz-JVFs4X
```

Set in `.env`:
```env
API_KEY=SrzczBcbeIhLsT3QQcEBtfhzQWeqo9lmn4K-TI1rHs
API_SECRET=a9VBUUykzIpl0AMWV0YlZpxsNzOzRkqFMXw6-H1VxaRuEPPy1VPSqflyLDWrsFWJS2MjkU4-XWFzzQYgTlRTP2gxfL9ksqljUGZfrOfZz-JVFs4X
```

---

## Authentication Flow

1. **Request comes in** with `x-api-key` and `x-api-secret` headers
2. **Guard extracts** credentials from headers
3. **Database query** to find tenant: `SELECT * FROM tenant WHERE apiKey = ? AND apiSecret = ?`
4. **If query fails** → 500 AUTH_SYSTEM_ERROR
5. **If tenant not found** → 401 Unauthorized
6. **If tenant disabled** → 403 Forbidden
7. **If successful** → Request proceeds

---

## Test Authentication

### Quick Test

```bash
curl -X GET http://localhost:3000/rpc/v1/purchase-orders/1 \
  -H "x-api-key: SrzczBcbeIhLsT3QQcEBtfhzQWeqo9lmn4K-TI1rHs" \
  -H "x-api-secret: a9VBUUykzIpl0AMWV0YlZpxsNzOzRkqFMXw6-H1VxaRuEPPy1VPSqflyLDWrsFWJS2MjkU4-XWFzzQYgTlRTP2gxfL9ksqljUGZfrOfZz-JVFs4X"
```

**Expected Results:**
- ✅ **200 OK** - Authentication successful
- ❌ **401 Unauthorized** - Invalid credentials
- ❌ **500 AUTH_SYSTEM_ERROR** - Database/system issue (current problem)

---

## Next Steps

1. **Check RPC Core logs** for database connection errors
2. **Verify database is accessible** from RPC Core service
3. **Check tenant table** exists and has correct schema
4. **Test database connection** directly from RPC Core

---

## Valid Test Credentials

From Postman environment and test data:

- **Tenant ID:** 1
- **Tenant Name:** Hartford Office Interiors
- **API Key:** `SrzczBcbeIhLsT3QQcEBtfhzQWeqo9lmn4K-TI1rHs`
- **API Secret:** `a9VBUUykzIpl0AMWV0YlZpxsNzOzRkqFMXw6-H1VxaRuEPPy1VPSqflyLDWrsFWJS2MjkU4-XWFzzQYgTlRTP2gxfL9ksqljUGZfrOfZz-JVFs4X`

These credentials are from the actual tenant data returned by the Record Grid MS in our tests.


