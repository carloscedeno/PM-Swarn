# Shipping Notice / ASN Implementation Plan (IN-46)

**Date:** December 2025  
**Status:** Planning Phase  
**Record Type ID:** 14 ("Shipping Notice")  
**Schema Source:** Provided JSON Schema for Shipping/ASN

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Schema Analysis](#schema-analysis)
3. [Database Field Mapping](#database-field-mapping)
4. [DTO Structure Design](#dto-structure-design)
5. [Mapper Design](#mapper-design)
6. [Service Layer Design](#service-layer-design)
7. [Controller Design](#controller-design)
8. [Validation Strategy](#validation-strategy)
9. [Testing Strategy](#testing-strategy)
10. [Implementation Phases](#implementation-phases)
11. [Dependencies & Prerequisites](#dependencies--prerequisites)
12. [Open Questions & Decisions](#open-questions--decisions)

---

## Executive Summary

### Objective
Implement Shipping Notice (ASN - Advanced Shipping Notice) creation endpoint in RPC Core following the existing PO/ACK pattern. Shipping Notices will be stored as `record_type.id = 14` with structured data in `record_additional_fields` and `line_items` tables.

### Key Decisions
- **Record Type:** Use existing `record_type.id = 14` ("Shipping Notice")
- **Storage Pattern:** Follow PO/ACK pattern (record_header + additional_fields + line_items)
- **Schema:** Follow provided JSON schema exactly (array of shipping notices)
- **Carrier Location:** Per shipment (not at notice level)
- **Line Items:** Store at notice level AND optionally per shipment

### Architecture Alignment
- **Mirrors PO/ACK:** Same layering (DTO → Mapper → Service → Controller)
- **Reuses Infrastructure:** Record Grid Client, Line Items Client, existing validation patterns
- **Future-Proof:** Designed to support IN-47 (API ingestion) and IN-48 (batch/OCR)

---

## Schema Analysis

### Top-Level Structure
```json
{
  "type": "array",
  "items": { /* Shipping Notice object */ }
}
```

**Important:** Schema defines an **array** at the top level. We will follow this exactly:
- **Request body:** Array of shipping notice objects (even if IN-46 submits one at a time, it will be `[{...}]`)
- **Response body:** Array of shipping notice objects (matches schema exactly)
- This ensures consistency and future-proofing for IN-47 (API ingestion) and IN-48 (batch/OCR)

### Required Fields (from schema)
1. `acknowledgmentNumber` (string) - Links to ACK record
2. `shipDate` (date) - Required shipment date
3. `shippingAddress` (object) - Required with address1, city, state, zip
4. `lineItems` (array) - Required array of line items

### Optional Fields
- `recordStatus` (enum: Draft, Submitted, Confirmed, Cancelled)
- `targetTenant` (string)
- `fulfillmentStatus` (enum: In Progress, Shipped, Delivered, Delayed)
- `noticeAttachment` (string - URL or attachment ID)
- `financial` (object: freightCost, handlingFee, totalCost)
- `shipments` (array) - Array of shipment objects

### Shipment Object Structure
Each shipment contains:
- `shipmentNumber` (number)
- `carrier` (string) - **Per shipment, not per notice**
- `trackingNumber` (string)
- `trackingURL` (uri)
- `shipmentType` (enum: LTL, FTL, Parcel, Air, Ocean)
- `status` (enum: Processing, In Transit, Delivered, Exception)
- `tariff` (string)
- `billOfLading` (string)
- `additionalInformation` (object with specialInstructions, handlingInstructions, claimsInformation, notes)
- `items` (array) - Line items contained in this shipment (references main lineItems schema)

### Line Item Structure
Matches PO line item structure with all fields:
- Required: `catalogCode`, `quantity`, `productNumber`, `productDescription`, `productSell`
- Optional: `manufacturerCode`, `productList`, `productCost`, discounts, totals, dimensions, furnitureCategory, assemblyRequired, options, tags

---

## Database Field Mapping

### Record Type
- **Type ID:** `14` (already exists: "Shipping Notice")
- **Table:** `record_header`
- **Record Number:** Auto-generated or provided (e.g., "SN-{timestamp}" or from `acknowledgmentNumber`)

### Additional Fields Required (to be configured in OrderBahn)

#### Core Fields
1. **`"Acknowledgment Number"`** (string, required)
   - Maps from: `acknowledgmentNumber`
   - Used to link Shipping Notice to ACK record

2. **`"Ship Date"`** (date, required)
   - Maps from: `shipDate`
   - Format: YYYY-MM-DD

3. **`"Record Status"`** (dropdown/enum, optional)
   - Maps from: `recordStatus`
   - Values: Draft, Submitted, Confirmed, Cancelled
   - May need listTypeId configuration (similar to PO Record Status)

4. **`"Fulfillment Status"`** (dropdown/enum, optional)
   - Maps from: `fulfillmentStatus`
   - Values: In Progress, Shipped, Delivered, Delayed
   - May need listTypeId configuration

5. **`"Target Tenant"`** (string, optional)
   - Maps from: `targetTenant`

6. **`"Notice Attachment"`** (string, optional)
   - Maps from: `noticeAttachment`
   - URL or attachment ID

#### Address Fields
7. **`"Shipping Address"`** (object/JSON, required)
   - Maps from: `shippingAddress` object
   - Store as object field with structure:
     ```json
     {
       "address1": "...",
       "address2": "...",
       "city": "...",
       "state": "...",
       "zip": "...",
       "contact": "...",
       "email": "...",
       "phone": "..."
     }
     ```
   - Or split into individual fields:
     - `"Shipping Address 1"` (string)
     - `"Shipping Address 2"` (string)
     - `"Shipping City"` (string)
     - `"Shipping State"` (string)
     - `"Shipping Zip"` (string)
     - `"Shipping Contact"` (string)
     - `"Shipping Email"` (string)
     - `"Shipping Phone"` (string)

#### Financial Fields
8. **`"Financial"`** (object/JSON, optional)
   - Maps from: `financial` object
   - Store as object field with structure:
     ```json
     {
       "freightCost": 0.0,
       "handlingFee": 0.0,
       "totalCost": 0.0
     }
     ```
   - Or split into individual fields:
     - `"Freight Cost"` (currency)
     - `"Handling Fee"` (currency)
     - `"Total Cost"` (currency)

#### Shipment Fields
9. **`"Shipments"`** (object/collection, optional but recommended)
   - Maps from: `shipments[]` array
   - Store as object/collection field (similar to PO `ShippingRequirements`)
   - Each objectValue represents one shipment:
     ```json
     {
       "shipmentNumber": 1,
       "carrier": "UPS",
       "trackingNumber": "1Z999AA10123456784",
       "trackingURL": "https://...",
       "shipmentType": "Parcel",
       "status": "In Transit",
       "tariff": "...",
       "billOfLading": "...",
       "additionalInformation": {
         "specialInstructions": "...",
         "handlingInstructions": "...",
         "claimsInformation": "...",
         "notes": "..."
       }
     }
     ```

### Line Items Storage

**Pattern:** Same as PO line items
- **Table:** `line_items` and `line_items_row`
- **Type:** Need to identify or create `lineItemsByTypeId` for Shipping Notice line items
- **Storage:** Each line item stored as row in `line_items` with field mappings
- **Full JSON:** Store complete line item JSON in description/value field for retrieval

**Line Items Per Shipment:**
- Shipment `items[]` array references main `lineItems[]` by index or catalogCode
- Store shipment-to-line-item mapping in shipment object's `items` field
- Or store separately in a junction structure (to be determined)

---

## DTO Structure Design

### CreateShippingNoticeDto

**Location:** `src/context/rpc-core/dto/create-shipping-notice.dto.ts`

**Structure:**
```typescript
// Enums
export enum RecordStatus {
  DRAFT = 'Draft',
  SUBMITTED = 'Submitted',
  CONFIRMED = 'Confirmed',
  CANCELLED = 'Cancelled',
}

export enum FulfillmentStatus {
  IN_PROGRESS = 'In Progress',
  SHIPPED = 'Shipped',
  DELIVERED = 'Delivered',
  DELAYED = 'Delayed',
}

export enum ShipmentType {
  LTL = 'LTL',
  FTL = 'FTL',
  PARCEL = 'Parcel',
  AIR = 'Air',
  OCEAN = 'Ocean',
}

export enum ShipmentStatus {
  PROCESSING = 'Processing',
  IN_TRANSIT = 'In Transit',
  DELIVERED = 'Delivered',
  EXCEPTION = 'Exception',
}

// Nested DTOs
export class ShippingAddressDto {
  @IsNotEmpty()
  @IsString()
  address1: string;

  @IsOptional()
  @IsString()
  address2?: string;

  @IsNotEmpty()
  @IsString()
  city: string;

  @IsNotEmpty()
  @IsString()
  state: string;

  @IsNotEmpty()
  @IsString()
  zip: string;

  @IsOptional()
  @IsString()
  contact?: string;

  @IsOptional()
  @IsEmail()
  email?: string;

  @IsOptional()
  @IsString()
  phone?: string;
}

export class FinancialDto {
  @IsOptional()
  @IsNumber()
  freightCost?: number;

  @IsOptional()
  @IsNumber()
  handlingFee?: number;

  @IsOptional()
  @IsNumber()
  totalCost?: number;
}

export class AdditionalInformationDto {
  @IsOptional()
  @IsString()
  specialInstructions?: string;

  @IsOptional()
  @IsString()
  handlingInstructions?: string;

  @IsOptional()
  @IsString()
  claimsInformation?: string;

  @IsOptional()
  @IsString()
  notes?: string;
}

export class ShipmentDto {
  @IsOptional()
  @IsNumber()
  shipmentNumber?: number;

  @IsOptional()
  @IsString()
  carrier?: string;

  @IsOptional()
  @IsString()
  trackingNumber?: string;

  @IsOptional()
  @IsUrl()
  trackingURL?: string;

  @IsOptional()
  @IsEnum(ShipmentType)
  shipmentType?: ShipmentType;

  @IsOptional()
  @IsEnum(ShipmentStatus)
  status?: ShipmentStatus;

  @IsOptional()
  @IsString()
  tariff?: string;

  @IsOptional()
  @IsString()
  billOfLading?: string;

  @IsOptional()
  @ValidateNested()
  @Type(() => AdditionalInformationDto)
  additionalInformation?: AdditionalInformationDto;

  @IsOptional()
  @IsArray()
  items?: any[]; // References to lineItems (by index or catalogCode)
}

// Reuse LineItemDto from create-purchase-order.dto.ts
// Or create ShippingNoticeLineItemDto if structure differs

export class CreateShippingNoticeDto {
  @IsNotEmpty()
  @IsString()
  acknowledgmentNumber: string;

  @IsNotEmpty()
  @IsDateString()
  shipDate: string;

  @IsNotEmpty()
  @ValidateNested()
  @Type(() => ShippingAddressDto)
  shippingAddress: ShippingAddressDto;

  @IsNotEmpty()
  @IsArray()
  @ValidateNested({ each: true })
  @Type(() => LineItemDto) // Reuse or create new
  lineItems: LineItemDto[];

  @IsOptional()
  @IsEnum(RecordStatus)
  recordStatus?: RecordStatus;

  @IsOptional()
  @IsString()
  targetTenant?: string;

  @IsOptional()
  @IsEnum(FulfillmentStatus)
  fulfillmentStatus?: FulfillmentStatus;

  @IsOptional()
  @IsString()
  noticeAttachment?: string;

  @IsOptional()
  @ValidateNested()
  @Type(() => FinancialDto)
  financial?: FinancialDto;

  @IsOptional()
  @IsArray()
  @ValidateNested({ each: true })
  @Type(() => ShipmentDto)
  shipments?: ShipmentDto[];
}
```

### ShippingNoticeResponseDto

**Location:** `src/context/rpc-core/dto/shipping-notice-response.dto.ts`

**Structure:** Mirrors CreateShippingNoticeDto but adds:
- `id` (number) - Record header ID
- `shippingNoticeNumber` (string) - Record number
- `createdAt` (string) - ISO timestamp
- `updatedAt` (string) - ISO timestamp
- `createdBy` (string, optional)
- `tenantId` (number)

**Note:** Response must be an array to match schema exactly:
```typescript
export class ShippingNoticeResponseDto {
  // ... all fields from CreateShippingNoticeDto plus metadata
}

// Controller returns: ShippingNoticeResponseDto[] (array format per schema)
// For IN-46: array with single item `[result]`
// For IN-47/48: array with multiple items `[result1, result2, ...]`
```

---

## Mapper Design

### ShippingNoticeToRecordMapper

**Location:** `src/context/rpc-core/mappers/shipping-notice-to-record.mapper.ts`

**Pattern:** Follow `PoToRecordMapper` structure

**Key Methods:**
1. `mapToRecordHeader(dto: CreateShippingNoticeDto, tenantId: number): ICreateRecordHeaderDto`
   - Sets `recordTypeId = 14`
   - Sets `recordNumber` (from acknowledgmentNumber or auto-generated)
   - Builds `additionalFields[]` array

2. `buildAdditionalFieldsFromShippingNotice(dto: CreateShippingNoticeDto): IAdditionalField[]`
   - Maps all top-level fields to additional fields
   - Handles enum mappings (recordStatus, fulfillmentStatus) to list value IDs
   - Serializes complex objects (shippingAddress, financial, shipments) to object/JSON fields

3. `mapShippingAddressToField(address: ShippingAddressDto): IAdditionalField`
   - Converts shippingAddress object to field
   - Decision: Single object field vs. multiple string fields

4. `mapFinancialToField(financial: FinancialDto): IAdditionalField`
   - Converts financial object to field

5. `mapShipmentsToField(shipments: ShipmentDto[]): IAdditionalField`
   - Converts shipments array to object/collection field
   - Each shipment becomes an objectValue entry

**Enum Mapping:**
- `recordStatus` → List value ID (need to identify listTypeId for Record Status dropdown)
- `fulfillmentStatus` → List value ID (need to identify listTypeId for Fulfillment Status dropdown)
- `shipmentType` → List value ID (if configured as dropdown)
- `shipment.status` → List value ID (if configured as dropdown)

### RecordToShippingNoticeMapper

**Location:** `src/context/rpc-core/mappers/record-to-shipping-notice.mapper.ts`

**Pattern:** Follow `RecordToPoMapper` structure

**Key Methods:**
1. `mapToShippingNotice(record: IRecordHeader): ShippingNoticeResponseDto`
   - Main mapping method
   - Extracts all fields from additionalFields
   - Deserializes complex objects (shippingAddress, financial, shipments)
   - Maps line items from `line_items` table

2. `extractShippingAddress(fields: IAdditionalField[]): ShippingAddressDto`
   - Reconstructs shippingAddress object from field(s)

3. `extractFinancial(fields: IAdditionalField[]): FinancialDto`
   - Reconstructs financial object from field

4. `extractShipments(fields: IAdditionalField[]): ShipmentDto[]`
   - Reconstructs shipments array from object/collection field
   - Parses objectValues array

5. `mapLineItems(lineItems: ILineItem[]): LineItemDto[]`
   - Reuses pattern from RecordToPoMapper
   - Parses JSON from line item value field

**Enum Reverse Mapping:**
- List value IDs → enum strings (recordStatus, fulfillmentStatus, etc.)

---

## Service Layer Design

### RpcCoreService Extension

**Location:** `src/context/rpc-core/rpc-core.service.ts`

**New Method:**
```typescript
async createShippingNotices(
  dtos: CreateShippingNoticeDto[],
  tenantId: number,
  userId?: number,
): Promise<ShippingNoticeResponseDto[]>
```

**Important:** This method accepts an **array** (per schema), but Record Grid Client only creates **one record at a time**. Implementation:
1. Loop through each DTO in the array
2. For each DTO:
   - Map to `ICreateRecordHeaderDto` via mapper
   - Call `recordGridClient.createRecord()` (single record)
   - Create line items via `lineItemsClient.createLineItems()`
   - Map result back to `ShippingNoticeResponseDto`
3. Collect all results and return as array

**Error Handling:**
- If one record fails, decide: fail all (transactional) or return partial success?
- **Recommendation:** Return partial success (array with successful items + errors for failed ones)
- Alternative: Fail fast (throw on first error)

**Implementation Steps (per DTO in array):**

For each `CreateShippingNoticeDto` in the input array:

1. **Validate ACK Reference:**
   - Look up ACK record by `acknowledgmentNumber`
   - Ensure ACK exists and belongs to tenant
   - If not found: Skip this item, add error to results array

2. **Validate Line Items:**
   - Ensure at least one line item provided
   - Validate required fields on each line item
   - If invalid: Skip this item, add error to results array

3. **Generate Record Number (if not provided):**
   - Pattern: `SN-{acknowledgmentNumber}-{timestamp}` or auto-increment

4. **Map DTO to Record:**
   - Use `ShippingNoticeToRecordMapper.mapToRecordHeader()`

5. **Create Record:**
   - Call `recordGridClient.createRecord(createRecordDto, tenantId, headers)`
   - **Note:** Record Grid Client only accepts single record, not array
   - Headers: tenantId, userId (if provided)
   - If fails: Skip this item, add error to results array

6. **Create Line Items:**
   - Use `lineItemsClientService.createLineItems()`
   - Need to identify correct `lineItemsByTypeId` for Shipping Notice line items
   - If fails: Record created but line items missing (log warning, continue)

7. **Map Record to Response:**
   - Use `RecordToShippingNoticeMapper.mapToShippingNotice()`
   - Add to results array

8. **Telemetry (per item):**
   - Emit `shipping_notice_create_started`, `shipping_notice_create_succeeded`, `shipping_notice_create_failed`
   - Include tenantId, recordId, acknowledgmentNumber

9. **Return Results:**
   - Return array of `ShippingNoticeResponseDto[]` (successful items)
   - Optionally include errors in response metadata

**Error Handling Strategy:**
- **Option A (Recommended):** Partial success - return array with successful items, log errors for failed items
- **Option B:** Fail fast - throw on first error, no items created
- **Decision needed:** Which approach for IN-46? (Recommend Option A for batch scenarios)

---

## Controller Design

### RpcCoreController Extension

**Location:** `src/context/rpc-core/rpc-core.controller.ts`

**New Endpoint:**
```typescript
@Post('/rpc/v1/shipping-notices')
@ApiOperation({ summary: 'Create a new Shipping Notice (ASN)' })
@ApiResponse({ status: 201, description: 'Shipping Notice created successfully', type: [ShippingNoticeResponseDto] })
@ApiResponse({ status: 400, description: 'Validation error' })
@ApiResponse({ status: 404, description: 'Acknowledgment not found' })
async createShippingNotice(
  @Body() dtos: CreateShippingNoticeDto[],
  @Headers('x-tenant-id') tenantId: string,
  @Headers('x-user-id') userId?: string,
): Promise<ShippingNoticeResponseDto[]>
```

**Implementation:**
1. Extract tenantId from headers (required)
2. Extract userId from headers (optional)
3. Validate array is not empty (at least one item required)
4. Call `rpcCoreService.createShippingNotices(dtos, parseInt(tenantId), userId ? parseInt(userId) : undefined)`
   - Service handles looping through array internally
   - Service calls Record Grid Client once per item (since it only accepts single records)
5. Return array of results: `[result1, result2, ...]` (matches schema array format)
6. For IN-46: Array will contain single item `[result]`
7. For IN-47/48: Array will contain multiple items

**Note:** This is different from PO/ACK endpoints which accept single objects. The schema requires array format, so we handle the array-to-single-record conversion in the service layer.

**Alternative:** Create separate `ShippingNoticesController` if preferred for organization.

---

## Validation Strategy

### DTO-Level Validation (class-validator)
- **Array validation:** Request body must be array with at least one item
- **Required fields:** `acknowledgmentNumber`, `shipDate`, `shippingAddress`, `lineItems`
- **Required nested fields:** `address1`, `city`, `state`, `zip` in shippingAddress
- **Required line item fields:** `catalogCode`, `quantity`, `productNumber`, `productDescription`, `productSell`
- **Enum validation:** `recordStatus`, `fulfillmentStatus`, `shipmentType`, `shipment.status`
- **Format validation:** `shipDate` (date), `email` (email format), `trackingURL` (URI)

### Service-Level Validation
1. **ACK Existence:**
   - Query record_header for ACK with matching acknowledgmentNumber
   - Ensure tenantId matches
   - Return 404 if not found

2. **Business Rules:**
   - At least one line item required
   - At least one shipment recommended (but optional per schema)
   - Shipment items must reference valid lineItems (by index or catalogCode)

3. **Data Consistency:**
   - If shipments provided, validate shipment.items references exist in lineItems
   - Validate financial totals if provided

---

## Testing Strategy

### Unit Tests

**Mapper Tests:**
- `ShippingNoticeToRecordMapper.spec.ts`
  - Test mapping of all fields
  - Test enum to list value ID conversion
  - Test object serialization (shippingAddress, financial, shipments)
  - Test edge cases (missing optional fields, empty arrays)

- `RecordToShippingNoticeMapper.spec.ts`
  - Test reverse mapping of all fields
  - Test list value ID to enum conversion
  - Test object deserialization
  - Test line items reconstruction

**Service Tests:**
- `RpcCoreService.spec.ts` (extend existing)
  - Test `createShippingNotices()` with array containing single item
  - Test `createShippingNotices()` with array containing multiple items
  - Test ACK validation (exists, doesn't exist, wrong tenant)
  - Test line items creation
  - Test partial success (one succeeds, one fails)
  - Test error handling (all fail, some fail)

### Integration Tests

**Script:** `scripts/test-shipping-notice-create.ts`

**Test Cases:**
1. **Happy Path (Single Item):**
   - Create shipping notice with all required fields (as array: `[{...}]`)
   - Verify record created in DB with correct recordTypeId (14)
   - Verify additional fields populated correctly
   - Verify line items created
   - Verify response matches input (array format: `[{...}]`)

1b. **Happy Path (Multiple Items):**
   - Create multiple shipping notices (as array: `[{...}, {...}]`)
   - Verify all records created in DB
   - Verify each has correct recordTypeId (14)
   - Verify response returns array with all items

2. **Minimal Payload:**
   - Create with only required fields (as array: `[{...}]`)
   - Verify defaults applied correctly

3. **Array Format:**
   - Submit array with single item: `[{...}]` → verify works
   - Submit array with multiple items: `[{...}, {...}]` → verify all created (for future IN-47/48)

4. **Multiple Shipments:**
   - Create with 2+ shipments in single notice
   - Verify shipments stored as object/collection field

5. **ACK Validation:**
   - Create with non-existent acknowledgmentNumber → 404
   - Create with ACK from different tenant → 404 or 403

6. **Line Items:**
   - Create with multiple line items
   - Verify line items stored correctly
   - Verify shipment.items references work

7. **Error Cases:**
   - Empty array `[]` → 400 (at least one item required)
   - Missing required fields → 400
   - Invalid enum values → 400
   - Invalid date format → 400

**Manual Tests:**
- Swagger UI: Test endpoint with various payloads
- Verify data in DB via `scripts/check-shipping-notice-schema.ts` (extend to read created records)

---

## Implementation Phases

### Phase 1: Database Configuration (Prerequisite)
**Owner:** DB/OrderBahn Team  
**Tasks:**
1. Confirm record_type.id = 14 exists and is correct
2. Create/configure additional fields:
   - Acknowledgment Number (string, required)
   - Ship Date (date, required)
   - Record Status (dropdown, optional) - configure listTypeId
   - Fulfillment Status (dropdown, optional) - configure listTypeId
   - Target Tenant (string, optional)
   - Notice Attachment (string, optional)
   - Shipping Address (object OR individual fields)
   - Financial (object OR individual fields)
   - Shipments (object/collection)
3. Create/configure lineItemsByTypeId for Shipping Notice line items
4. Document field names and IDs for mapping

**Deliverable:** Field configuration document with exact field names and IDs

### Phase 2: DTOs and Enums
**Owner:** RPC Core Team  
**Tasks:**
1. Create `create-shipping-notice.dto.ts` with all DTOs and enums
2. Create `shipping-notice-response.dto.ts`
3. Reuse or extend `LineItemDto` from PO DTOs
4. Add validation decorators
5. Export from `dto/index.ts`

**Deliverable:** Complete DTO files with validation

### Phase 3: Mappers
**Owner:** RPC Core Team  
**Tasks:**
1. Create `ShippingNoticeToRecordMapper`
   - Implement field mapping logic
   - Implement enum to list value ID mapping
   - Implement object serialization
2. Create `RecordToShippingNoticeMapper`
   - Implement reverse mapping logic
   - Implement list value ID to enum mapping
   - Implement object deserialization
3. Add unit tests for both mappers

**Deliverable:** Mapper classes with tests

### Phase 4: Service Layer
**Owner:** RPC Core Team  
**Tasks:**
1. Add `createShippingNotice()` method to `RpcCoreService`
2. Implement ACK validation logic
3. Implement line items creation
4. Add telemetry
5. Add error handling
6. Add unit tests

**Deliverable:** Service method with tests

### Phase 5: Controller
**Owner:** RPC Core Team  
**Tasks:**
1. Add `POST /rpc/v1/shipping-notices` endpoint
2. Add Swagger documentation
3. Add error response documentation
4. Test via Swagger UI

**Deliverable:** Working endpoint with documentation

### Phase 6: Integration Testing
**Owner:** RPC Core Team  
**Tasks:**
1. Create `scripts/test-shipping-notice-create.ts`
2. Test all scenarios (happy path, errors, edge cases)
3. Verify DB data integrity
4. Update `scripts/check-shipping-notice-schema.ts` to read created records

**Deliverable:** Integration test script and verified functionality

### Phase 7: Documentation
**Owner:** RPC Core Team  
**Tasks:**
1. Update API documentation
2. Document field mappings
3. Document enum mappings
4. Create example payloads
5. Document relationship to ACK records

**Deliverable:** Complete API documentation

---

## Dependencies & Prerequisites

### Database Configuration
- ✅ Record type 14 exists
- ⚠️ Additional fields need to be created/configured
- ⚠️ Line items type for Shipping Notice needs to be identified/created
- ⚠️ List types for enums need to be identified/created

### Code Dependencies
- ✅ Record Grid Client (existing)
- ✅ Line Items Client Service (existing)
- ✅ PO/ACK mappers (for pattern reference)
- ✅ Validation infrastructure (class-validator, class-transformer)

### External Dependencies
- OrderBahn field configuration (blocking for Phase 2+)
- ACK records must exist for testing (non-blocking, can mock)

---

## Open Questions & Decisions

### 1. Shipping Address Storage
**Question:** Store as single object field or multiple string fields?  
**Options:**
- A) Single object field `"Shipping Address"` with JSON structure
- B) Multiple fields: `"Shipping Address 1"`, `"Shipping City"`, etc.

**Recommendation:** Option A (single object) for flexibility and consistency with other complex fields.

### 2. Financial Storage
**Question:** Store as single object field or multiple currency fields?  
**Options:**
- A) Single object field `"Financial"` with JSON structure
- B) Multiple fields: `"Freight Cost"`, `"Handling Fee"`, `"Total Cost"`

**Recommendation:** Option A (single object) for consistency.

### 3. Shipment Items Reference
**Question:** How to store shipment.items references to lineItems?  
**Options:**
- A) Store line item indices in shipment.items array
- B) Store catalogCode/productNumber in shipment.items array
- C) Store full line item objects in shipment.items

**Recommendation:** Option A (indices) for simplicity and data consistency.

### 4. Record Number Generation
**Question:** How to generate shipping notice record number?  
**Options:**
- A) `SN-{acknowledgmentNumber}-{timestamp}`
- B) `SN-{acknowledgmentNumber}`
- C) Auto-increment: `SN-0001`, `SN-0002`, etc.
- D) Let client provide in DTO (optional field)

**Recommendation:** Option D (optional, with fallback to Option A if not provided).

### 5. Array vs Single Object in API
**Question:** Schema defines array, but Record Grid Client only accepts single records.  
**Decision:** ✅ **Follow schema exactly, handle conversion in service layer**
- **Request body:** Array of shipping notice objects (required by schema)
  - For IN-46: UI submits `[{...}]` (array with single item)
  - For IN-47/48: API submits `[{...}, {...}, ...]` (array with multiple items)
- **Response body:** Array of shipping notice objects (matches schema)
  - Always returns array format: `[{...}]` or `[{...}, {...}, ...]`
- **Implementation:**
  - Controller accepts array: `@Body() dtos: CreateShippingNoticeDto[]`
  - Service loops through array: `for (const dto of dtos) { ... }`
  - Service calls `recordGridClient.createRecord()` once per item (single record API)
  - Service collects results and returns array
- **Rationale:** Schema compliance, future-proofing, handles batch scenarios
- **Note:** Different from PO/ACK which accept single objects, but that's okay - schema requires array

### 6. Line Items Type ID
**Question:** What is the `lineItemsByTypeId` for Shipping Notice line items?  
**Action:** Query DB or create new type if doesn't exist.

### 7. Enum List Type IDs
**Question:** What are the listTypeIds for:
- Record Status dropdown
- Fulfillment Status dropdown
- Shipment Type dropdown (if configured)
- Shipment Status dropdown (if configured)

**Action:** Query DB or configure new list types.

### 8. ACK Lookup Strategy
**Question:** How to find ACK record by acknowledgmentNumber?  
**Options:**
- A) Query record_header by recordNumber where recordTypeId = 7 (ACK)
- B) Query record_additional_fields for "Acknowledgment Number" field
- C) Use Record Grid MS search endpoint

**Recommendation:** Option A (query by recordNumber) if ACK recordNumber = acknowledgmentNumber. Otherwise Option B.

### 9. Target Tenant Field
**Question:** What is `targetTenant` used for?  
**Action:** Clarify with product owner (Jenniffer).

### 10. Notice Attachment
**Question:** How are attachments stored/retrieved?  
**Action:** Check existing attachment handling in PO/ACK flows.

---

## Success Criteria

### Functional
- ✅ Can create Shipping Notice via `POST /rpc/v1/shipping-notices`
- ✅ Shipping Notice stored as record_type.id = 14
- ✅ All fields correctly mapped to additional_fields
- ✅ Line items correctly stored in line_items table
- ✅ Shipments correctly stored as object/collection field
- ✅ ACK validation works (404 if ACK not found)
- ✅ Response matches schema structure (array format)

### Non-Functional
- ✅ Follows PO/ACK pattern (consistent code structure)
- ✅ Comprehensive error handling
- ✅ Telemetry emitted for monitoring
- ✅ Unit tests coverage > 80%
- ✅ Integration tests cover happy path and error cases
- ✅ API documentation complete

### Future-Proof
- ✅ Schema supports IN-47 (API ingestion - array of notices)
- ✅ Schema supports IN-48 (batch/OCR - array of notices)
- ✅ Field mappings documented for future enhancements

---

## Next Steps

1. **Review this plan** with team and product owner
2. **Resolve open questions** (especially DB field configuration)
3. **Create DB configuration request** for OrderBahn team
4. **Begin Phase 1** (Database Configuration) - coordinate with DB team
5. **Begin Phase 2** (DTOs) once field names confirmed

---

**Document Version:** 1.0  
**Last Updated:** December 2025  
**Author:** RPC Core Team  
**Reviewers:** [To be assigned]

