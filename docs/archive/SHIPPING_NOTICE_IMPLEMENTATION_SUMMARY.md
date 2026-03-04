# Shipping Notice Implementation Summary (IN-46)

**Status:** ✅ Implementation Complete (Pending DB Configuration)  
**Date:** December 2025  
**Record Type ID:** 14 ("Shipping Notice")

---

## What Was Implemented

### 1. DTOs (Data Transfer Objects)
- ✅ `CreateShippingNoticeDto` - Request body for creating shipping notices
- ✅ `ShippingNoticeResponseDto` - Response format
- ✅ Supporting DTOs:
  - `ShippingAddressDto`
  - `FinancialDto`
  - `ShipmentDto`
  - `AdditionalInformationDto`
  - `ShippingNoticeLineItemDto`
- ✅ Enums:
  - `RecordStatus` (Draft, Submitted, Confirmed, Cancelled)
  - `FulfillmentStatus` (In Progress, Shipped, Delivered, Delayed)
  - `ShipmentType` (LTL, FTL, Parcel, Air, Ocean)
  - `ShipmentStatus` (Processing, In Transit, Delivered, Exception)

**Files:**
- `src/context/rpc-core/dto/create-shipping-notice.dto.ts`
- `src/context/rpc-core/dto/shipping-notice-response.dto.ts`

### 2. Mappers
- ✅ `ShippingNoticeToRecordMapper` - Maps DTO → RecordHeader format
- ✅ `RecordToShippingNoticeMapper` - Maps RecordHeader → Response DTO

**Files:**
- `src/context/rpc-core/mappers/shipping-notice-to-record.mapper.ts`
- `src/context/rpc-core/mappers/record-to-shipping-notice.mapper.ts`

### 3. Service Layer
- ✅ `createShippingNotices()` method in `RpcCoreService`
  - Accepts array of DTOs (per schema)
  - Loops through array and creates one record at a time
  - Validates line items
  - Creates record via Record Grid Client
  - Creates line items via Line Items Client
  - Emits telemetry events
  - Returns array of results (partial success supported)

**File:**
- `src/context/rpc-core/rpc-core.service.ts`

### 4. Controller
- ✅ `POST /rpc/v1/purchase-orders/shipping-notices` endpoint
  - Accepts array of `CreateShippingNoticeDto[]`
  - Returns array of `ShippingNoticeResponseDto[]`
  - Validates tenant authentication
  - Validates array is not empty

**File:**
- `src/context/rpc-core/rpc-core.controller.ts`

### 5. Module Configuration
- ✅ Registered mappers in `RpcCoreModule`
- ✅ Injected mappers into service

**File:**
- `src/context/rpc-core/rpc-core.module.ts`

### 6. Integration Test Script
- ✅ `scripts/test-shipping-notice-create.ts`
  - Test 1: Create with full payload
  - Test 2: Create with minimal payload
  - Test 3: Reject empty array

---

## API Endpoint

### POST /rpc/v1/purchase-orders/shipping-notices

**Request Body:** Array of shipping notice objects
```json
[
  {
    "acknowledgmentNumber": "ACK-12345",
    "shipDate": "2025-12-01",
    "shippingAddress": {
      "address1": "123 Main St",
      "city": "Test City",
      "state": "TS",
      "zip": "12345"
    },
    "lineItems": [
      {
        "catalogCode": "CAT-001",
        "productNumber": "PROD-001",
        "quantity": 5,
        "productDescription": "Office Chair",
        "productSell": 299.99
      }
    ],
    "recordStatus": "Submitted",
    "fulfillmentStatus": "Shipped",
    "financial": {
      "freightCost": 50.0,
      "handlingFee": 10.0,
      "totalCost": 60.0
    },
    "shipments": [
      {
        "shipmentNumber": 1,
        "carrier": "UPS",
        "trackingNumber": "1Z999AA10123456784",
        "shipmentType": "Parcel",
        "status": "In Transit"
      }
    ]
  }
]
```

**Response:** Array of created shipping notices
```json
[
  {
    "id": 12345,
    "shippingNoticeNumber": "SN-ACK-12345-1733097600000",
    "acknowledgmentNumber": "ACK-12345",
    "shipDate": "2025-12-01",
    "shippingAddress": { ... },
    "lineItems": [ ... ],
    "shipments": [ ... ],
    "tenantId": 1,
    "createdAt": "2025-12-01T12:00:00.000Z",
    "updatedAt": "2025-12-01T12:00:00.000Z"
  }
]
```

---

## What Still Needs To Be Done

### 1. Database Configuration (BLOCKING)
The following fields need to be configured in OrderBahn for `record_type.id = 14`:

**Required Fields:**
- `"Acknowledgment Number"` (string, required)
- `"Ship Date"` (date, required)
- `"Shipping Address"` (object/JSON, required)

**Optional Fields:**
- `"Record Status"` (dropdown, optional) - needs listTypeId configuration
- `"Fulfillment Status"` (dropdown, optional) - needs listTypeId configuration
- `"Target Tenant"` (string, optional)
- `"Notice Attachment"` (string, optional)
- `"Financial"` (object/JSON, optional)
- `"Shipments"` (object/JSON, optional)

**Line Items:**
- Identify or create `lineItemsByTypeId` for Shipping Notice line items
- Current implementation reuses PO line items structure

### 2. Enum/List Value Mappings (BLOCKING)
The mappers use placeholder list value IDs that need to be updated:

**Record Status:**
- Draft → 782 (placeholder)
- Submitted → 783 (placeholder)
- Confirmed → 1136 (placeholder)
- Cancelled → 784 (placeholder)

**Fulfillment Status:**
- In Progress → 1001 (placeholder)
- Shipped → 1002 (placeholder)
- Delivered → 1003 (placeholder)
- Delayed → 1004 (placeholder)

**Action:** Query DB or configure new list types, then update mapper constants.

### 3. ACK Validation (TODO in Service)
Currently skipped to allow testing. Need to implement:
- Query `record_header` for ACK with matching `acknowledgmentNumber`
- Verify ACK exists and belongs to tenant
- Return 404 if not found

**File:** `src/context/rpc-core/rpc-core.service.ts` (line ~1035)

### 4. Testing
- ✅ Integration test script created
- ⚠️ Cannot test until DB fields are configured
- ⚠️ Need to verify field names match actual DB configuration

---

## How To Test (Once DB is Configured)

### 1. Start the application
```bash
yarn start:dev
```

### 2. Run the integration test
```bash
yarn ts-node scripts/test-shipping-notice-create.ts
```

### 3. Check Swagger UI
Navigate to `http://localhost:3000/docs` and find the `POST /rpc/v1/purchase-orders/shipping-notices` endpoint.

---

## Field Mapping Strategy

### Current Approach (Placeholder)
- Simple fields: Direct mapping to `additionalFields` with field names
- Complex objects: JSON.stringify() and store as string
  - `shippingAddress` → stored as JSON string
  - `financial` → stored as JSON string
  - `shipments[]` → stored as JSON array string

### Alternative Approach (If Needed)
- Use `objectValues` pattern (like PO `ShippingRequirements`)
- Split complex objects into individual fields
- Decision depends on actual DB field configuration

---

## Telemetry Events

The implementation emits the following telemetry events:

1. `shipping_notice_create_started`
   - tenantId
   - acknowledgmentNumber
   - shipDate
   - lineItemCount
   - shipmentCount

2. `shipping_notice_create_succeeded`
   - tenantId
   - recordId
   - acknowledgmentNumber
   - recordNumber
   - lineItemCount

3. `shipping_notice_create_failed`
   - tenantId
   - acknowledgmentNumber
   - error

---

## Next Steps

1. **Coordinate with DB/OrderBahn team** to configure fields for record_type 14
2. **Update mapper field names** once actual DB configuration is known
3. **Update enum list value IDs** once list types are configured
4. **Implement ACK validation** in service method
5. **Test with real data** using the integration test script
6. **Adjust field mappings** based on test results
7. **Document final field mappings** for future reference

---

## Files Changed

### Created
- `src/context/rpc-core/dto/create-shipping-notice.dto.ts`
- `src/context/rpc-core/dto/shipping-notice-response.dto.ts`
- `src/context/rpc-core/mappers/shipping-notice-to-record.mapper.ts`
- `src/context/rpc-core/mappers/record-to-shipping-notice.mapper.ts`
- `scripts/test-shipping-notice-create.ts`
- `docs/SHIPPING_NOTICE_IMPLEMENTATION_PLAN.md`
- `docs/SHIPPING_NOTICE_IMPLEMENTATION_SUMMARY.md`

### Modified
- `src/context/rpc-core/dto/index.ts` - Added exports
- `src/context/rpc-core/rpc-core.service.ts` - Added `createShippingNotices()` method
- `src/context/rpc-core/rpc-core.controller.ts` - Added `POST /shipping-notices` endpoint
- `src/context/rpc-core/rpc-core.module.ts` - Registered mappers

---

## Known Limitations

1. **No DB field validation** - Field names are placeholders
2. **No ACK validation** - Skipped to allow testing
3. **Partial success handling** - If some notices fail, successful ones are still returned
4. **Line items type** - Currently reuses PO line items structure
5. **No idempotency** - Unlike PO/ACK, no idempotency key support yet

---

## References

- Implementation Plan: `docs/SHIPPING_NOTICE_IMPLEMENTATION_PLAN.md`
- Schema: Provided JSON schema (see plan document)
- Jira Ticket: IN-46
- DB Check Script: `scripts/check-shipping-notice-schema.ts`





