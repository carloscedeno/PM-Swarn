# Shipping Notice Field Requirements - Confirmation

**Date:** December 3, 2025  
**Purpose:** Confirm which fields are actually needed vs optional

---

## Field Usage Analysis

### 1. ❌ **Fulfillment Status** (dropdown)
**Status:** NEEDS CREATION  
**In DTO:** ✅ Optional (`@IsOptional()`)  
**In Mapper:** ✅ Used (lines 109-123) - saves if provided  
**In Response:** ✅ Returned if present  
**In Schema:** ✅ Part of JSON schema  
**Business Logic:** Used for tracking shipping status (In Progress, Shipped, Delivered, Delayed)  
**Used for Idempotency:** ❌ No  
**Verdict:** ✅ **NEEDED** - Part of schema, used in mapper, important for status tracking

---

### 2. ❌ **Notice Attachment** (text)
**Status:** NEEDS CREATION  
**In DTO:** ✅ Optional (`@IsOptional()`)  
**In Mapper:** ✅ Used (lines 129-131) - saves if provided  
**In Response:** ✅ Returned if present  
**In Schema:** ✅ Part of JSON schema  
**Business Logic:** URL or attachment ID for notice document  
**Used for Idempotency:** ❌ No  
**Verdict:** ✅ **NEEDED** - Part of schema, used in mapper, but purely optional metadata

---

### 3. ❌ **Financial** (object)
**Status:** NEEDS CREATION  
**In DTO:** ✅ Optional (`@IsOptional()`)  
**In Mapper:** ✅ Used (lines 160-180) - saves if provided  
**In Response:** ✅ Returned if present  
**In Schema:** ✅ Part of JSON schema  
**Business Logic:** Financial information (freightCost, handlingFee, totalCost)  
**Validation:** ✅ Validated in `ShippingNoticeValidationService` (lines 200-218) - checks for non-negative values  
**Used for Idempotency:** ❌ No  
**Verdict:** ✅ **NEEDED** - Part of schema, used in mapper, has validation logic

---

### 4. ❌ **Shipments** (text/JSON)
**Status:** NEEDS CREATION  
**In DTO:** ✅ Optional (`@IsOptional()`)  
**In Mapper:** ✅ Used (lines 182-189) - saves as JSON string if provided  
**In Response:** ✅ Returned if present  
**In Schema:** ✅ Part of JSON schema  
**Business Logic:** Array of shipment objects with tracking info  
**Validation:** ✅ Validated in `ShippingNoticeValidationService` (lines 159-180) - checks for unique tracking numbers, valid shipments  
**Used for Idempotency:** ✅ **YES** - Used in `rpc-core.service.ts` line 1041-1042 for generating idempotency key if `referenceId` not provided  
**Verdict:** ✅ **NEEDED** - Part of schema, used in mapper, has validation, **CRITICAL for idempotency key generation**

---

## Summary

### ✅ All 4 Fields Are Needed

| Field | Type | Required? | Critical? | Used For |
|-------|------|-----------|-----------|----------|
| **Fulfillment Status** | dropdown | Optional | Medium | Status tracking |
| **Notice Attachment** | text | Optional | Low | Document reference |
| **Financial** | object | Optional | Medium | Cost information + validation |
| **Shipments** | text/JSON | Optional | **HIGH** | Tracking info + **idempotency key** |

### Why All 4 Are Needed:

1. **All are in the JSON Schema** - They're part of the official schema definition
2. **All are used in the mapper** - Code tries to save them if provided
3. **All are in the response DTO** - Code tries to retrieve and return them
4. **Shipments is critical** - Used for idempotency key generation (fallback if `referenceId` not provided)
5. **Financial has validation** - Business rules validate financial data
6. **Fulfillment Status is important** - Used for tracking shipping status

### If You Want to Skip Some:

**Minimum Required Fields:**
- ✅ **Shipments** - **MUST HAVE** (used for idempotency key generation)
- ✅ **Fulfillment Status** - **SHOULD HAVE** (important for status tracking)

**Can Skip (but not recommended):**
- ⚠️ **Notice Attachment** - Purely optional metadata (can skip if not needed)
- ⚠️ **Financial** - Optional but has validation logic (can skip if not tracking costs)

---

## Recommendation

### ✅ **Create All 4 Fields**

**Reasoning:**
1. All fields are part of the JSON schema
2. All fields are already implemented in the code
3. All fields are optional, so they won't break if not provided
4. Creating all fields ensures full schema compliance
5. Shipments is critical for idempotency
6. Future-proofing - if you skip fields now, you'll need to create them later when customers start using them

### Alternative (Minimum Viable):

If you want to minimize database changes, create at minimum:
1. ✅ **Shipments** (CRITICAL - used for idempotency)
2. ✅ **Fulfillment Status** (IMPORTANT - status tracking)

Skip for now (can add later):
- ⚠️ Notice Attachment
- ⚠️ Financial

---

## Final Answer

**You need to create ALL 4 fields:**
1. ✅ **Fulfillment Status** (dropdown)
2. ✅ **Notice Attachment** (text)
3. ✅ **Financial** (object)
4. ✅ **Shipments** (text/JSON) - **CRITICAL**

**Minimum if you want to reduce scope:**
1. ✅ **Shipments** (text/JSON) - **MUST HAVE**
2. ✅ **Fulfillment Status** (dropdown) - **SHOULD HAVE**

