# Security Headers — Base44 Action Required
**Author:** Rex (Senior Frontend Developer)
**Date:** 2026-05-01
**Related audit:** owner_inbox/security_headers_audit.md (Maya)
**Findings in scope:** SEC-01 through SEC-06

---

## Status

HTTP security headers (SEC-01 through SEC-06) CANNOT be set from within the React source
code on Base44. These are HTTP response headers that must be configured at the platform
(server) level. No `_headers` file, `vercel.json`, or `.htaccess` equivalent exists in this
repository because Base44 does not expose that mechanism in the codebase.

Code-level fixes already implemented (this session):
- SEC-07: Email obfuscated in source (runtime assembly via `_m()` helper); phone removed from README
- SEC-08: All external `<a target="_blank">` links updated to `rel="noopener noreferrer"`

---

## Action Required from Inon (Base44 Dashboard)

Log in to https://base44.app, open the portfolio app settings, and look for a
"Custom Headers" or "Response Headers" panel. Add the following headers:

### 1. Content-Security-Policy (HIGH — SEC-01)
```
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https://base44.app https://raw.githubusercontent.com; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self' mailto:
```
Note: `'unsafe-inline'` is required because this React app uses inline `style={{}}` props
throughout. A future refactor to CSS modules would allow removing it.

### 2. X-Frame-Options (HIGH — SEC-02)
```
X-Frame-Options: DENY
```
Prevents clickjacking. Also covered by `frame-ancestors 'none'` in CSP above.

### 3. X-Content-Type-Options (MEDIUM — SEC-03)
```
X-Content-Type-Options: nosniff
```

### 4. Referrer-Policy (MEDIUM — SEC-04)
```
Referrer-Policy: strict-origin-when-cross-origin
```

### 5. Permissions-Policy (LOW — SEC-05)
```
Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=(), interest-cohort=()
```

### 6. Strict-Transport-Security (MEDIUM — SEC-06)
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
```
First verify: run `curl -I https://inon-baasov-website.base44.app` to check if Base44 already
sets this. Only add if it is absent. Do NOT add `preload` until the domain is stable.

---

## If Base44 Dashboard Has No Custom Headers Panel

Escalate to Base44 support requesting platform-level header injection.
Alternatively, migrate to Vercel (free tier) where a `vercel.json` with a `headers` block
takes under 10 minutes to configure.

**Do NOT migrate to Vercel without Inon's explicit sign-off** — this is a platform decision.

---

## TASK 2: Custom Domain TODO

A `SITE_URL` constant was added to `pages/Home.jsx` as a single source of truth for the
site URL used in og:url, schema.org JSON-LD, and any future canonical tags.

Current value: `"https://TODO-SET-CUSTOM-DOMAIN.com"` (placeholder)

To fix: Set up a custom domain in the Base44 dashboard, then update `SITE_URL` in
`pages/Home.jsx` line 6 to the real domain.
