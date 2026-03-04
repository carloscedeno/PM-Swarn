# Purchase Order Test Values for Record Headers Endpoint

## Endpoint Details

**URL:** `POST http://localhost:4001/record-headers/v3/many?limit=1&offset=0&returnListValues=false`

## How to Get Test Values

### 1. Get Record ID from Database

Run this SQL query in your database:

```sql
SELECT 
  id,
  "recordNumber",
  "Record_type_id" as "recordTypeId",
  "tenant_id" as "tenantId",
  "createdAt"
FROM record_header
WHERE "Record_type_id" = 30  -- 30 = Purchase Order
ORDER BY "createdAt" DESC
LIMIT 10;
```

### 2. Example Test Values (Based on Codebase)

From the codebase, I found these example values used in tests:

| Record ID | Tenant ID | Record Type ID | Source |
|-----------|-----------|----------------|--------|
| 42091 | 1 | 30 | `scripts/test-get-record.ts` |
| 89261 | 1 | 30 | `endpoint-testing/ENDPOINT_TEST_RESULTS.md` |
| 89262 | 1 | 30 | `endpoint-testing/ENDPOINT_TEST_RESULTS.md` |

**Note:** These are example values from test files. Use actual IDs from your database.

## Complete Request Example

### Headers
```json
{
  "Content-Type": "application/json",
  "x-tenant-id": "1",
  "tenantId": "1",
  "userId": "1",
  "x-user-id": "1",
  "role_id": "1"
}
```

### Request Body
```json
{
  "tenantId": 1,
  "recordTypeId": 30,
  "filters": {
    "ids": [42091]
  }
}
```

**Replace `42091` with an actual Record ID from your database.**

## Quick Test Script

Run this script to get PO records from your database:

```bash
yarn ts-node scripts/get-po-records-for-testing.ts
```

**Prerequisites:**
- Set environment variables in `.env` file:
  - `DB_HOST` (default: localhost)
  - `DB_PORT` (default: 5432, or 5433 for SSH tunnel)
  - `DB_USERNAME`
  - `DB_PASSWORD`
  - `DB_NAME`

## Manual Database Query

If you have direct database access, run:

```sql
-- Get latest 5 Purchase Orders
SELECT 
  id as "recordId",
  "recordNumber",
  "tenant_id" as "tenantId",
  "Record_type_id" as "recordTypeId",
  "createdAt"
FROM record_header
WHERE "Record_type_id" = 30
ORDER BY "createdAt" DESC
LIMIT 5;
```

## cURL Command Example

```bash
curl -X POST "http://localhost:4001/record-headers/v3/many?limit=1&offset=0&returnListValues=false" \
  -H "Content-Type: application/json" \
  -H "x-tenant-id: 1" \
  -H "tenantId: 1" \
  -H "userId: 1" \
  -H "x-user-id: 1" \
  -H "role_id: 1" \
  -d '{
    "tenantId": 1,
    "recordTypeId": 30,
    "filters": {
      "ids": [42091]
    }
  }'
```

**Remember to replace `42091` with a valid Record ID from your database!**

## Record Type IDs Reference

- **30** = Purchase Order (PO)
- **7** = Acknowledgment (ACK)
- **14** = Shipping Notice

## Troubleshooting

### No Records Found
If you get "No records found":
1. Check if you have any Purchase Orders in the database
2. Verify the `Record_type_id` is 30
3. Check tenant ID matches your records

### Connection Issues
If database connection fails:
1. Check SSH tunnel is running (if using remote DB)
2. Verify `.env` file has correct credentials
3. Test connection: `yarn ts-node scripts/verify-db-tunnel.ts`



