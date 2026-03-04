# RPC Core Architecture Documentation

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Core Components](#core-components)
4. [Data Flow](#data-flow)
5. [Translation Layer](#translation-layer)
6. [Microservices Integration](#microservices-integration)
7. [Authentication & Security](#authentication--security)
8. [Configuration & No-Code Aspects](#configuration--no-code-aspects)
9. [Deployment](#deployment)

---

## Overview

**RPC Core** is a NestJS-based integration layer that provides a stable RPC facade between COR ERP (external system) and OrderBahn/Strata internal microservices. It handles Purchase Order (PO) data translation, validation, and orchestration.

### Purpose
- **Translation**: Converts between COR ERP Purchase Order format and OrderBahn internal RecordHeader format
- **Reliability**: Provides idempotency, error handling, and audit logging
- **Security**: Implements authentication, rate limiting, and input sanitization
- **Observability**: Emits telemetry and audit logs for monitoring

### Key Features
- ✅ OAuth 2.0 and API Key/Secret authentication
- ✅ Idempotency support (prevents duplicate processing)
- ✅ Field mapping and translation
- ✅ Rate limiting and security headers
- ✅ Telemetry emission to data lake
- ✅ Tenant-based feature flags

---

## System Architecture

### High-Level Architecture

```
┌─────────────────┐
│   COR ERP       │
│  (External)     │
└────────┬────────┘
         │ HTTP/REST
         │ (OAuth 2.0 / API Key)
         ▼
┌─────────────────────────────────────┐
│         RPC Core API                │
│  ┌──────────────────────────────┐  │
│  │  Authentication & Guards     │  │
│  │  - OAuth 2.0                 │  │
│  │  - API Key/Secret             │  │
│  └──────────────────────────────┘  │
│  ┌──────────────────────────────┐  │
│  │  Middleware Stack            │  │
│  │  - Input Sanitization        │  │
│  │  - Correlation ID            │  │
│  │  - Security Headers           │  │
│  │  - Rate Limiting             │  │
│  └──────────────────────────────┘  │
│  ┌──────────────────────────────┐  │
│  │  Translation Layer           │  │
│  │  - PO → RecordHeader         │  │
│  │  - RecordHeader → PO         │  │
│  │  - Field Mapping             │  │
│  └──────────────────────────────┘  │
│  ┌──────────────────────────────┐  │
│  │  Business Logic              │  │
│  │  - Idempotency Service       │  │
│  │  - Validation                │  │
│  │  - Feature Flags             │  │
│  └──────────────────────────────┘  │
└────────┬───────────────────────────┘
         │
         │ HTTP/REST
         ▼
┌─────────────────────────────────────┐
│   OrderBahn Microservices           │
│  ┌──────────┐  ┌──────────┐         │
│  │ Records  │  │  Line    │         │
│  │   Grid   │  │  Items   │         │
│  │    MS    │  │    MS    │         │
│  └──────────┘  └──────────┘         │
│  ┌──────────┐  ┌──────────┐         │
│  │ Tenants  │  │  Lists   │         │
│  │    MS    │  │    MS    │         │
│  └──────────┘  └──────────┘         │
└─────────────────────────────────────┘
         │
         │
         ▼
┌─────────────────────────────────────┐
│   PostgreSQL Database               │
│  - Idempotency Keys                 │
│  - Tenant Configuration             │
└─────────────────────────────────────┘
```

### Technology Stack

- **Framework**: NestJS 9.x (Node.js/TypeScript)
- **Database**: PostgreSQL (via TypeORM)
- **Authentication**: OAuth 2.0 (JWT Bearer tokens) + API Key/Secret
- **HTTP Client**: Axios (@nestjs/axios)
- **Validation**: class-validator, class-transformer
- **Documentation**: Swagger/OpenAPI
- **Logging**: Pino (nestjs-pino)
- **Cloud**: AWS (S3, CloudWatch, Secrets Manager)

---

## Core Components

### 1. Application Module (`app.module.ts`)

**Purpose**: Root module that configures the entire application.

**Key Responsibilities**:
- Configures global modules (ConfigModule, TypeORM, Logger)
- Registers global guards, interceptors, and filters
- Applies middleware stack
- Imports feature modules (RpcCoreModule, TenantsModule, OAuthModule)

**Global Components**:
- `ExternalApiAuthGuard`: Validates OAuth tokens or API keys
- `RateLimitInterceptor`: Enforces rate limiting
- `AuditLoggingInterceptor`: Logs all API requests/responses
- `TelemetryInterceptor`: Emits telemetry to data lake
- `InputSanitizationMiddleware`: Sanitizes input to prevent XSS
- `CorrelationIdMiddleware`: Adds correlation IDs for tracing

### 2. RPC Core Module (`rpc-core.module.ts`)

**Purpose**: Main feature module for Purchase Order operations.

**Key Services**:
- `RpcCoreService`: Orchestrates PO creation, updates, retrieval
- `TranslationService`: Coordinates translation between formats
- `RecordGridClientService`: HTTP client for Records Grid MS
- `LineItemsClientService`: HTTP client for Line Items MS
- `IdempotencyService`: Prevents duplicate processing
- `FieldMappingClientService`: Fetches field definitions
- `ListValuesClientService`: Fetches list values
- `FieldValidatorService`: Validates field existence

**Mappers**:
- `PoToRecordMapper`: Converts PO DTO → RecordHeader DTO
- `RecordToPoMapper`: Converts RecordHeader → PO Response DTO

### 3. Translation Service (`translation.service.ts`)

**Purpose**: Orchestrates translation between COR ERP and OrderBahn formats.

**Key Methods**:
- `translatePoToRecord()`: PO → RecordHeader (for creation)
- `translateRecordToPo()`: RecordHeader → PO (for retrieval)
- `mergePurchaseOrderUpdates()`: Merges updates with existing record
- `validatePurchaseOrder()`: Business rule validation

**Translation Flow**:
1. Receives PO DTO from COR ERP
2. Validates business rules
3. Maps PO fields to RecordHeader additionalFields
4. Handles field name mapping (via FieldNameMapperService)
5. Returns RecordHeader DTO for microservice call

### 4. Field Mapping System

**Components**:
- `field-name-mappings.config.ts`: Static field name aliases
- `field-name-mapper.service.ts`: Dynamic field tag → name mapping
- `field-mapping-client.service.ts`: Fetches field definitions from Records MS
- `field-validator.service.ts`: Validates fields exist before storing

**Field Mapping Strategy**:
1. **Static Mappings**: Pre-configured aliases in `field-name-mappings.config.ts`
   - Example: "PO Date" → ["Date Ordered", "PO Date", "Purchase Order Date"]
2. **Dynamic Mappings**: Fetched from Records MS `/record-types/{id}/fields`
   - Maps field tags (e.g., "1;42091;141") to field names
   - Cached per record type for performance
3. **Validation**: Before storing, validates field exists in record type

### 5. Idempotency Service (`idempotency.service.ts`)

**Purpose**: Prevents duplicate Purchase Order processing.

**Key Features**:
- Extracts idempotency key from:
  1. `X-Idempotency-Key` header (explicit)
  2. `clientOrderId` field (fallback)
  3. PO Number (last resort)
- Stores processed requests with responses in PostgreSQL
- Returns cached response if duplicate detected
- Tenant-isolated (same key can exist for different tenants)
- TTL-based expiration (default 24 hours)

**Database Schema**:
```sql
CREATE TABLE idempotency_keys (
  id SERIAL PRIMARY KEY,
  idempotency_key VARCHAR(255),
  tenant_id INTEGER,
  request_hash VARCHAR(64),
  response_status INTEGER,
  response_body JSONB,
  created_at TIMESTAMP,
  expires_at TIMESTAMP,
  UNIQUE(idempotency_key, tenant_id)
);
```

### 6. Authentication System

**Two Authentication Methods**:

1. **OAuth 2.0 Bearer Token**
   - Endpoint: `POST /oauth/token`
   - Returns JWT token
   - Use: `Authorization: Bearer <token>`

2. **API Key/Secret**
   - Headers: `x-api-key` and `x-api-secret`
   - Validated against tenant credentials

**Implementation**:
- `ExternalApiAuthGuard`: Validates both methods
- `OAuthModule`: Handles OAuth token generation
- Tenant credentials stored in AWS Secrets Manager or database

---

## Data Flow

### Purchase Order Creation Flow

```
1. COR ERP → POST /rpc/v1/purchase-orders
   └─ Headers: Authorization: Bearer <token> OR x-api-key + x-api-secret
   └─ Body: CreatePurchaseOrderDto

2. RPC Core Controller
   └─ Validates authentication (ExternalApiAuthGuard)
   └─ Extracts tenant ID from credentials
   └─ Applies middleware (sanitization, correlation ID, etc.)

3. RpcCoreService.createPurchaseOrder()
   └─ Extracts idempotency key
   └─ Checks for existing response (IdempotencyService)
   └─ If duplicate: returns cached response
   └─ If new: continues processing

4. TranslationService.translatePoToRecord()
   └─ Validates business rules
   └─ Maps PO DTO to RecordHeader DTO
   └─ Uses PoToRecordMapper
   └─ Maps field names via FieldNameMapperService

5. RecordGridClientService.createRecord()
   └─ HTTP POST to Records Grid MS
   └─ Creates RecordHeader with additionalFields

6. LineItemsClientService.createLineItems()
   └─ HTTP POST to Line Items MS
   └─ Creates line items for RecordHeader

7. TranslationService.translateRecordToPo()
   └─ Maps RecordHeader back to PO Response DTO
   └─ Uses RecordToPoMapper

8. IdempotencyService.storeResponse()
   └─ Stores response with idempotency key

9. Returns PurchaseOrderResponseDto to COR ERP
```

### Purchase Order Retrieval Flow

```
1. COR ERP → GET /rpc/v1/purchase-orders/{id}

2. RpcCoreService.getPurchaseOrder()
   └─ Fetches RecordHeader from Records Grid MS
   └─ Fetches Line Items from Line Items MS
   └─ Translates to PO Response DTO
   └─ Returns to COR ERP
```

---

## Translation Layer

### PO DTO Structure (COR ERP Format)

```typescript
{
  poInfo: {
    poNumber: string;
    poDate: string; // ISO 8601 date
    orderStatus: string;
    expectedDeliveryDate?: string;
    paymentTerms?: string;
  };
  vendor: {
    name: string;
    address?: string;
    city?: string;
    state?: string;
    contactAssociated?: string;
    email?: string;
    phone?: string;
  };
  dealer: { ... };
  shipping: { ... };
  installation: { ... };
  billing: { ... };
  financials: { ... };
  lineItems: Array<{
    itemNumber: string;
    description: string;
    quantity: number;
    unitPrice: number;
    totalSell: number;
    // ... more fields
  }>;
}
```

### RecordHeader Structure (OrderBahn Format)

```typescript
{
  recordTypeId: 30; // Purchase Order record type
  recordNumber: string; // PO Number
  additionalFields: Array<{
    fieldName: string; // e.g., "Date Ordered", "Vendor Name"
    value: string | number | date;
    listValues?: Array<{ id: number; value: string }>;
    objectValue?: any;
  }>;
  level: 0;
  isProject: false;
}
```

### Field Mapping Examples

| PO Field | RecordHeader Field Name | Field ID | Notes |
|----------|------------------------|----------|-------|
| `poInfo.poDate` | "Date Ordered" | 253 | Not "PO Date" |
| `poInfo.poNumber` | "PO Number" | 214 | Direct mapping |
| `financials.poTotalAmount` | "Grand Total" | 260 | Not "PO Total" |
| `vendor.name` | "Vendor Name" | 16 | May need verification |
| `dealer.dealerName` | "Dealer Name" | 255 | List field |

---

## Microservices Integration

### Records Grid Microservice

**Base URL**: `RECORDS_GRID_MS_URL` (env var)

**Endpoints Used**:
- `POST /records`: Create RecordHeader
- `GET /records/{id}`: Get RecordHeader
- `PUT /records/{id}`: Update RecordHeader
- `GET /record-types/{id}/fields`: Get field definitions

**Client Service**: `RecordGridClientService`

### Line Items Microservice

**Base URL**: `LINE_ITEMS_MS_URL` (env var)

**Endpoints Used**:
- `POST /line-items`: Create line items
- `GET /line-items`: Get line items for record

**Client Service**: `LineItemsClientService`

### Tenants Microservice

**Base URL**: `TENANTS_MS_URL` (env var)

**Endpoints Used**:
- `GET /tenants/{id}`: Get tenant configuration
- Feature flag checks

**Client Service**: `TenantsClientService`

### Records Microservice

**Base URL**: `RECORDS_MS_URL` (env var)

**Endpoints Used**:
- `GET /lists/{id}/values`: Get list values
- Field mapping endpoints

**Client Services**: `ListValuesClientService`, `FieldMappingClientService`

---

## Authentication & Security

### Authentication Methods

1. **OAuth 2.0**
   - Endpoint: `POST /oauth/token`
   - Request: `{ client_id, client_secret, grant_type: "client_credentials" }`
   - Response: `{ access_token, token_type: "Bearer", expires_in }`
   - Usage: `Authorization: Bearer <token>`

2. **API Key/Secret**
   - Headers: `x-api-key` and `x-api-secret`
   - Validated against tenant credentials

### Security Features

- **Input Sanitization**: XSS prevention via `InputSanitizationMiddleware`
- **Security Headers**: CSP, CORP, Permissions Policy via `SecurityHeadersMiddleware`
- **Rate Limiting**: Configurable per tenant via `RateLimitInterceptor`
- **CORS**: Configured via `CorpMiddleware`
- **Helmet**: Security headers (XSS, HSTS, etc.)
- **HPP**: HTTP Parameter Pollution prevention

### Rate Limiting

**Configuration** (env vars):
- `RATE_LIMIT_WINDOW_MS`: Time window (default: 15 minutes)
- `RATE_LIMIT_MAX_REQUESTS`: Max requests per window (default: 100)
- `RATE_LIMIT_SKIP_SUCCESSFUL`: Skip counting successful requests
- `RATE_LIMIT_SKIP_FAILED`: Skip counting failed requests

**Bypass**: Configured via AWS Secrets Manager for specific tenants/IPs

---

## Configuration & No-Code Aspects

### Environment Variables

See `ENV_VARIABLES_ANALYSIS.md` for complete list.

**Key Categories**:
- Database: `DB_HOST`, `DB_USERNAME`, `DB_PASSWORD`, `DB_PORT`, `DB_NAME`, `DB_SCHEMA`
- Microservices: `RECORDS_GRID_MS_URL`, `RECORDS_MS_URL`, `LINE_ITEMS_MS_URL`, `TENANTS_MS_URL`
- AWS: `AWS_REGION`, `AWS_S3_BUCKET_NAME`, `ATTACHMENTS_BUCKET`
- Rate Limiting: `RATE_LIMIT_WINDOW_MS`, `RATE_LIMIT_MAX_REQUESTS`
- Idempotency: `IDEMPOTENCY_ENABLED`, `IDEMPOTENCY_TTL_MS`
- Telemetry: `TELEMETRY_ENABLED`, `TELEMETRY_LOG_GROUP_NAME`

### Field Name Mappings (No-Code Configuration)

**File**: `src/context/rpc-core/config/field-name-mappings.config.ts`

**Purpose**: Maps RPC Core field names to all possible database field name variations.

**Example**:
```typescript
['PO Date', ['Date Ordered', 'PO Date', 'Purchase Order Date']]
['Order Total', ['Grand Total', 'Amount', 'Order Total', 'PO Total']]
```

**How to Update**:
1. Edit `field-name-mappings.config.ts`
2. Add new field name and aliases
3. Deploy (no code changes needed for mapper logic)

### Record Type Configuration

**Record Type ID**: 30 (Purchase Order)

**Field Definitions**: Fetched dynamically from Records MS `/record-types/30/fields`

**List Values**: Fetched from Records MS `/lists/{id}/values`

### Feature Flags

**Service**: `TenantFeatureFlagService`

**Purpose**: Route tenants to different implementations (e.g., RPC flow vs direct flow)

**Configuration**: Stored in tenant configuration (via Tenants MS)

---

## Deployment

### Docker

**Dockerfile**: Builds NestJS application with Node.js

**Docker Compose**: See `docker-compose.yaml` and `docker-compose.example.yaml`

**Build Args**:
- AWS credentials (for CodeArtifact)
- CodeArtifact repository/domain
- SonarQube token

**Runtime Env Vars**: See `docker-compose.yaml` for full list

### Kubernetes

**Config**: `kubernetes/rpc-core.yaml`

**Components**:
- Deployment
- Service
- ConfigMap (for env vars)
- Secrets (for sensitive data)

### Health Checks

**Endpoint**: `GET /` (root)

**Docker**: Healthcheck configured in `docker-compose.yaml`

**Kubernetes**: Liveness/readiness probes

---

## API Documentation

### Swagger/OpenAPI

**Endpoint**: `GET /docs` (when running)

**Features**:
- Interactive API explorer
- Authentication testing (OAuth 2.0, API Key/Secret)
- Request/response examples
- Schema definitions

### Postman Collections

**Location**: `postman-collections/`

**Files**:
- `RPC-Core-API.postman_collection.json`: Main API collection
- `RPC-Core-API-Environment.postman_environment.json`: Environment variables
- `External API LineItems.postman_collection.json`: Line items examples

---

## Monitoring & Observability

### Logging

**Framework**: Pino (nestjs-pino)

**Log Levels**: `log`, `error`, `warn`, `debug`

**Structured Logging**: JSON format with correlation IDs

### Telemetry

**Service**: `TelemetryService`

**Destination**: AWS CloudWatch Logs

**Data**: HTTP request/response metadata (endpoint, method, status, duration)

**Configuration**: `TELEMETRY_ENABLED`, `TELEMETRY_LOG_GROUP_NAME`

### Audit Logging

**Interceptor**: `AuditLoggingInterceptor`

**Purpose**: Logs all API requests/responses for compliance

**Data**: Request body, response body, headers, tenant ID, user ID

---

## Error Handling

### Exception Filters

- `CorrelationIdExceptionFilter`: Adds correlation ID to error responses
- `AuditExceptionFilter`: Logs exceptions for audit

### Validation Errors

**Format**:
```json
{
  "message": "Validation failed",
  "errors": [
    {
      "field": "poInfo.poNumber",
      "constraints": {
        "isNotEmpty": "poNumber should not be empty"
      }
    }
  ]
}
```

### HTTP Status Codes

- `200 OK`: Success
- `201 Created`: Resource created
- `400 Bad Request`: Validation error
- `401 Unauthorized`: Authentication failed
- `403 Forbidden`: Authorization failed
- `404 Not Found`: Resource not found
- `409 Conflict`: Duplicate (idempotency)
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

---

## Development

### Project Structure

```
src/
├── app.module.ts              # Root module
├── main.ts                    # Application entry point
├── context/
│   ├── rpc-core/              # RPC Core feature module
│   │   ├── config/            # Field mappings (no-code)
│   │   ├── dto/               # Data Transfer Objects
│   │   ├── entities/          # TypeORM entities
│   │   ├── interfaces/        # TypeScript interfaces
│   │   ├── mappers/           # PO ↔ RecordHeader mappers
│   │   ├── services/         # Business logic services
│   │   └── utils/            # Utility functions
│   └── tenants/              # Tenants feature module
└── shared/                    # Shared modules
    ├── filters/              # Exception filters
    ├── guards/               # Authentication guards
    ├── interceptors/          # Request/response interceptors
    ├── middleware/           # HTTP middleware
    └── services/             # Shared services
```

### Scripts

- `npm run build`: Build for production
- `npm run start`: Start production server
- `npm run dev`: Start development server (watch mode)
- `npm run test`: Run unit tests
- `npm run test:e2e`: Run end-to-end tests
- `npm run lint`: Lint code

---

## Future Enhancements

### Planned Features

- [ ] GraphQL support (via @nestjs/graphql)
- [ ] Webhook notifications for PO status changes
- [ ] Batch PO operations
- [ ] Advanced field mapping UI (no-code)
- [ ] Field mapping versioning
- [ ] Multi-tenant field mapping overrides

---

## References

- **Field Mapping Guide**: See `docs/create-fields-guide.md`
- **Field Analysis**: See `docs/check-md-vs-database-analysis.md`
- **Environment Variables**: See `ENV_VARIABLES_ANALYSIS.md`
- **API Examples**: See `postman-collections/` and `examples/`

---

*Last Updated: 2025-01-XX*
*Version: 2.0.0*





