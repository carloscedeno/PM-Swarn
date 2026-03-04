# Shipping Notice Schema Persistence Analysis

**Date:** December 3, 2025  
**Test Record ID:** 89333  
**Status:** ⚠️ **Data Saved, But Some Fields Not Retrieved**

---

## Test Results Summary

### ✅ Fields Successfully Saved and Retrieved

| Field | Status | Value |
|-------|--------|-------|
| `acknowledgmentNumber` | ✅ Present | ACK-SCHEMA-TEST-1764778778322 |
| `shipDate` | ✅ Present | 2025-12-15 |
| `recordStatus` | ✅ Present | Confirmed |
| `lineItems[0].catalogCode` | ✅ Present | PROD-SCHEMA-001 |
| `lineItems[0].quantity` | ✅ Present | 10 |
| `lineItems[0].productNumber` | ✅ Present | SKU-SCHEMA-123 |
| `lineItems[0].productDescription` | ✅ Present | Schema Test Product |
| `lineItems[0].productSell` | ✅ Present | 99.99 |

**Total Present:** 8/45 fields

---

### ❌ Fields Saved But Not Retrieved (Required)

| Field | Issue |
|-------|-------|
| `shippingAddress.address1` | Empty string returned |
| `shippingAddress.city` | Empty string returned |
| `shippingAddress.state` | Empty string returned |
| `shippingAddress.zip` | Empty string returned |

**Root Cause:** The mapper saves shipping address as an object field (`Shipping Address v1` with `objectValue`), but the extraction method may not be finding it in the database response, OR the field doesn't exist in the database yet.

---

### ⚠️ Fields Saved But Not Retrieved (Optional)

**Top-Level:**
- `targetTenant` - Not sent (field expects number, not string)
- `fulfillmentStatus` - Saved but not retrieved (list value mapping issue?)
- `noticeAttachment` - Saved but not retrieved

**Shipping Address:**
- `address2`, `contact`, `email`, `phone` - All saved but not retrieved

**Financial:**
- `freightCost`, `handlingFee`, `totalCost` - All saved but not retrieved

**Line Items:**
- `manufacturerCode`, `productList`, `productCost`, `purchaseDiscount`, `sellDiscount`
- `totalList`, `totalProduct`, `totalPurchase`, `totalSell`
- `dimensions`, `furnitureCategory`, `assemblyRequired`, `options`, `tags`
- **Note:** These are stored in JSON in the line item `value` field, but may not be parsed correctly

**Shipments:**
- All shipment fields - Saved as JSON string but not retrieved

---

## Root Cause Analysis

### 1. Shipping Address Issue

**Mapper (Saving):**
```typescript
// shipping-notice-to-record.mapper.ts:136-158
fields.push({
  fieldName: 'Shipping Address v1',
  value: '',
  objectValue: {
    objectId: 436, // TODO: Verify actual objectId
    objectValues: [
      { name: 'address1', value: dto.shippingAddress.address1 || '' },
      // ... other fields
    ],
  },
});
```

**Mapper (Retrieving):**
```typescript
// record-to-shipping-notice.mapper.ts:124-161
const addressField = fields.find((f) => f.fieldName === 'Shipping Address v1');
if (addressField?.objectValue?.objectValues) {
  // Extract from objectValues
}
```

**Possible Issues:**
1. Field `Shipping Address v1` (ID: 436) may not exist in database
2. `objectId: 436` may be incorrect
3. Database may not be returning `objectValue` structure correctly
4. Field name mismatch between save and retrieve

### 2. Financial Issue

**Mapper (Saving):**
```typescript
// shipping-notice-to-record.mapper.ts:163-180
fields.push({
  fieldName: 'Financial',
  value: '',
  objectValue: {
    objectId: 0, // Placeholder - TODO: Get actual objectId
    objectValues: [...],
  },
});
```

**Issue:** `objectId: 0` is a placeholder. The field may not exist in the database yet.

### 3. Shipments Issue

**Mapper (Saving):**
```typescript
// shipping-notice-to-record.mapper.ts:184-189
fields.push({
  fieldName: 'Shipments',
  value: JSON.stringify(dto.shipments),
});
```

**Mapper (Retrieving):**
```typescript
// record-to-shipping-notice.mapper.ts:198-210
const shipmentsJson = this.getFieldValue(fields, 'Shipments');
if (shipmentsJson) {
  return JSON.parse(shipmentsJson);
}
```

**Issue:** Field `Shipments` may not exist in database, or JSON string may not be saved correctly.

### 4. Line Items Optional Fields

**Saving:** Line items store full JSON in `value` field (line-items-client.service.ts:225)
```typescript
descriptionField.value = JSON.stringify(itemWithTags);
```

**Retrieving:** RecordToShippingNoticeMapper parses JSON (record-to-shipping-notice.mapper.ts:230)
```typescript
const parsedValue = JSON.parse(item.value as string);
```

**Issue:** The JSON parsing should work, but may fail if `item.value` is not a string or is malformed.

---

## Verification Needed

### Database Field Verification

1. **Check if these fields exist in database:**
   - `Shipping Address v1` (ID: 436) - Object field
   - `Financial` - Object field (may need to be created)
   - `Shipments` - Text/JSON field (may need to be created)
   - `Fulfillment Status` - List field (may need to be created)
   - `Notice Attachment` - Text field (may need to be created)

2. **Verify objectId for Shipping Address:**
   - Current code uses `objectId: 436`
   - Need to verify this matches the actual object definition in database

3. **Check Record Type 14 field definitions:**
   - Query: `SELECT * FROM field WHERE record_type_id = 14`
   - Verify all expected fields exist

### Data Verification

1. **Query the actual saved record:**
   ```sql
   SELECT * FROM record_header WHERE id = 89333;
   SELECT * FROM record_additional_field WHERE record_header_id = 89333;
   ```

2. **Check if objectValue structure is saved:**
   - Verify `objectValue` and `objectValues` are stored correctly
   - Check JSON structure in database

---

## Recommendations

### Immediate Actions

1. **Verify Database Fields Exist:**
   - Run query to check if `Shipping Address v1` (ID: 436) exists for record type 14
   - Check if `Financial`, `Shipments`, `Fulfillment Status`, `Notice Attachment` fields exist

2. **Fix Shipping Address Extraction:**
   - If field exists but not retrieved, debug `extractShippingAddress()` method
   - Add logging to see what `additionalFields` contains when retrieving

3. **Create Missing Fields (if needed):**
   - If fields don't exist, they need to be created in the database
   - Or use alternative field names that do exist

### Code Fixes Needed

1. **Shipping Address:**
   - Verify `objectId: 436` is correct
   - Add fallback to extract from JSON if objectValue not found
   - Add logging to debug extraction

2. **Financial:**
   - Get actual `objectId` for Financial field (currently placeholder `0`)
   - Create field in database if it doesn't exist

3. **Shipments:**
   - Verify `Shipments` field exists in database
   - Or use alternative field name
   - Ensure JSON string is properly saved and retrieved

4. **Line Items:**
   - Verify JSON parsing works correctly
   - Add error handling for malformed JSON
   - Ensure all optional fields are included in JSON

---

## Conclusion

**Status:** ⚠️ **Partial Implementation**

- ✅ Core fields (acknowledgmentNumber, shipDate, recordStatus, basic line items) are saved and retrieved
- ❌ Shipping address (required) is saved but not retrieved properly
- ⚠️ Optional fields (financial, shipments, line item details) are saved but not retrieved

**Next Steps:**
1. Verify database fields exist for record type 14
2. Fix field name mappings if they don't match
3. Create missing fields in database if needed
4. Debug extraction methods to see why data isn't being retrieved
5. Re-test after fixes

---

**Test Results File:** `test-schema-persistence-results.json`  
**Created Record ID:** 89333  
**Created Record Number:** SN-ACK-SCHEMA-TEST-1764778778322-1764778795291

