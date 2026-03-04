# Field Mapping Caching Strategy - Review & Recommendations

## Current Implementation Analysis

### Current Caching Strategy

**File:** `src/context/rpc-core/services/field-mapping-client.service.ts`

**Current Setup:**
- **Cache Type:** In-memory Map (lost on server restart)
- **Cache TTL:** 1 hour (3,600,000 milliseconds)
- **Cache Size Limit:** 10 record types maximum
- **Cache Eviction:** LRU (Least Recently Used) - oldest entry removed when limit reached
- **Cache Scope:** Per record type (e.g., Record Type 30 = Purchase Orders)

**What Gets Cached:**
- Field ID → Field Name mapping
- Field Name → Field ID mapping (with dataType, listTypeId)
- Field Tag → Field Name mapping

**When Cache is Used:**
- First request: Calls microservice, caches result
- Subsequent requests (within 1 hour): Uses cache (no microservice call)
- After 1 hour: Cache expires, calls microservice again

---

## Your Question: Why Not Use ENV File?

### Why Field Definitions CAN Change

**Reasons field definitions change:**
1. **New Fields Added** - OrderBahn admins add new fields to Purchase Order record type
2. **Field Names Updated** - Field names can be renamed in OrderBahn UI
3. **Field IDs Can Change** - Rare, but possible during system migrations
4. **Field Types Change** - Data type or list type can be modified
5. **Multi-Tenant Differences** - Different tenants might have different field configurations (though current code assumes same across tenants)

### Current System Behavior

**First Request After Server Start:**
- Calls microservice: `GET /record-types/30/fields`
- Caches result in memory
- Uses cache for next 1 hour

**Subsequent Requests (Within 1 Hour):**
- Uses cached data (no microservice call)
- Very fast (in-memory lookup)

**After 1 Hour:**
- Cache expires
- Next request calls microservice again
- Updates cache

---

## Pros & Cons Analysis

### Current Approach (Microservice + In-Memory Cache)

#### ✅ **Pros:**
1. **Dynamic Updates** - Automatically picks up field changes without redeployment
2. **Multi-Tenant Support** - Can handle different field configs per tenant (if needed)
3. **No Manual Maintenance** - No need to update config files when fields change
4. **Already Cached** - Most requests use cache (no network call)
5. **Handles Edge Cases** - Works when fields are added/removed dynamically

#### ❌ **Cons:**
1. **Network Dependency** - First request after cache expiry requires microservice call
2. **Latency on Cache Miss** - ~50-200ms per microservice call
3. **Cache Lost on Restart** - In-memory cache cleared when server restarts
4. **Microservice Dependency** - If Records MS is down, field mapping fails
5. **Cache Expiry Overhead** - Every hour, first request is slower

---

### ENV File / Config File Approach

#### ✅ **Pros:**
1. **Zero Network Calls** - No microservice dependency
2. **Faster** - Instant lookup (no network latency)
3. **Works Offline** - No dependency on microservice availability
4. **Predictable** - Same data every time
5. **No Cache Expiry** - No periodic slowdowns

#### ❌ **Cons:**
1. **Static Data** - Won't reflect field changes without code deployment
2. **Manual Maintenance** - Need to update file when fields change
3. **Deployment Required** - Every field change needs code deployment
4. **Multi-Tenant Complexity** - Hard to manage different configs per tenant
5. **Risk of Stale Data** - If fields change in OrderBahn, config file becomes outdated
6. **Large Config Files** - Purchase Order has 100+ fields, config file would be large

---

## Recommendation: Hybrid Approach

### Best Solution: **Persistent Cache with Long TTL + Fallback**

#### **Option 1: Redis Cache (Recommended for Production)**

**Implementation:**
- Use Redis for persistent cache (survives server restarts)
- Cache TTL: **24 hours** (instead of 1 hour)
- Fallback: If Redis unavailable, use in-memory cache
- Cache invalidation: Manual trigger or webhook when fields change

**Benefits:**
- ✅ Fast (Redis is fast)
- ✅ Persistent (survives restarts)
- ✅ Shared across multiple server instances
- ✅ Can be invalidated when fields change
- ✅ Still dynamic (updates every 24 hours)

**Trade-offs:**
- Requires Redis infrastructure
- Slight complexity increase

---

#### **Option 2: File-Based Cache (Good for Single Instance)**

**Implementation:**
- Cache field definitions to JSON file: `cache/field-definitions-30.json`
- Cache TTL: **24 hours**
- On startup: Load from file if exists and not expired
- On cache miss: Fetch from microservice, save to file

**Benefits:**
- ✅ No network calls after first fetch (until expiry)
- ✅ Survives server restarts
- ✅ Simple implementation
- ✅ Still dynamic (updates every 24 hours)

**Trade-offs:**
- File I/O (but very fast for small JSON)
- Need file system access
- Not shared across instances

---

#### **Option 3: Config File with Manual Refresh (Current + Enhancement)**

**Implementation:**
- Keep current in-memory cache
- Add config file: `config/field-definitions-30.json` (optional)
- On startup: Load from config file if exists
- Use config file as initial cache
- Still call microservice to refresh (but less frequently)

**Benefits:**
- ✅ Fast startup (no microservice call on first request)
- ✅ Works if microservice is down initially
- ✅ Can be manually updated when needed
- ✅ Still dynamic (microservice updates cache)

**Trade-offs:**
- Manual maintenance if you want to update config file
- Two sources of truth (config file + microservice)

---

## Specific Recommendations

### **For Your Use Case:**

#### **Short-Term (Quick Win):**
1. **Increase Cache TTL** from 1 hour to **24 hours**
   - **File:** `field-mapping-client.service.ts`
   - **Change:** `CACHE_TTL = 86400000` (24 hours)
   - **Impact:** Reduces microservice calls by 96% (from every hour to once per day)
   - **Risk:** Low - field definitions rarely change

#### **Medium-Term (Better Solution):**
2. **Add File-Based Cache**
   - Save cache to `cache/field-definitions-{recordTypeId}.json`
   - Load on startup if file exists and not expired
   - Save after fetching from microservice
   - **Impact:** Zero microservice calls after first fetch (until 24h expiry)
   - **Risk:** Low - simple file I/O

#### **Long-Term (Production Ready):**
3. **Use Redis Cache**
   - Persistent, shared, fast
   - Can be invalidated via webhook when fields change
   - **Impact:** Best performance + reliability
   - **Risk:** Requires Redis infrastructure

---

## Why NOT Pure ENV File?

### **Problems with Pure ENV File:**

1. **Field Changes Happen** - Even if rare, they do happen:
   - New fields added: "Installation Contact Email" (new field)
   - Field names updated: "PO Date" → "Date Ordered" (name changed)
   - Field IDs can change during migrations

2. **Deployment Overhead** - Every field change requires:
   - Update config file
   - Commit to git
   - Deploy new version
   - Restart server
   - **vs.** Current: Automatic update within 24 hours

3. **Multi-Tenant Complexity** - If different tenants have different fields:
   - Need separate config per tenant
   - ENV file becomes very large
   - Hard to manage

4. **Stale Data Risk** - If OrderBahn admin adds field but config file not updated:
   - New field won't be mapped
   - Data might be lost or stored incorrectly
   - Silent failures

---

## Recommended Action Plan

### **Immediate (5 minutes):**
```typescript
// In field-mapping-client.service.ts
private readonly CACHE_TTL = 86400000; // 24 hours instead of 1 hour
```
**Impact:** Reduces microservice calls by 96%

### **Next Sprint (2-4 hours):**
Implement file-based cache:
- Save to `cache/field-definitions-{recordTypeId}.json`
- Load on startup
- Update when cache expires

**Impact:** Zero microservice calls after first fetch

### **Future (When Scaling):**
Move to Redis cache for multi-instance deployments

---

## Performance Impact Analysis

### **Current (1 hour TTL):**
- **Microservice calls:** ~24 per day per record type
- **Cache hits:** ~99% of requests (after first call)
- **Latency on cache miss:** ~50-200ms

### **With 24 hour TTL:**
- **Microservice calls:** ~1 per day per record type
- **Cache hits:** ~99.96% of requests
- **Latency on cache miss:** ~50-200ms (but only once per day)

### **With File Cache:**
- **Microservice calls:** ~1 per day per record type (only if file expired)
- **Cache hits:** ~100% of requests (after first fetch)
- **Latency on cache miss:** ~50-200ms (but only once per day)
- **Startup latency:** ~0ms (loads from file)

---

## Conclusion

**Your intuition is correct** - field definitions don't change often, so we can optimize caching.

**Best Approach:**
1. ✅ **Keep calling microservice** (for dynamic updates)
2. ✅ **Increase cache TTL to 24 hours** (quick win)
3. ✅ **Add file-based cache** (better persistence)
4. ❌ **Don't use pure ENV file** (too static, maintenance burden)

**Why this is better than ENV file:**
- Still dynamic (auto-updates)
- Much faster (24h cache vs every request)
- No manual maintenance
- Handles field changes automatically
- Works across multiple server instances

**The current system is actually good** - it just needs a longer cache TTL and persistent storage.

---

**Last Updated:** 2025-01-XX



