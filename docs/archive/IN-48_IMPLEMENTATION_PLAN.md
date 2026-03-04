# IN-48: BR-003 - Ingest Shipping Notices via OCR (EDI/Batch)
## Complete Implementation Plan

**Ticket:** IN-48  
**Status:** To Do  
**Priority:** High  
**Created:** Oct 20, 2025 | Last Updated: Nov 24, 2025

---

## Executive Summary

### Objective
Implement bulk import functionality for shipping notices from multiple manufacturers via EDI, CSV, or JSON file formats. This enables regional operations users to centralize shipments from global sources without manual entry.

### Key Requirements
1. **File Upload Support** - Accept file uploads via multipart/form-data
2. **Multi-Format Parsing** - Support EDI, CSV, and JSON file formats
3. **Structure Validation** - Validate file structure and log rejected rows
4. **Batch Processing** - Process multiple shipping notices efficiently
5. **Audit Records** - Create audit records per import with success/failure counts
6. **Error Logging** - Log rejected rows with detailed error reasons

### Current State
- ✅ **IN-46 Complete**: UI capture for single shipping notices
- ✅ **IN-47 Complete**: External API for automated shipping notice creation
- ✅ **Infrastructure**: DTOs, mappers, service layer, validation service exist
- ⚠️ **Gaps for IN-48**:
  - No file upload endpoint
  - No file parsing (EDI/CSV/JSON)
  - No batch processing with error logging
  - No import audit records

---

## Implementation Phases

### Phase 1: Requirements Analysis & Design (Days 1-3)

#### 1.1 Define File Format Specifications

**CSV Format:**
- Headers: acknowledgmentNumber, shipDate, shippingAddress.address1, shippingAddress.city, etc.
- Flat structure or nested (JSON in cells)
- Encoding: UTF-8
- Delimiter: Comma (configurable)
- Quote character: Double quotes

**JSON Format:**
- Array of shipping notice objects (same as API format)
- Single object (wrapped in array)
- Newline-delimited JSON (NDJSON) support

**EDI Format:**
- EDI X12 856 (ASN - Advanced Shipping Notice)
- EDI EDIFACT DESADV
- Custom EDI formats (configurable mapping)

**Decision Points:**
- Which EDI standards to support initially?
- CSV structure: flat vs nested?
- File size limits?
- **Recommendation:** Start with JSON and CSV, add EDI in Phase 2

#### 1.2 Design File Upload Endpoint

**Approach:**
- Use NestJS `@UseInterceptors(FileInterceptor)` for file uploads
- Accept `multipart/form-data` with file field
- Support optional metadata (source, manufacturer, etc.)
- File size limit: 50MB (configurable)

**Endpoint Design:**
```
POST /rpc/v1/purchase-orders/shipping-notices/import
Content-Type: multipart/form-data

Fields:
- file: File (required)
- format: 'csv' | 'json' | 'edi' (optional, auto-detect)
- source: string (optional, manufacturer name)
- metadata: JSON string (optional, additional context)
```

#### 1.3 Design Batch Processing Architecture

**Processing Flow:**
1. Upload file → Store temporarily (memory or temp file)
2. Parse file → Extract shipping notice records
3. Validate each record → Collect errors
4. Process valid records → Create shipping notices in batch
5. Generate audit record → Store import results
6. Return summary → Success/failure counts, error details

**Error Handling Strategy:**
- Continue processing on individual record errors
- Collect all errors for reporting
- Return partial success (some records succeed, some fail)
- Detailed error log per rejected row

#### 1.4 Design Audit Record Structure

**Audit Record Fields:**
- Import ID (unique identifier)
- Tenant ID
- User ID (who uploaded)
- File name
- File format (CSV/JSON/EDI)
- Upload timestamp
- Processing status (processing, completed, failed)
- Total records
- Successful records
- Failed records
- Error summary (JSON)
- Processing duration

**Storage:**
- Option A: New database table `shipping_notice_imports`
- Option B: Store in existing audit/logging system
- **Recommendation:** Option A (structured, queryable)

---

### Phase 2: Core Implementation (Days 4-10)

#### 2.1 File Upload Infrastructure

**New DTO:** `ImportShippingNoticesDto`
```typescript
{
  file: Express.Multer.File;
  format?: 'csv' | 'json' | 'edi';
  source?: string;
  metadata?: Record<string, any>;
}
```

**Controller Method:**
- Use `@UseInterceptors(FileInterceptor('file'))`
- Validate file type and size
- Extract metadata from form data
- Call service layer

**File Validation:**
- File size: Max 50MB
- File type: Check extension (.csv, .json, .edi, .txt)
- MIME type validation
- Encoding detection (UTF-8 required)

#### 2.2 File Parser Service

**New Service:** `ShippingNoticeFileParserService`

**Responsibilities:**
- Detect file format (auto-detect or use provided format)
- Parse CSV files
- Parse JSON files (array, single object, NDJSON)
- Parse EDI files (Phase 2 - basic support)
- Handle encoding issues
- Extract shipping notice records

**Methods:**
- `detectFormat(file: Express.Multer.File): 'csv' | 'json' | 'edi'`
- `parseCsv(file: Buffer, options?: CsvParseOptions): CreateShippingNoticeDto[]`
- `parseJson(file: Buffer): CreateShippingNoticeDto[]`
- `parseEdi(file: Buffer, format?: string): CreateShippingNoticeDto[]` (Phase 2)
- `validateFileStructure(file: Buffer, format: string): ValidationResult`

**CSV Parsing:**
- Use `csv-parse` library (or similar)
- Handle headers (first row)
- Map columns to DTO fields
- Handle nested fields (shippingAddress.city → shippingAddress: { city })
- Handle missing/optional columns
- Validate required fields per row

**JSON Parsing:**
- Parse as array of objects
- Handle single object (wrap in array)
- Handle NDJSON (newline-delimited)
- Validate structure matches DTO
- Handle malformed JSON gracefully

#### 2.3 Batch Processing Service

**New Service:** `ShippingNoticeBatchService`

**Responsibilities:**
- Process array of shipping notice DTOs
- Validate each record
- Create shipping notices in batch
- Collect errors per record
- Generate summary report

**Methods:**
- `processBatch(dtos: CreateShippingNoticeDto[], tenantId: number, userId: number, request?: any): BatchProcessResult`
- `validateRecord(dto: CreateShippingNoticeDto, index: number): ValidationResult`
- `createShippingNoticesBatch(dtos: CreateShippingNoticeDto[], tenantId: number, request?: any): BatchCreateResult`

**Batch Processing Strategy:**
- Process in chunks (e.g., 100 records at a time)
- Use existing `createShippingNotices()` method
- Continue on errors (don't fail entire batch)
- Track success/failure per record
- Return detailed results

**Performance Optimization:**
- Parallel processing (configurable concurrency)
- Batch API calls where possible
- Progress tracking for large files
- Memory-efficient streaming for large files

#### 2.4 Import Audit Service

**New Service:** `ShippingNoticeImportAuditService`

**Responsibilities:**
- Create audit records for imports
- Track import status
- Store error summaries
- Query import history

**Methods:**
- `createImportRecord(metadata: ImportMetadata): Promise<ImportAuditRecord>`
- `updateImportStatus(importId: string, status: ImportStatus, results: BatchProcessResult): Promise<void>`
- `getImportHistory(tenantId: number, filters?: ImportFilters): Promise<ImportAuditRecord[]>`

**Database Schema (if new table):**
```sql
CREATE TABLE shipping_notice_imports (
  id SERIAL PRIMARY KEY,
  import_id VARCHAR(255) UNIQUE NOT NULL,
  tenant_id INTEGER NOT NULL,
  user_id INTEGER,
  file_name VARCHAR(500),
  file_format VARCHAR(10),
  source VARCHAR(255),
  upload_timestamp TIMESTAMP DEFAULT NOW(),
  processing_status VARCHAR(20),
  total_records INTEGER,
  successful_records INTEGER,
  failed_records INTEGER,
  error_summary JSONB,
  processing_duration_ms INTEGER,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

**Note:** Since we're not doing DB migrations, use in-memory storage or existing audit system initially.

#### 2.5 Error Logging & Reporting

**Error Structure:**
```typescript
{
  rowIndex: number; // Row number in file (1-based)
  recordIndex: number; // Index in parsed array (0-based)
  errors: Array<{
    field?: string;
    code: string;
    message: string;
  }>;
  rawData?: any; // Original row/record data
}
```

**Error Categories:**
1. **Parse Errors** - File format issues, encoding problems
2. **Validation Errors** - Missing required fields, invalid formats
3. **Business Rule Errors** - ACK not found, duplicate reference, etc.
4. **Processing Errors** - Database errors, microservice failures

**Error Reporting:**
- Per-record error details
- Summary statistics
- Error log file (optional download)
- Error codes for programmatic handling

---

### Phase 3: Integration & Testing (Days 11-14)

#### 3.1 Unit Tests

**Test Coverage:**
- File parser service (all formats)
- Batch processing service
- Import audit service
- Error handling and reporting

**Test Files:**
- `shipping-notice-file-parser.service.spec.ts`
- `shipping-notice-batch.service.spec.ts`
- `shipping-notice-import-audit.service.spec.ts`

#### 3.2 Integration Tests

**Test Scenarios:**
1. **CSV Import:**
   - Valid CSV file with headers
   - CSV with missing columns
   - CSV with invalid data
   - Large CSV file (1000+ records)

2. **JSON Import:**
   - Array of shipping notices
   - Single object (wrapped)
   - NDJSON format
   - Malformed JSON

3. **Batch Processing:**
   - All records succeed
   - Some records fail
   - All records fail
   - Large batch (performance)

4. **Error Handling:**
   - File too large
   - Invalid file format
   - Encoding issues
   - Partial success scenarios

#### 3.3 End-to-End Tests

**Test Scenarios:**
- Full flow: File upload → Parse → Validate → Create → Audit
- Verify audit records are created
- Verify error logs are accurate
- Verify telemetry events are emitted

---

### Phase 4: Documentation & Deployment (Days 15-16)

#### 4.1 API Documentation Updates

**Swagger/OpenAPI Updates:**
- Add file upload endpoint documentation
- Document supported file formats
- Add request/response examples
- Document error responses

**Files to Update:**
- `docs/API_REFERENCE.md`
- `RPC_CORE_ENDPOINTS.md`
- Controller Swagger annotations

#### 4.2 Integration Guide Updates

**New Section:** "Bulk Import Shipping Notices"

**Content:**
- File format specifications
- CSV template and examples
- JSON format examples
- Error handling guide
- Best practices
- Common issues and solutions

**Files to Update:**
- `docs/INTEGRATION_GUIDE.md`

#### 4.3 Release Notes

**Document:**
- New bulk import feature
- Supported file formats
- File size limits
- Known limitations

---

## Technical Architecture

### Component Diagram

```
Regional Operations User
    ↓
POST /rpc/v1/purchase-orders/shipping-notices/import
    (multipart/form-data with file)
    ↓
RpcCoreController.importShippingNotices()
    ↓
[Authentication & Rate Limiting]
    ↓
ShippingNoticeFileParserService
    ├─→ detectFormat()
    ├─→ parseCsv() / parseJson() / parseEdi()
    └─→ validateFileStructure()
    ↓
ShippingNoticeBatchService
    ├─→ validateRecord() (per record)
    ├─→ processBatch()
    └─→ createShippingNoticesBatch()
    ↓
RpcCoreService.createShippingNotices()
    (reuse existing method)
    ↓
ShippingNoticeImportAuditService
    ├─→ createImportRecord()
    └─→ updateImportStatus()
    ↓
Return Import Summary
```

### Data Flow

1. **File Upload** → Controller receives multipart/form-data
2. **File Validation** → Check size, type, encoding
3. **Format Detection** → Auto-detect or use provided format
4. **File Parsing** → Extract shipping notice records
5. **Structure Validation** → Validate file structure
6. **Record Validation** → Validate each record (reuse IN-47 validation)
7. **Batch Processing** → Create shipping notices in batches
8. **Error Collection** → Collect errors per record
9. **Audit Record** → Create import audit record
10. **Response** → Return summary with success/failure counts

### File Processing Flow

```
Uploaded File
    ↓
[Format Detection]
    ├─→ CSV → Parse with csv-parse
    ├─→ JSON → Parse with JSON.parse
    └─→ EDI → Parse with EDI parser (Phase 2)
    ↓
Array of Raw Records
    ↓
[Record Mapping]
    ├─→ CSV: Map columns to DTO fields
    ├─→ JSON: Validate structure matches DTO
    └─→ EDI: Map EDI segments to DTO fields
    ↓
Array of CreateShippingNoticeDto
    ↓
[Batch Validation]
    ├─→ Validate each record
    └─→ Collect errors
    ↓
[Batch Creation]
    ├─→ Process in chunks
    ├─→ Create shipping notices
    └─→ Track success/failure
    ↓
Import Summary
```

---

## File Format Specifications

### CSV Format

**Structure:**
```csv
acknowledgmentNumber,shipDate,shippingAddress.address1,shippingAddress.city,shippingAddress.state,shippingAddress.zip,lineItems[0].catalogCode,lineItems[0].quantity,lineItems[0].productNumber,lineItems[0].productDescription,lineItems[0].productSell
ACK-2025-001,2025-12-15,123 Main St,New York,NY,10001,PROD-001,10,SKU-123,Product Description,99.99
ACK-2025-002,2025-12-16,456 Oak Ave,Los Angeles,CA,90001,PROD-002,5,SKU-456,Another Product,149.99
```

**Nested Field Notation:**
- Use dot notation: `shippingAddress.city`
- Use array notation: `lineItems[0].catalogCode`
- Support multiple line items: `lineItems[1].catalogCode`, etc.

**Alternative: JSON in CSV Cells**
```csv
acknowledgmentNumber,shipDate,shippingAddress,lineItems
ACK-2025-001,2025-12-15,"{""address1"":""123 Main St"",""city"":""New York""}","[{""catalogCode"":""PROD-001"",""quantity"":10}]"
```

**Recommendation:** Support both formats (dot notation preferred, JSON fallback)

### JSON Format

**Array Format (Preferred):**
```json
[
  {
    "acknowledgmentNumber": "ACK-2025-001",
    "shipDate": "2025-12-15",
    "shippingAddress": {
      "address1": "123 Main St",
      "city": "New York",
      "state": "NY",
      "zip": "10001"
    },
    "lineItems": [
      {
        "catalogCode": "PROD-001",
        "quantity": 10,
        "productNumber": "SKU-123",
        "productDescription": "Product Description",
        "productSell": 99.99
      }
    ]
  }
]
```

**Single Object Format:**
```json
{
  "acknowledgmentNumber": "ACK-2025-001",
  ...
}
```
(Will be wrapped in array automatically)

**NDJSON Format (Newline-Delimited):**
```jsonl
{"acknowledgmentNumber":"ACK-2025-001","shipDate":"2025-12-15",...}
{"acknowledgmentNumber":"ACK-2025-002","shipDate":"2025-12-16",...}
```

### EDI Format (Phase 2)

**EDI X12 856 (ASN):**
- Standard EDI X12 format
- Segment-based structure
- Requires EDI parser library

**Initial Support:**
- Basic EDI parsing
- Map common segments to DTO fields
- Custom mapping configuration

---

## Error Handling Strategy

### Error Response Format

**Success Response (200 OK):**
```json
{
  "success": true,
  "importId": "import-2025-12-15-abc123",
  "summary": {
    "totalRecords": 100,
    "successfulRecords": 95,
    "failedRecords": 5,
    "processingDurationMs": 2500
  },
  "errors": [
    {
      "rowIndex": 10,
      "recordIndex": 9,
      "errors": [
        {
          "field": "acknowledgmentNumber",
          "code": "ACK_NOT_FOUND",
          "message": "Acknowledgment 'ACK-INVALID' not found"
        }
      ]
    }
  ],
  "warnings": []
}
```

**Partial Success:**
- Return 200 OK even if some records fail
- Include detailed error information
- Allow client to retry failed records

**Complete Failure:**
- Return 400 Bad Request if file is invalid
- Return 500 Internal Server Error if processing fails

### Error Codes

| Code | Description |
|------|-------------|
| `FILE_TOO_LARGE` | File exceeds size limit |
| `INVALID_FILE_FORMAT` | Unsupported file format |
| `ENCODING_ERROR` | File encoding not UTF-8 |
| `PARSE_ERROR` | File parsing failed |
| `VALIDATION_ERROR` | Record validation failed |
| `ACK_NOT_FOUND` | Acknowledgment not found |
| `DUPLICATE_REFERENCE` | Duplicate reference ID |
| `PROCESSING_ERROR` | Internal processing error |

---

## Performance Considerations

### Optimization Strategies

1. **Streaming Processing:**
   - Stream large files instead of loading into memory
   - Process records in chunks
   - Use Node.js streams for CSV/NDJSON

2. **Parallel Processing:**
   - Process records in parallel (configurable concurrency)
   - Batch API calls
   - Use Promise.all with chunking

3. **Caching:**
   - Cache ACK lookups (reuse IN-47 cache)
   - Cache validation results
   - Reduce redundant microservice calls

4. **Database Optimization:**
   - Batch inserts for audit records
   - Use transactions for consistency
   - Index on import_id, tenant_id

### Performance Targets

- **Small Files (< 100 records):** < 5 seconds
- **Medium Files (100-1000 records):** < 30 seconds
- **Large Files (1000-10000 records):** < 5 minutes
- **Very Large Files (> 10000 records):** Async processing (background job)

### File Size Limits

- **Default:** 50MB
- **Configurable:** Via environment variable
- **Large Files:** Consider async processing or chunked uploads

---

## Security Considerations

### File Upload Security

1. **File Type Validation:**
   - Whitelist allowed file extensions
   - Validate MIME types
   - Reject executable files

2. **File Size Limits:**
   - Enforce maximum file size
   - Prevent DoS attacks
   - Configurable per tenant

3. **Content Validation:**
   - Scan for malicious content (optional)
   - Validate file structure before processing
   - Sanitize file names

4. **Access Control:**
   - Require authentication
   - Tenant isolation
   - Rate limiting per tenant

### Data Validation

1. **Input Sanitization:**
   - Sanitize all parsed data
   - Validate against DTO schemas
   - Prevent injection attacks

2. **Business Logic:**
   - Validate ACK linkage (reuse IN-47)
   - Check duplicate references
   - Enforce tenant boundaries

---

## Dependencies & Prerequisites

### External Dependencies

1. **File Parsing Libraries:**
   - `csv-parse` or `papaparse` for CSV parsing
   - Built-in `JSON.parse` for JSON
   - EDI parser library (Phase 2)

2. **File Upload:**
   - `@nestjs/platform-express` (already included)
   - `multer` (for multipart/form-data)

3. **Existing Services:**
   - `RpcCoreService.createShippingNotices()` (reuse)
   - `ShippingNoticeValidationService` (reuse IN-47)
   - `IdempotencyService` (reuse for duplicate detection)

### Internal Dependencies

1. **Existing Infrastructure:**
   - DTOs: `CreateShippingNoticeDto`
   - Mappers: `ShippingNoticeToRecordMapper`
   - Validation: `ShippingNoticeValidationService`
   - Telemetry: `TelemetryService`

2. **Configuration:**
   - File size limits
   - Batch processing chunk size
   - Parallel processing concurrency
   - Supported file formats

---

## Open Questions & Decisions Needed

### Technical Decisions

1. **File Storage:**
   - Store uploaded files temporarily or process in memory?
   - **Recommendation:** Process in memory for small files, temp file for large files

2. **EDI Support:**
   - Which EDI standards to support initially?
   - **Recommendation:** Start with JSON/CSV, add EDI in Phase 2

3. **Audit Record Storage:**
   - New database table or existing audit system?
   - **Recommendation:** In-memory or existing audit system (no DB migration)

4. **Batch Size:**
   - How many records to process at once?
   - **Recommendation:** 100 records per batch (configurable)

5. **Error Handling:**
   - Fail fast or continue on errors?
   - **Recommendation:** Continue processing, collect all errors

### Business Decisions

1. **File Size Limits:**
   - Maximum file size?
   - **Recommendation:** 50MB default, configurable

2. **Processing Mode:**
   - Synchronous or asynchronous for large files?
   - **Recommendation:** Synchronous for < 1000 records, async for larger

3. **Retry Logic:**
   - Should failed records be retryable?
   - **Recommendation:** Yes, via separate retry endpoint or re-upload

4. **Import History:**
   - How long to keep import audit records?
   - **Recommendation:** 90 days (configurable)

---

## Success Criteria

### Functional Requirements

- ✅ Shipping notices can be imported via CSV file
- ✅ Shipping notices can be imported via JSON file
- ✅ File structure is validated before processing
- ✅ Individual records are validated (reuse IN-47 validation)
- ✅ Errors are logged with row-level details
- ✅ Audit records are created per import
- ✅ Partial success is supported (some records succeed, some fail)

### Non-Functional Requirements

- ✅ File upload completes in < 30 seconds for 1000 records
- ✅ Supports files up to 50MB
- ✅ Handles encoding issues gracefully
- ✅ Clear error messages for troubleshooting
- ✅ 80%+ test coverage

### Acceptance Criteria

1. **Given** a valid CSV file with shipping notices
   **When** it is uploaded and processed
   **Then** valid notices are created and errors are logged for review

2. **Given** a JSON file with shipping notices
   **When** it is uploaded and processed
   **Then** valid notices are created and errors are logged for review

3. **Given** a file with some invalid records
   **When** it is processed
   **Then** valid records are created and invalid records are logged with errors

4. **Given** a large file (1000+ records)
   **When** it is processed
   **Then** processing completes successfully with performance within targets

---

## Timeline & Milestones

### Week 1: Design & Planning
- **Day 1-2:** Requirements analysis, file format specifications
- **Day 3:** Technical design review, architecture approval

### Week 2: Core Implementation
- **Day 1-2:** File upload infrastructure
- **Day 3-4:** File parser service (CSV, JSON)
- **Day 5:** Batch processing service

### Week 3: Integration & Testing
- **Day 1-2:** Import audit service
- **Day 3-4:** Integration and unit tests
- **Day 5:** End-to-end testing

### Week 4: Documentation & Deployment
- **Day 1-2:** Documentation updates
- **Day 3:** Code review and fixes
- **Day 4:** Staging deployment and testing
- **Day 5:** Production deployment

**Total Estimated Time:** 4 weeks (20 working days)

---

## Risk Assessment & Mitigation

### Technical Risks

1. **Risk:** Large file processing causes memory issues
   - **Mitigation:** Use streaming, process in chunks, set file size limits

2. **Risk:** CSV parsing fails on malformed data
   - **Mitigation:** Robust error handling, skip invalid rows, detailed logging

3. **Risk:** Performance degradation with large batches
   - **Mitigation:** Batch processing, parallel processing, performance testing

### Business Risks

1. **Risk:** Users upload incorrect file formats
   - **Mitigation:** Clear documentation, file format validation, helpful error messages

2. **Risk:** Import failures cause data loss
   - **Mitigation:** Audit records, error logging, retry mechanism

3. **Risk:** Security vulnerabilities in file upload
   - **Mitigation:** File type validation, size limits, content scanning

---

## Post-Implementation

### Monitoring & Metrics

**Key Metrics to Track:**
- Import success rate
- Average processing time
- File size distribution
- Error rate by error type
- Most common validation errors

**Alerts to Configure:**
- High failure rate (> 20%)
- Slow processing times (> 1 minute for 100 records)
- Large file uploads (> 10MB)

### Future Enhancements

1. **EDI Support:**
   - Full EDI X12 856 support
   - EDI EDIFACT DESADV
   - Custom EDI mapping configuration

2. **Async Processing:**
   - Background job processing for large files
   - Email notifications on completion
   - Progress tracking API

3. **Import Templates:**
   - CSV template download
   - Format validation before upload
   - Sample files

4. **Retry Mechanism:**
   - Retry failed records
   - Export failed records for correction
   - Re-import corrected records

---

## Conclusion

This implementation plan provides a comprehensive roadmap for completing IN-48. The approach builds upon existing IN-46 and IN-47 infrastructure while adding bulk import capabilities for CSV, JSON, and eventually EDI formats.

The phased approach allows for incremental development, starting with CSV and JSON support, with EDI support as a future enhancement. The estimated 4-week timeline is realistic given the scope and complexity.

**Next Steps:**
1. Review and approve this plan
2. Make technical decisions on open questions
3. Begin Phase 1: Requirements Analysis & Design
4. Set up project tracking and milestones

---

**Document Version:** 1.0  
**Last Updated:** December 2025  
**Author:** Implementation Team  
**Status:** Ready for Review


