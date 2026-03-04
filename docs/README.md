# RPC Core Documentation

Welcome to the RPC Core documentation. This directory contains comprehensive documentation for developers, product owners, and operations teams.

---

## 📚 Quick Navigation

### For Developers
1. **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System architecture and design
2. **[DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md)** - Development guidelines and practices
3. **[API_REFERENCE.md](./API_REFERENCE.md)** - Complete API reference

### For Product Owners
1. **[PO-GUIDE-TRANSLATIONS-AND-NOCODE.md](./PO-GUIDE-TRANSLATIONS-AND-NOCODE.md)** - Translations and no-code configuration
2. **[SCHEMA_VERIFICATION.md](./SCHEMA_VERIFICATION.md)** - Schema and field status
3. **[OPERATIONS_FIELD_CREATION_REQUEST.md](./OPERATIONS_FIELD_CREATION_REQUEST.md)** - Database field creation requests

### For Integration Teams
1. **[INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md)** - Integration guide for customers
2. **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** - One-page cheat sheet
3. **[API_REFERENCE.md](./API_REFERENCE.md)** - Complete API documentation

---

## 📖 Documentation Index

### Core Documentation

#### API Documentation
- **[API_REFERENCE.md](./API_REFERENCE.md)** - Complete API reference
  - All endpoints documented with examples
  - Request/response formats
  - Authentication guide
  - Error handling
  - Rate limiting and idempotency

- **[INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md)** - Integration guide for customers
  - Getting started
  - Authentication setup
  - First API call
  - Common integration patterns
  - Best practices and troubleshooting

- **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** - One-page cheat sheet
  - Common endpoints
  - Authentication headers
  - Error codes
  - Sample requests

#### Architecture & Technical
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Complete system architecture
  - System overview and diagrams
  - Core components and services
  - Data flow and translation layer
  - Microservices integration
  - Authentication & security
  - Deployment guide

- **[DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md)** - Developer guide for internal teams
  - Architecture overview
  - Service structure
  - Adding new endpoints
  - Testing guidelines
  - Deployment process
  - Monitoring and observability

#### Product Owner Guides
- **[PO-GUIDE-TRANSLATIONS-AND-NOCODE.md](./PO-GUIDE-TRANSLATIONS-AND-NOCODE.md)** - Product Owner guide
  - How to record new translations
  - Field name mapping (no-code configuration)
  - Field creation process
  - Troubleshooting translation issues
  - Best practices

- **[SCHEMA_VERIFICATION.md](./SCHEMA_VERIFICATION.md)** - Schema and field verification
  - Complete field status
  - Database field mapping
  - Schema comparison
  - Data persistence status
  - Verification results

- **[OPERATIONS_FIELD_CREATION_REQUEST.md](./OPERATIONS_FIELD_CREATION_REQUEST.md)** - Database field creation
  - Field specifications
  - Creation requirements
  - Priority and status

#### Training & Release Notes
- **[TRAINING_SESSION_GUIDE.md](./TRAINING_SESSION_GUIDE.md)** - Training facilitator guide
  - 2-hour training session structure
  - Step-by-step guide
  - Hands-on exercises
  - Q&A section

- **[RELEASE_NOTES_v2.0.0.md](./RELEASE_NOTES_v2.0.0.md)** - Version 2.0.0 release notes
  - New features
  - Breaking changes
  - Migration guide
  - Deprecations

---

## 🗂️ Archive & Historical Documentation

### Archive Directories

- **[archive/](./archive/)** - Archived documentation
  - Historical implementation plans
  - Outdated test results
  - Superseded documentation

- **[test-results/](./test-results/)** - Historical test results
  - Endpoint testing reports
  - Performance test results
  - Validation test results

- **[analysis/](./analysis/)** - Technical analysis
  - Code reviews
  - Troubleshooting guides
  - Design decision documentation
  - Technical deep-dives

---

## 🔑 Key Concepts

### Translations

A **translation** converts data between COR ERP format and OrderBahn format:
- **COR ERP Format**: Purchase Order DTO (nested objects)
- **OrderBahn Format**: RecordHeader with additionalFields (flat structure)

### Field Mappings

**Field mappings** are no-code configurations that map field names:
- COR ERP sends: "PO Date"
- OrderBahn expects: "Date Ordered"
- Mapping: `['PO Date', ['Date Ordered', 'PO Date', 'Purchase Order Date']]`

### No-Code Configuration

**No-code configuration** means you can update field mappings without writing code:
- Edit `src/context/rpc-core/config/field-name-mappings.config.ts`
- Deploy (TypeScript compiles automatically)
- No code logic changes needed

---

## 🚀 Common Tasks

### Adding a New Field Mapping

1. Open `src/context/rpc-core/config/field-name-mappings.config.ts`
2. Add mapping: `['COR_ERP_FIELD', ['OrderBahn_Field', 'Alias1', 'Alias2']]`
3. Deploy

### Troubleshooting Translation Issues

1. Check logs for field mapping warnings
2. Verify field exists in OrderBahn
3. Check field mapping configuration
4. Test with Postman/Swagger
5. See troubleshooting section in PO guide

### Requesting Database Field Creation

1. Review [SCHEMA_VERIFICATION.md](./SCHEMA_VERIFICATION.md) for field status
2. Check [OPERATIONS_FIELD_CREATION_REQUEST.md](./OPERATIONS_FIELD_CREATION_REQUEST.md) for specifications
3. Submit request to operations team

---

## 📊 Documentation Status

### ✅ Complete & Up-to-Date
- API Reference
- Integration Guide
- Architecture Documentation
- Developer Guide
- Schema Verification

### 📝 Maintenance Required
- Release Notes (update for new versions)
- Training Guide (update as features change)

---

## 🔗 Related Resources

- **Root Documentation:**
  - `RPC_CORE_ENDPOINTS.md` - Complete endpoint list
  - `RPC_ENDPOINTS_COMPLETE_SCHEMA.md` - Complete schema documentation
  - `SCHEMA_VERIFICATION_REPORT.md` - Schema verification report
  - `REPOSITORY_OVERVIEW.md` - Repository overview

- **API Documentation:**
  - Swagger UI: `http://localhost:3000/docs` (when running)
  - OpenAPI JSON: `http://localhost:3000/docs-json`

- **Testing:**
  - Postman Collections: `postman-collections/` directory
  - Test Scripts: `scripts/` directory (see [scripts/README.md](../scripts/README.md))

---

## 📞 Support

For questions or issues:
- Check relevant documentation above
- Review troubleshooting sections
- Contact development team
- Open an issue in the repository

---

**Last Updated:** December 2025  
**Version:** 2.0.0  
**Maintained By:** RPC Core Development Team
