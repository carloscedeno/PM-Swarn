# Documentation Structure

**Last Updated:** December 2025

---

## 📁 Current Structure

### Core Documentation (Main `docs/` folder)

#### Essential Guides
- **README.md** - Main documentation index and navigation
- **API_REFERENCE.md** - Complete API reference with examples
- **ARCHITECTURE.md** - System architecture and design
- **DEVELOPER_GUIDE.md** - Development guidelines
- **INTEGRATION_GUIDE.md** - Customer integration guide
- **QUICK_REFERENCE.md** - One-page cheat sheet

#### Product Owner & Operations
- **PO-GUIDE-TRANSLATIONS-AND-NOCODE.md** - Translations and no-code config
- **SCHEMA_VERIFICATION.md** - Schema and field verification (consolidated)
- **OPERATIONS_FIELD_CREATION_REQUEST.md** - Database field creation specs

#### Training & Release
- **TRAINING_SESSION_GUIDE.md** - Training facilitator guide
- **RELEASE_NOTES_v2.0.0.md** - Version 2.0.0 release notes

### Archive Directories

#### `archive/` - Historical Documentation
- Implementation plans (IN-48, Shipping Notice)
- Superseded schema verification files
- Outdated field verification reports
- Cleanup summaries

#### `test-results/` - Historical Test Results
- Endpoint testing reports
- Performance test results
- Validation test results
- Comparison documents

#### `analysis/` - Technical Analysis
- Code reviews
- Troubleshooting guides
- Design decision documentation
- Technical deep-dives

---

## 📊 Documentation Statistics

### Main Documentation
- **Core Docs:** 11 files
- **Archive:** 12 files
- **Test Results:** 8 files
- **Analysis:** 7 files

### Consolidation Results
- **Before:** 20+ files in main docs folder
- **After:** 11 essential files
- **Consolidated:** 4 schema files → 1 comprehensive file
- **Archived:** 9 redundant/historical files

---

## 🎯 Documentation Principles

### Keep in Main Folder
- Active, frequently referenced documentation
- Guides for current development
- API and integration documentation
- Current status and verification docs

### Move to Archive
- Historical implementation plans
- Superseded verification reports
- Outdated test results
- Completed project documentation

### Move to Analysis
- Technical deep-dives
- Design decision explanations
- Troubleshooting guides
- Code review documents

---

## 🔄 Maintenance Guidelines

### Adding New Documentation
1. Determine category (core, archive, test-results, analysis)
2. Follow naming conventions
3. Update README.md if it's core documentation
4. Link from appropriate index

### Updating Documentation
1. Keep core docs up-to-date
2. Archive outdated versions if major changes
3. Update version numbers and dates
4. Maintain cross-references

### Deprecating Documentation
1. Move to archive if historical value
2. Delete if completely obsolete
3. Update README.md to remove references
4. Document reason for deprecation

---

## 📚 Quick Reference

### For Developers
→ Start with [ARCHITECTURE.md](./ARCHITECTURE.md) and [DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md)

### For Product Owners
→ Start with [PO-GUIDE-TRANSLATIONS-AND-NOCODE.md](./PO-GUIDE-TRANSLATIONS-AND-NOCODE.md)

### For Integration Teams
→ Start with [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) and [API_REFERENCE.md](./API_REFERENCE.md)

### For Operations
→ See [OPERATIONS_FIELD_CREATION_REQUEST.md](./OPERATIONS_FIELD_CREATION_REQUEST.md) and [SCHEMA_VERIFICATION.md](./SCHEMA_VERIFICATION.md)

---

*This structure ensures documentation is organized, accessible, and maintainable.*

