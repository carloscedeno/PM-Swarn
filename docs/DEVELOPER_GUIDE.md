# RPC Core Developer Guide

**Version:** 2.0.0  
**Target Audience:** Internal developers, contributors

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Service Structure](#service-structure)
3. [Adding New Endpoints](#adding-new-endpoints)
4. [Testing Guidelines](#testing-guidelines)
5. [Deployment Process](#deployment-process)
6. [Monitoring & Observability](#monitoring--observability)

---

## Architecture Overview

RPC Core is a NestJS application that acts as an integration layer between COR ERP and OrderBahn microservices.

### Core Components

```
┌─────────────┐
│ COR ERP     │
└──────┬──────┘
       │ HTTP/REST
       ▼
┌─────────────────┐
│  RPC Core API   │
│  (NestJS)       │
└──────┬──────────┘
       │
       ├─► Translation Layer
       ├─► Validation
       ├─► Retry Logic (IN-38)
       │
       ▼
┌─────────────────┐
│ OrderBahn MS    │
│ (Record Grid)   │
└─────────────────┘
```

### Key Modules

- **RpcCoreModule**: Main feature module
- **TelemetryModule**: CloudWatch logging
- **RetryModule**: Retry logic with exponential backoff (IN-38)
- **OAuthModule**: OAuth 2.0 token generation

---

## Service Structure

### Directory Layout

```
src/
├── context/
│   └── rpc-core/
│       ├── dto/              # Data Transfer Objects
│       ├── services/          # Business logic
│       ├── mappers/           # Data transformation
│       ├── config/            # Configuration
│       └── utils/             # Utilities
├── shared/
│   ├── service/
│   │   ├── retry/            # Retry service (IN-38)
│   │   └── telemetry/        # Telemetry service
│   ├── guards/               # Authentication guards
│   ├── interceptors/         # Request/response interceptors
│   └── middleware/           # Request middleware
└── app.module.ts             # Root module
```

### Key Services

#### RpcCoreService
Main orchestration service. Coordinates:
- Translation
- Validation
- Microservice communication
- Idempotency checks

#### TranslationService
Handles data transformation:
- PO DTO → RecordHeader
- RecordHeader → PO Response
- Field name mapping
- Validation

#### RecordGridClientService
HTTP client for Record Grid microservice:
- CRUD operations
- Retry logic (IN-38)
- Error handling

#### RetryService (IN-38)
Implements retry logic:
- Exponential backoff (1s, 2s, 4s)
- 3 retry attempts
- Dead-letter queue logging

---

## Adding New Endpoints

### Step 1: Create DTO

```typescript
// src/context/rpc-core/dto/create-custom.dto.ts
import { ApiProperty } from '@nestjs/swagger';
import { IsString, IsRequired } from 'class-validator';

export class CreateCustomDto {
  @ApiProperty({ description: 'Custom field' })
  @IsString()
  @IsRequired()
  customField: string;
}
```

### Step 2: Add Controller Method

```typescript
// src/context/rpc-core/rpc-core.controller.ts
@Post('custom')
@ApiOperation({ summary: 'Create Custom Resource' })
async createCustom(
  @Body() createDto: CreateCustomDto,
  @Req() request: any,
): Promise<CustomResponseDto> {
  const tenantId = request.tenant?.id;
  return this.rpcCoreService.createCustom(createDto, tenantId, request);
}
```

### Step 3: Add Service Method

```typescript
// src/context/rpc-core/rpc-core.service.ts
async createCustom(
  dto: CreateCustomDto,
  tenantId: number,
  request?: any,
): Promise<CustomResponseDto> {
  // Business logic here
  // Use retry service for HTTP calls
  const result = await this.retryService.executeWithRetry(
    () => this.httpService.post(url, data),
    'CustomService',
    { method: 'POST', url }
  );
  
  return result;
}
```

### Step 4: Add Tests

```typescript
// test/rpc-core/rpc-core.service.spec.ts
describe('createCustom', () => {
  it('should create custom resource', async () => {
    // Test implementation
  });
});
```

---

## Testing Guidelines

### Unit Tests

Test individual services and utilities:

```typescript
describe('TranslationService', () => {
  it('should translate PO to RecordHeader', () => {
    // Test translation logic
  });
});
```

### Integration Tests

Test API endpoints:

```typescript
describe('POST /rpc/v1/purchase-orders', () => {
  it('should create purchase order', async () => {
    const response = await request(app.getHttpServer())
      .post('/rpc/v1/purchase-orders')
      .set('x-api-key', 'test-key')
      .set('x-api-secret', 'test-secret')
      .send(validPoData)
      .expect(201);
  });
});
```

### Running Tests

```bash
# Unit tests
npm test

# Integration tests
npm run test:integration

# E2E tests
npm run test:e2e
```

---

## Deployment Process

### 1. Build

```bash
npm run build
```

### 2. Test

```bash
npm test
npm run test:integration
```

### 3. Deploy

Deployment is handled via CI/CD pipeline. Ensure:
- Environment variables are set
- Database migrations are run
- Health checks pass

### Environment Variables

```env
# Database
DB_HOST=...
DB_PORT=5432
DB_USERNAME=...
DB_PASSWORD=...

# Microservices
RECORDS_GRID_MS_URL=http://localhost:4001
LINE_ITEMS_MS_URL=http://localhost:4001

# AWS (for telemetry)
AWS_REGION=us-east-1
CLOUDWATCH_LOG_GROUP=rpc-core-logs
```

---

## Monitoring & Observability

### Logging

All requests are logged with:
- Correlation ID
- Tenant ID
- User ID
- Request/response details

### Telemetry

Telemetry events are emitted to CloudWatch:
- Request metrics
- Error rates
- Performance metrics

### Dead-Letter Queue

Failed requests (after 3 retries) are logged:
- Full error details
- Request context
- Timestamp
- Retry attempts

**Location:** Application logs (search for `[DEAD-LETTER-QUEUE]`)

### Health Checks

```http
GET /health
```

Returns service health status.

---

## Code Style

### TypeScript

- Use strict mode
- Prefer interfaces for types
- Use async/await over promises
- Document public methods

### NestJS Patterns

- Use dependency injection
- Follow module structure
- Use decorators for validation
- Implement proper error handling

---

## Common Tasks

### Adding Field Mapping

1. Edit `src/context/rpc-core/config/field-name-mappings.config.ts`
2. Add mapping: `['COR_Field', ['OrderBahn_Field', 'Alias1']]`
3. Deploy

### Adding Retry Logic

Already integrated via `RetryService`. Use:

```typescript
await this.retryService.executeWithRetry(
  () => this.httpService.post(url, data),
  'ServiceName',
  { method: 'POST', url }
);
```

### Adding Telemetry

Telemetry is automatic via `TelemetryInterceptor`. No code changes needed.

---

## Resources

- **Architecture**: See `ARCHITECTURE.md`
- **API Reference**: See `API_REFERENCE.md`
- **NestJS Docs**: https://docs.nestjs.com
- **TypeScript Docs**: https://www.typescriptlang.org/docs

---

*Last Updated: 2025-01-15*  
*Version: 2.0.0*

