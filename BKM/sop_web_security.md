# SOP: Web Security Audit Procedure

**File Path:** `/BKM/sop_web_security.md`  
**Authority:** Andy (Orchestrator)  
**Agent:** Maya (Web Security Auditor)  
**Version:** 1.0 — 2026-04-24

---

## Scope
This SOP applies to all web security audits conducted on live websites or applications within the framework. It covers client-side and application-layer security only — not server infrastructure penetration testing.

---

## Audit Checklist

### 1. Information Disclosure
- [ ] Page title reveals internal system names or platform details
- [ ] HTML source contains internal comments, API keys, credentials, or version info
- [ ] Dev/admin UI elements visible to unauthenticated users
- [ ] Error messages expose stack traces or internal paths
- [ ] URL structure reveals platform or framework (`base44.app`, `vercel.app`, etc.)

### 2. PII Exposure
- [ ] Email addresses in plaintext HTML (harvestable by bots)
- [ ] Phone numbers in plaintext HTML
- [ ] Personal identifiers (ID numbers, addresses) exposed without need
- [ ] Forms that submit PII without HTTPS

### 3. HTTP Security Headers
Check via browser DevTools Network tab or securityheaders.com:
- [ ] `Content-Security-Policy` — prevents XSS
- [ ] `Strict-Transport-Security` — enforces HTTPS
- [ ] `X-Frame-Options` — prevents clickjacking
- [ ] `X-Content-Type-Options: nosniff` — prevents MIME sniffing
- [ ] `Referrer-Policy` — controls referrer leakage
- [ ] `Permissions-Policy` — restricts browser features

### 4. Cookies
- [ ] Session cookies have `Secure` flag
- [ ] Session cookies have `HttpOnly` flag
- [ ] Cookies use `SameSite=Strict` or `SameSite=Lax`

### 5. Forms and Input
- [ ] Forms include CSRF protection
- [ ] Contact forms have rate limiting or CAPTCHA
- [ ] No client-side-only validation (security theater)

### 6. Third-Party Scripts
- [ ] All external scripts are from trusted, necessary sources
- [ ] No abandoned or unverified CDN dependencies
- [ ] Subresource Integrity (SRI) hashes on critical external scripts

### 7. Authentication (if applicable)
- [ ] No unauthenticated access to admin/owner-only features
- [ ] Session tokens not exposed in URL parameters
- [ ] Logout properly destroys session

---

## Severity Classification

| Level    | Definition                                                           |
|----------|----------------------------------------------------------------------|
| Critical | Immediate user harm, credential exposure, or admin access bypass     |
| High     | PII exposure, missing auth on sensitive features, no CSRF protection |
| Medium   | Missing security headers, minor information disclosure               |
| Low      | Best-practice gaps with no immediate exploitability                  |
| Info     | Observations worth noting but not actionable risks                   |

---

## Output Format

```markdown
## [SEC-XX] Finding Name
**Severity:** Critical / High / Medium / Low / Info
**CWE:** CWE-XXX (if applicable)
**Location:** [URL, element, header name]
**Evidence:** [What was found, verbatim]
**Impact:** [What an attacker could do]
**Recommendation:** [Specific fix with implementation note]
```

---

## Rules
1. Document first, fix later — never modify the target during audit.
2. If a finding requires server access to confirm, mark it "Unconfirmed."
3. Always cross-reference findings with OWASP Top 10.
4. Hand all confirmed High/Critical findings to Rex immediately via `/tasks/active_tasks.json`.
