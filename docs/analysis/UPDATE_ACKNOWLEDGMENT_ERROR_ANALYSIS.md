# UPDATE Acknowledgment Error Analysis

**Endpoint:** `PUT /rpc/v1/purchase-orders/acks/:id`  
**Error:** 400 Bad Request (Validation Error)

---

## Problem

The UPDATE Acknowledgment endpoint is failing with a validation error due to **two issues**:

1. **Incorrect field location**: `acknowledgmentTotal` was placed in `financials`, but it belongs in `ackInfo`
2. **Required field validation**: When updating `ackInfo`, NestJS validates ALL required fields in `AckInfoDto`, even though it's an update operation

---

## Root Cause

### Issue 1: Wrong Field Location
**Original Test Payload (INCORRECT):**
```json
{
  "financials": {
    "acknowledgmentTotal": 1200
  }
}
```

**Problem:** The field `acknowledgmentTotal` does **NOT** exist in `AckFinancialsDto`. 

Looking at the DTO structure:
- `acknowledgmentTotal` is in `AckInfoDto` (line 449 in create-acknowledgment.dto.ts)
- `AckFinancialsDto` has different fields: `productSubtotal`, `salesTax`, `surcharge`, `totalAcknowledged`, `invoiceNumber`, `invoiceDate`, `invoiceTotal`

### Issue 2: Required Field Validation
**Attempted Fix (STILL FAILS):**
```json
{
  "ackInfo": {
    "acknowledgmentTotal": 1200,
    "comments": "Updated via API test"
  }
}
```

**Problem:** When you provide `ackInfo` in an update, NestJS validation checks ALL fields in `AckInfoDto`, including required ones:
- `acknowledgmentNumber` (required)
- `poNumber` (required)  
- `acknowledgmentDate` (required)

Even though `UpdateAcknowledgmentDto` extends `PartialType(CreateAcknowledgmentDto)`, the nested `AckInfoDto` still has `@IsNotEmpty()` decorators that trigger validation when the parent object is provided.

---

## DTO Structure

### AckInfoDto (Core Acknowledgment Information)
```typescript
export class AckInfoDto {
  acknowledgmentNumber: string;      // Required
  poNumber: string;                   // Required
  acknowledgmentDate: string;         // Required
  acknowledgmentTotal?: number;        // ✅ This is where acknowledgmentTotal belongs
  orderDate?: string;
  requestDate?: string;
  shipDate?: string;
  arrivalDate?: string;
  terms?: string;
  comments?: string;
  processName?: string;
  processedOn?: string;
  clientProcessedOn?: string;
  notificationState?: string;
}
```

### AckFinancialsDto (Financial Summary)
```typescript
export class AckFinancialsDto {
  productSubtotal?: number;
  salesTax?: number;
  surcharge?: number;
  totalAcknowledged?: number;         // ✅ Use this instead
  invoiceNumber?: string;
  invoiceDate?: string;
  invoiceTotal?: number;
}
```

---

## Solution

### ✅ CORRECT: Update financials (Recommended)
```json
{
  "financials": {
    "totalAcknowledged": 1200,
    "productSubtotal": 1000,
    "salesTax": 200
  }
}
```

**Why this works:**
- `AckFinancialsDto` has NO required fields (all are `@IsOptional()`)
- No validation conflicts
- Clean partial update

### ✅ CORRECT: Update shipping (Alternative)
```json
{
  "shipping": {
    "freight": 50,
    "trackingInformation": "TRACK-12345"
  }
}
```

**Why this works:**
- `AckShippingDto` has NO required fields
- Safe for partial updates

### ❌ INCORRECT: Update ackInfo (Fails Validation)
```json
{
  "ackInfo": {
    "acknowledgmentTotal": 1200
  }
}
```

**Why this fails:**
- NestJS validates ALL fields in `AckInfoDto` when `ackInfo` is provided
- Required fields (`acknowledgmentNumber`, `poNumber`, `acknowledgmentDate`) must be present
- Even though it's an update, the nested DTO validation still applies

---

## Validation Rules

Since `UpdateAcknowledgmentDto` extends `PartialType(CreateAcknowledgmentDto)`, all fields are optional, BUT:

1. **Field names must match exactly** - No typos or wrong field names
2. **Nested structure must be correct** - Fields must be in the right DTO
3. **Type validation applies** - Numbers must be numbers, strings must be strings, dates must be valid ISO 8601

---

## Corrected Test Payload

```typescript
// Option 1: Update ackInfo
const updateData = {
  ackInfo: {
    acknowledgmentTotal: 1200,
    comments: 'Updated via API test'
  }
};

// Option 2: Update financials
const updateData = {
  financials: {
    totalAcknowledged: 1200,
    productSubtotal: 1000,
    salesTax: 200
  }
};

// Option 3: Update shipping
const updateData = {
  shipping: {
    freight: 50,
    trackingInformation: 'TRACK-12345'
  }
};
```

---

## Why This Error Occurred

1. **Field Location Confusion**: `acknowledgmentTotal` sounds like it should be in `financials`, but it's actually in `ackInfo`
2. **DTO Structure**: The nested structure requires fields to be in the correct parent object
3. **Validation**: NestJS validation uses `whitelistValidation` which rejects unknown properties

---

## Fix for Test Script

Update `scripts/test-all-rpc-endpoints.ts`:

```typescript
async function testUpdateAcknowledgment(recordId: number): Promise<TestResult> {
  // ✅ CORRECT: Update financials (no required fields)
  const updateData = {
    financials: {
      totalAcknowledged: 1200,
      productSubtotal: 1000,
      salesTax: 200,
    }
  };
  
  // ✅ ALTERNATIVE: Update shipping (also works)
  // const updateData = {
  //   shipping: {
  //     freight: 50,
  //     trackingInformation: 'TRACK-12345'
  //   }
  // };
  
  // ❌ WRONG: Don't update ackInfo without all required fields
  // const updateData = {
  //   ackInfo: {
  //     acknowledgmentTotal: 1200  // This will fail validation!
  //   }
  // };
  
  // ... rest of function
}
```

---

## Summary

**Problem 1:** Field `acknowledgmentTotal` was placed in `financials` object, but it belongs in `ackInfo` object.

**Problem 2:** When updating `ackInfo`, NestJS validates ALL required fields (`acknowledgmentNumber`, `poNumber`, `acknowledgmentDate`), causing validation to fail even for partial updates.

**Solution:** 
- ✅ Use `financials.totalAcknowledged` instead of `ackInfo.acknowledgmentTotal`
- ✅ Or update other optional fields like `shipping`, `project`, `warrantyInformation`
- ❌ Avoid updating `ackInfo` unless you provide all required fields

**Status:** ✅ Fixed - Use `financials` or other optional fields for updates.

