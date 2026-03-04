# Product Owner Guide: Translations and No-Code Configuration

## Table of Contents
1. [Overview](#overview)
2. [Understanding Translations](#understanding-translations)
3. [Recording New Translations](#recording-new-translations)
4. [Field Name Mapping (No-Code)](#field-name-mapping-no-code)
5. [Field Creation Process](#field-creation-process)
6. [Troubleshooting Translation Issues](#troubleshooting-translation-issues)
7. [Best Practices](#best-practices)

---

## Overview

This guide is for **Product Owners (POs)** and **non-technical team members** who need to:
- Record and manage translations between COR ERP and OrderBahn
- Configure field mappings without writing code
- Request new fields in OrderBahn
- Troubleshoot translation issues

### What is a Translation?

A **translation** is the process of converting data from one format to another:
- **COR ERP Format**: The format that COR ERP sends (Purchase Order DTO)
- **OrderBahn Format**: The format that OrderBahn expects (RecordHeader with additionalFields)

**Example**:
- COR ERP sends: `{ poInfo: { poDate: "2024-01-15" } }`
- OrderBahn expects: `{ fieldName: "Date Ordered", value: "2024-01-15" }`

The translation layer automatically converts between these formats.

---

## Understanding Translations

### Translation Flow

```
COR ERP Purchase Order
    ↓
Translation Service
    ↓
Field Name Mapper (maps "PO Date" → "Date Ordered")
    ↓
OrderBahn RecordHeader
```

### Key Concepts

1. **Field Names**: The human-readable names (e.g., "PO Date", "Vendor Name")
2. **Field IDs**: The database identifiers (e.g., 253, 214)
3. **Field Tags**: The microservice identifiers (e.g., "1;42091;141")
4. **Field Mappings**: The configuration that maps one field name to another

### Translation Components

1. **Static Mappings** (`field-name-mappings.config.ts`)
   - Pre-configured field name aliases
   - Example: "PO Date" can map to ["Date Ordered", "PO Date", "Purchase Order Date"]
   - **No code changes needed** - just update the config file

2. **Dynamic Mappings** (from Records Microservice)
   - Fetched from `/record-types/30/fields` endpoint
   - Maps field tags to field names
   - Automatically cached

3. **Field Validator**
   - Checks if a field exists before storing
   - Prevents data from being stored in non-existent fields

---

## Recording New Translations

### When to Record a New Translation

Record a new translation when:
- COR ERP sends a new field that doesn't exist in OrderBahn
- OrderBahn has a field that COR ERP doesn't send
- Field names don't match between systems
- A field mapping is incorrect

### Step-by-Step: Recording a Translation

#### Step 1: Identify the Field

**From COR ERP Side**:
- What field name does COR ERP use? (e.g., "PO Date")
- What data type is it? (e.g., date, string, number)
- Is it required or optional?

**From OrderBahn Side**:
- What field name does OrderBahn use? (e.g., "Date Ordered")
- What is the field ID? (e.g., 253)
- Does it exist in the Purchase Order record type? (Record Type ID: 30)

#### Step 2: Check Existing Mappings

**Check**: `docs/check.md` or `docs/check-md-vs-database-analysis.md`

**Look for**:
- Does the field already exist in OrderBahn?
- What is the correct field name?
- What is the field ID?

**Example**:
- COR ERP sends: "PO Date"
- OrderBahn has: "Date Ordered" (ID: 253)
- Mapping needed: "PO Date" → "Date Ordered"

#### Step 3: Update Field Name Mappings (No-Code)

**File**: `src/context/rpc-core/config/field-name-mappings.config.ts`

**Format**:
```typescript
['COR_ERP_FIELD_NAME', ['OrderBahn_Field_Name_1', 'OrderBahn_Field_Name_2', 'Alias_3']]
```

**Example**:
```typescript
// Before
['PO Date', ['PO Date', 'Purchase Order Date']]

// After (add "Date Ordered" as primary)
['PO Date', ['Date Ordered', 'PO Date', 'Purchase Order Date']]
```

**Rules**:
- First name in array is the **primary** (most likely to match)
- Additional names are **aliases** (fallback options)
- Order matters: system tries first name first, then aliases

#### Step 4: Test the Translation

1. **Use Postman** or Swagger UI (`/docs`)
2. **Send a test request** with the new field
3. **Check the response** to see if field was mapped correctly
4. **Check OrderBahn** to verify data was stored correctly

#### Step 5: Document the Translation

**Update**: `docs/check.md` or create a new entry in translation log

**Include**:
- COR ERP field name
- OrderBahn field name
- Field ID
- Data type
- Required/Optional
- Date recorded

---

## Field Name Mapping (No-Code)

### What is Field Name Mapping?

Field name mapping is a **no-code configuration** that tells the system:
- "When COR ERP sends 'PO Date', try to find 'Date Ordered' in OrderBahn"
- "If 'Date Ordered' doesn't exist, try 'PO Date' as fallback"

### Configuration File

**Location**: `src/context/rpc-core/config/field-name-mappings.config.ts`

**Structure**:
```typescript
export const FIELD_NAME_MAPPINGS: Map<string, string[]> = new Map([
  ['COR_ERP_FIELD', ['OrderBahn_Primary', 'OrderBahn_Alias_1', 'OrderBahn_Alias_2']],
  // ... more mappings
]);
```

### How to Add a New Mapping

#### Example: Adding "Vendor Company Name"

**Scenario**: COR ERP sends "Vendor Company Name", but OrderBahn uses "Vendor Name"

**Step 1**: Open `src/context/rpc-core/config/field-name-mappings.config.ts`

**Step 2**: Find the Vendor section (around line 41)

**Step 3**: Add or update the mapping:
```typescript
// Before
['Vendor Name', ['Vendor Name', 'Vendor Company Name', 'Vendor Company']]

// After (if "Vendor Company Name" is the primary from COR ERP)
['Vendor Company Name', ['Vendor Name', 'Vendor Company Name', 'Vendor Company']]
```

**Step 4**: Save the file

**Step 5**: Deploy (no code compilation needed - TypeScript will compile on deploy)

### Common Mapping Patterns

#### Pattern 1: Exact Match
```typescript
['PO Number', ['PO Number']]  // Exact match, no aliases needed
```

#### Pattern 2: Multiple Aliases
```typescript
['Order Total', ['Grand Total', 'Amount', 'Order Total', 'PO Total', 'Total']]
// Tries "Grand Total" first, then "Amount", then others
```

#### Pattern 3: Generic Fields
```typescript
['Vendor Email 1', ['Email 1', 'Vendor Email 1', 'Vendor Email 2', 'Vendor Email']]
// Generic "Email 1" might be shared, so try specific name first
```

### Field Name Matching Logic

The system uses this logic to find fields:

1. **Try primary name** (first in array)
2. **If not found, try aliases** (rest of array)
3. **If still not found, use field tag** (from microservice)
4. **If still not found, log warning** and skip field

### Best Practices for Mappings

1. **Put most specific name first**
   - ✅ `['Vendor Email 1', ['Vendor Email 1', 'Email 1']]`
   - ❌ `['Vendor Email 1', ['Email 1', 'Vendor Email 1']]`

2. **Include common variations**
   - ✅ `['PO Date', ['Date Ordered', 'PO Date', 'Purchase Order Date', 'Order Date']]`
   - ❌ `['PO Date', ['Date Ordered']]`

3. **Document field IDs in comments**
   ```typescript
   // PO Date: Updated to use "Date Ordered" (ID: 253) - actual field name in database
   ['PO Date', ['Date Ordered', 'PO Date', 'Purchase Order Date']]
   ```

4. **Group related fields together**
   - Keep Vendor fields together
   - Keep Dealer fields together
   - Keep Financial fields together

---

## Field Creation Process

### When to Request a New Field

Request a new field when:
- COR ERP sends a field that **doesn't exist** in OrderBahn
- OrderBahn needs a field that COR ERP **can provide**
- A field exists but has the **wrong data type**

### Step-by-Step: Requesting a New Field

#### Step 1: Document the Requirement

**Create a document** with:
- **Field Name**: What should it be called? (e.g., "Installation Contact Email")
- **Data Type**: string, number, date, datetime, dropdown, etc.
- **Required/Optional**: Is it required?
- **Description**: What is this field for?
- **Source**: Where does the data come from? (COR ERP, manual entry, etc.)
- **Example Value**: Example of what the value looks like

**Template**:
```
Field Name: Installation Contact Email
Data Type: string (email)
Required: No
Description: Email address for the installation contact person
Source: COR ERP Purchase Order
Example Value: "install.contact@example.com"
Related Fields: Installation Contact, Installation Phone
```

#### Step 2: Check if Field Already Exists

**Check**:
- `docs/check.md`: List of all Purchase Order fields
- `docs/check-md-vs-database-analysis.md`: Fields that exist vs. don't exist
- `docs/missing-fields-list.md`: Fields that are missing

**Search for**:
- Similar field names
- Generic fields that might work (e.g., "Email 1", "Contact Associated")

#### Step 3: Use Field Creation Guide

**See**: `docs/create-fields-guide.md`

**Follow the guide** to:
- Determine field type
- Determine data type
- Determine if it needs a list
- Determine if it needs to be an object

#### Step 4: Submit Field Creation Request

**Option 1: Email Template**
- See: `docs/field-creation-email-template.md`
- Fill out the template
- Send to OrderBahn Product Team

**Option 2: Create Issue/Ticket**
- Use the template from `docs/field-creation-request.md`
- Include all required information

**Include**:
- Field name
- Data type
- Required/Optional
- Description
- Business justification
- Example values

#### Step 5: Track Field Creation

**Use**: `docs/missing-fields-tracker.csv`

**Update with**:
- Field name
- Status (Requested, In Progress, Created, Rejected)
- Date requested
- Date created
- Field ID (once created)
- Notes

#### Step 6: Update Mappings After Field is Created

**Once field is created in OrderBahn**:

1. **Get the field ID** from Operations/Product Team
2. **Update** `field-name-mappings.config.ts`:
   ```typescript
   // Installation Contact Email: record_additional_field_XXX (ID: XXX)
   ['Installation Contact Email', ['Installation Contact Email', 'Installation Email']]
   ```
3. **Update** `docs/check.md` with new field
4. **Test** the mapping

---

## Troubleshooting Translation Issues

### Common Issues

#### Issue 1: Field Not Being Stored

**Symptoms**:
- COR ERP sends field, but it doesn't appear in OrderBahn
- No error, but field is missing

**Possible Causes**:
1. Field doesn't exist in OrderBahn
2. Field name doesn't match
3. Field is being filtered out

**Solutions**:
1. **Check if field exists**: See `docs/check.md` or query Records MS
2. **Check field name mapping**: See `field-name-mappings.config.ts`
3. **Check logs**: Look for warnings about field not found
4. **Request field creation**: If field doesn't exist

#### Issue 2: Field Stored with Wrong Name

**Symptoms**:
- Field is stored, but with different name than expected
- Data is in wrong field

**Possible Causes**:
1. Field mapping is incorrect
2. Field name alias matched wrong field

**Solutions**:
1. **Check field mapping**: Verify mapping in `field-name-mappings.config.ts`
2. **Check field names**: Verify actual field names in OrderBahn
3. **Update mapping**: Fix the mapping to use correct field name
4. **Test**: Send test request and verify

#### Issue 3: Field Value is Wrong Type

**Symptoms**:
- Field is stored, but value is wrong format
- Date stored as string, number stored as text, etc.

**Possible Causes**:
1. Data type mismatch between COR ERP and OrderBahn
2. Field expects different format

**Solutions**:
1. **Check data types**: Verify COR ERP sends correct type
2. **Check OrderBahn field type**: Verify what OrderBahn expects
3. **Request field type change**: If field type is wrong in OrderBahn
4. **Update mapper**: If translation logic needs to convert type

#### Issue 4: Required Field Missing

**Symptoms**:
- Error: "Field X is required"
- Request fails validation

**Possible Causes**:
1. COR ERP doesn't send required field
2. Field mapping failed
3. Field is optional in COR ERP but required in OrderBahn

**Solutions**:
1. **Check if field is required**: See field definition in OrderBahn
2. **Request field to be optional**: If it should be optional
3. **Request COR ERP to send field**: If it should be required
4. **Provide default value**: If field can have default

### Debugging Steps

#### Step 1: Check Logs

**Look for**:
- Field mapping warnings
- Field validation errors
- Translation errors

**Log locations**:
- Application logs (CloudWatch, console)
- Audit logs (if enabled)

#### Step 2: Test with Postman

**Use Postman collection**: `postman-collections/RPC-Core-API.postman_collection.json`

**Steps**:
1. Send test request with field
2. Check response
3. Check OrderBahn to see if field was stored
4. Compare expected vs. actual

#### Step 3: Verify Field Exists

**Query Records MS**:
```
GET /record-types/30/fields
```

**Look for**:
- Field name
- Field ID
- Data type
- Required/Optional

#### Step 4: Check Field Mapping

**Check**: `src/context/rpc-core/config/field-name-mappings.config.ts`

**Verify**:
- Mapping exists for field
- Primary name is correct
- Aliases include correct names

#### Step 5: Contact Development Team

**If issue persists**, provide:
- Field name from COR ERP
- Field name expected in OrderBahn
- Field ID (if known)
- Error message (if any)
- Logs (if available)
- Test request/response (if available)

---

## Best Practices

### For Recording Translations

1. **Document everything**
   - Field names (both systems)
   - Field IDs
   - Data types
   - Required/Optional
   - Date recorded

2. **Test before deploying**
   - Use Postman/Swagger to test
   - Verify data in OrderBahn
   - Check logs for warnings

3. **Keep mappings up to date**
   - Update when field names change
   - Remove obsolete mappings
   - Add new mappings promptly

4. **Use consistent naming**
   - Follow OrderBahn naming conventions
   - Use clear, descriptive names
   - Avoid abbreviations when possible

### For Field Mappings

1. **Put most specific name first**
   - Specific names are more likely to match
   - Generic names can match wrong fields

2. **Include common variations**
   - Different systems use different names
   - Include all known variations

3. **Document field IDs**
   - Add comments with field IDs
   - Makes debugging easier

4. **Group related fields**
   - Keep Vendor fields together
   - Keep Dealer fields together
   - Makes maintenance easier

### For Field Creation Requests

1. **Provide complete information**
   - Field name, type, description
   - Business justification
   - Example values

2. **Check if field already exists**
   - Search existing fields
   - Check if generic field can be used

3. **Track requests**
   - Use tracker spreadsheet
   - Follow up on status
   - Update when field is created

4. **Test after field is created**
   - Verify field exists
   - Test mapping
   - Verify data storage

---

## Quick Reference

### Field Mapping File Location
```
src/context/rpc-core/config/field-name-mappings.config.ts
```

### Field Documentation Files
- `docs/check.md`: All Purchase Order fields
- `docs/check-md-vs-database-analysis.md`: Field analysis
- `docs/missing-fields-list.md`: Missing fields
- `docs/create-fields-guide.md`: How to create fields

### Field Creation Templates
- `docs/field-creation-email-template.md`: Email template
- `docs/field-creation-request.md`: Request template

### Field Tracker
- `docs/missing-fields-tracker.csv`: Track field creation status

### API Documentation
- Swagger UI: `http://localhost:3000/docs` (when running)
- Postman: `postman-collections/RPC-Core-API.postman_collection.json`

### Record Type
- **Purchase Order Record Type ID**: 30

### Common Field Mappings

| COR ERP Field | OrderBahn Field | Field ID |
|--------------|-----------------|----------|
| `poInfo.poDate` | "Date Ordered" | 253 |
| `poInfo.poNumber` | "PO Number" | 214 |
| `financials.poTotalAmount` | "Grand Total" | 260 |
| `vendor.name` | "Vendor Name" | 16 |
| `dealer.dealerName` | "Dealer Name" | 255 |

---

## Support

### Questions?

- **Translation Issues**: Contact Development Team
- **Field Creation**: Contact OrderBahn Product Team
- **Field Mapping**: See `docs/create-fields-guide.md`

### Resources

- Architecture Documentation: `docs/ARCHITECTURE.md`
- Field Analysis: `docs/check-md-vs-database-analysis.md`
- Environment Variables: `ENV_VARIABLES_ANALYSIS.md`

---

*Last Updated: 2025-01-XX*
*Version: 2.0.0*





