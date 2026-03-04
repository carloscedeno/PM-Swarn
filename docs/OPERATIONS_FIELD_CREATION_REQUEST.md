# Shipping Notice - Database Field Creation Request

**Date:** December 3, 2025  
**Record Type ID:** 14 (Shipping Notice)  
**Priority:** High

---

## Summary

We need **4 new fields** created for Record Type 14 (Shipping Notice).

**Current Status:**
- ✅ 6 fields already exist (no action needed)
- ❌ 4 fields need to be created

---

## Fields to Create

### 1. Fulfillment Status
- **Type:** Dropdown
- **Required:** No (Optional)
- **List Values:**
  - In Progress
  - Shipped
  - Delivered
  - Delayed

### 2. Notice Attachment
- **Type:** Text/String
- **Required:** No (Optional)
- **Purpose:** URL or attachment ID for notice document

### 3. Financial
- **Type:** Object
- **Required:** No (Optional)
- **Properties:** freightCost, handlingFee, totalCost

### 4. Shipments
- **Type:** Text/String (stores JSON)
- **Required:** No (Optional)
- **Purpose:** Array of shipment information (tracking numbers, carriers, etc.)

---

## Fields That Already Exist (No Action Needed)

✅ Acknowledgement Number  
✅ Ship Date  
✅ Shipping Address v1  
✅ Record Status  
✅ Record Target Tenant  
✅ Line Items (stored in table, not a field)

---

## Important Notes

1. **All 4 fields are OPTIONAL** - Won't break existing functionality
2. **Field names must match exactly:**
   - `Fulfillment Status` (with space)
   - `Notice Attachment` (with space)
   - `Financial` (exact case)
   - `Shipments` (exact case)
3. **Shipments field is CRITICAL** - Used for duplicate detection

---

## Confirmation

**Total Fields Needed:** 4  
**Total Fields Already Exist:** 6  
**No other fields required.**

---

**End of Request**
