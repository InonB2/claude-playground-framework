# Security Headers Audit — Inon Baasov Portfolio Website
**Task:** WEBSITE-001-SEC-04  
**Auditor:** Maya (Web Security Auditor)  
**Date:** 2026-04-30  
**Target:** https://inon-baasov-website.base44.app  
**Stack:** React SPA (JSX) hosted on Base44 managed platform  
**Prepared for:** Rex (implementation)

---

## Executive Summary

The portfolio is a client-rendered React SPA deployed on Base44's proprietary managed hosting platform. There are **zero server-side HTTP security headers** configured — no `_headers` file, no `vercel.json`, no `next.config.js`, no `.htaccess`, and no server middleware of any kind exists in the repository. All header configuration must be implemented either through Base44's platform settings (if available) or by migrating to a hosting environment that supports custom response headers (e.g., Vercel, Netlify, Cloudflare Pages).

Additionally, three secondary findings were identified in the source code that are unrelated to HTTP headers but are within scope of the SOP.

**Risk posture: Medium-High.** No immediate user-data breach risk (no auth, no sensitive data stored), but clickjacking, MIME sniffing, and XSS injection vectors are unmitigated.

---

## Stack Analysis

| Property | Value |
|----------|-------|
| Framework | React 18 (JSX, client-side only) |
| Platform | Base44 managed mini-app hosting |
| Config files | None (no package.json, no build config in repo) |
| Header control surface | Base44 platform layer only (not in codebase) |
| HTTPS | Enforced by Base44 (confirmed by `.base44.app` subdomain) |
| Cookies | None set by this application |
| Forms | Contact form — submits via `mailto:` (no server POST) |
| External origins | `base44.app` (images), `linkedin.com`, `raw.githubusercontent.com`, `family-flow-he.lovable.app`, `trade-pulse-journal-pro.base44.app` |

---

## Findings

---

### [SEC-01] Content-Security-Policy — Missing
**Severity:** High  
**CWE:** CWE-693 (Protection Mechanism Failure)  
**Location:** HTTP response headers — all pages  
**Evidence:** No `Content-Security-Policy` header present. Confirmed by absence of any header configuration in the repository.  
**Impact:** Without CSP, a reflected or stored XSS payload (e.g., injected via an open redirect on Base44's platform or a compromised CDN resource) can execute arbitrary JavaScript in visitors' browsers. It also enables data exfiltration to attacker-controlled origins. For a portfolio site, the attack surface is low but not zero — especially given the `mailto:` contact form encoding user input into a URL.  
**Recommendation:** Add the following policy. It should be set as an HTTP response header (not a `<meta>` tag, which cannot protect against all attack vectors):

```
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https://base44.app https://raw.githubusercontent.com; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self' mailto:
```

**Implementation note for Rex:** The `'unsafe-inline'` allowances are required because this React app injects all styles via inline `style={{}}` props and the `<style>` tag in `Home.jsx`. A future refactor to CSS modules or a stylesheet would allow removing those. Until then, use a nonce-based approach if Base44 supports it, otherwise `'unsafe-inline'` is the practical choice for this stack.  
**Platform action required:** Configure via Base44 dashboard > Custom Headers, or migrate to Vercel/Netlify/Cloudflare Pages for a `_headers` or `vercel.json` file-based approach.

---

### [SEC-02] X-Frame-Options — Missing
**Severity:** High  
**CWE:** CWE-1021 (Improper Restriction of Rendered UI Layers — Clickjacking)  
**Location:** HTTP response headers — all pages  
**Evidence:** No `X-Frame-Options` header present.  
**Impact:** The portfolio page can be embedded in a hidden `<iframe>` on an attacker's site. A visitor could be tricked into clicking "Hire Me" or submitting the contact form while believing they are interacting with a different UI (UI redressing / clickjacking). While monetary damage is limited (no payment flow), reputation damage and visitor data exfiltration via the form are realistic risks.  
**Recommendation:**
```
X-Frame-Options: DENY
```
Note: This is also covered by the `frame-ancestors 'none'` directive in the CSP recommendation above (SEC-01). Both should be set for compatibility with older browsers that do not respect CSP.

---

### [SEC-03] X-Content-Type-Options — Missing
**Severity:** Medium  
**CWE:** CWE-430 (Deployment of Wrong Handler)  
**Location:** HTTP response headers — all pages  
**Evidence:** No `X-Content-Type-Options` header present.  
**Impact:** Without `nosniff`, browsers may MIME-sniff response bodies and execute content as a different type than declared (e.g., treating a malicious upload disguised as an image as JavaScript). For a static SPA with no user uploads this risk is low, but it is a zero-effort baseline hardening.  
**Recommendation:**
```
X-Content-Type-Options: nosniff
```

---

### [SEC-04] Referrer-Policy — Missing
**Severity:** Medium  
**CWE:** CWE-200 (Exposure of Sensitive Information)  
**Location:** HTTP response headers — all pages  
**Evidence:** No `Referrer-Policy` header present. Default browser behaviour sends the full URL as `Referer` on cross-origin navigation.  
**Impact:** When a visitor clicks the LinkedIn link, CV download link (raw.githubusercontent.com), or the live product links, the full URL of the portfolio (`https://inon-baasov-website.base44.app/...`) is sent in the `Referer` header. This is low-risk for this site because there are no private URL parameters, but it is a best-practice gap and will affect analytics accuracy.  
**Recommendation:**
```
Referrer-Policy: strict-origin-when-cross-origin
```
This sends the origin only (no path/query) on cross-origin requests, and the full URL on same-origin requests.

---

### [SEC-05] Permissions-Policy — Missing
**Severity:** Low  
**CWE:** CWE-693 (Protection Mechanism Failure)  
**Location:** HTTP response headers — all pages  
**Evidence:** No `Permissions-Policy` header present.  
**Impact:** Without this header, browser features like camera, microphone, geolocation, and payment APIs are governed only by default browser policies. An XSS payload could attempt to request sensitive permissions in the site's security context. Risk is low given the absence of authenticated features.  
**Recommendation:**
```
Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=(), interest-cohort=()
```
This denies all sensitive browser feature APIs that the portfolio site has no reason to use, and also opts out of FLoC/Topics API.

---

### [SEC-06] Strict-Transport-Security (HSTS) — Unconfirmed / Likely Absent
**Severity:** Medium  
**CWE:** CWE-319 (Cleartext Transmission of Sensitive Information)  
**Location:** HTTP response headers  
**Evidence:** HTTPS is served by Base44's infrastructure. Whether Base44 sets `Strict-Transport-Security` by default is unconfirmed without a live header inspection (tool-based verification is outside this codebase audit). The repository contains no HSTS configuration.  
**Impact:** Without HSTS, a visitor who types the URL without `https://` may be briefly served over HTTP before being redirected — creating a window for SSL stripping attacks on public Wi-Fi.  
**Recommendation:**
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
```
**Action:** Rex should verify via `curl -I https://inon-baasov-website.base44.app` whether Base44 already sets this. If not, request it through the platform dashboard or escalate to Base44 support. Do not add `preload` until the domain is stable and intentionally submitted to the HSTS preload list.

---

## Secondary Findings (Non-Header Issues)

---

### [SEC-07] PII Exposed in HTML Source — Email and Phone
**Severity:** Medium  
**CWE:** CWE-359 (Exposure of Private Personal Information)  
**Location:** `pages/Home.jsx` — README.md, ContactForm, Hero section  
**Evidence:**
- Email `Inonbaasov@gmail.com` appears in plaintext in 3 `href="mailto:..."` anchor tags and 1 `window.location.href = "mailto:..."` call.
- Phone `+972-54-444-5856` appears in `README.md` (not rendered to the live site, but present in the public GitHub repository).
**Impact:** Email address is harvestable by web scrapers and spam bots. Phone number is exposed in the public GitHub repo. Low severity for this use-case since the email is intentionally public, but worth noting.  
**Recommendation:** For the email, consider obfuscating with a simple rot13 or CSS-only trick, or using a contact form that posts to a serverless function rather than `mailto:`. For the phone number, remove from the public repo's README.

---

### [SEC-08] External Links Missing `rel="noopener noreferrer"`
**Severity:** Low  
**CWE:** CWE-601 (URL Redirection to Untrusted Site)  
**Location:** `pages/Home.jsx` — multiple `<a>` tags  
**Evidence:** Several external links use `rel="noopener"` only, without `noreferrer`:
```jsx
<a href="https://linkedin.com/in/inonbaasov" target="_blank" rel="noopener">
<a href="https://raw.githubusercontent.com/..." target="_blank" rel="noopener" download>
```
**Impact:** `rel="noopener"` alone prevents `window.opener` access. `noreferrer` additionally prevents the `Referer` header from being sent and implies `noopener`. Without `noreferrer`, the full page URL is sent in the `Referer` header to LinkedIn and GitHub — compounding the risk from SEC-04.  
**Recommendation:** Change all external `target="_blank"` links to `rel="noopener noreferrer"`.

---

### [SEC-09] Contact Form — No Rate Limiting or CAPTCHA
**Severity:** Low (Info for this stack)  
**CWE:** CWE-799 (Improper Control of Interaction Frequency)  
**Location:** `pages/Home.jsx` — `ContactForm` component  
**Evidence:** The form submits via `window.location.href = "mailto:..."` — it does not POST to any server endpoint. Rate limiting is therefore enforced by the visitor's own mail client, not the site.  
**Impact:** No server-side risk. The `mailto:` approach is actually inherently rate-limited by UX friction (each submission opens a native mail client). No CAPTCHA or rate-limiting needed for this implementation.  
**Note:** If the form is ever migrated to a serverless function (recommended for better UX), rate limiting and CAPTCHA become mandatory. Flag this for future sprints.

---

## Implementation Priority for Rex

| Priority | Finding | Header / Fix | Effort |
|----------|---------|--------------|--------|
| 1 | SEC-01 | Content-Security-Policy | Medium — requires Base44 platform config or migration |
| 2 | SEC-02 | X-Frame-Options: DENY | Low — single header |
| 3 | SEC-06 | HSTS verification | Low — curl check first |
| 4 | SEC-03 | X-Content-Type-Options: nosniff | Low — single header |
| 5 | SEC-04 | Referrer-Policy | Low — single header |
| 6 | SEC-08 | Add `noreferrer` to external links | Low — code change in Home.jsx |
| 7 | SEC-05 | Permissions-Policy | Low — single header |
| 8 | SEC-07 | PII / phone in README | Low — remove phone from README |

---

## Platform Constraint — Critical Note for Rex

**Base44 is a managed mini-app platform.** Unlike Vercel or Netlify, it does not expose a `_headers` file or `vercel.json` equivalent in the repository. All security headers must be configured through one of:

1. **Base44 dashboard** — Check if there is a "Custom Headers" or "Response Headers" panel in the app settings at base44.app. This is the preferred path.
2. **Base44 support request** — If no dashboard option exists, raise a support ticket requesting that the headers be applied at the platform level.
3. **Platform migration** — If Base44 cannot support custom headers, the recommended path is to export the React app to a standard CRA or Vite build and deploy to Vercel (free tier), where a `vercel.json` with headers takes 5 minutes to configure.

Rex: Do not attempt to set security headers via `<meta>` tags in `Home.jsx`. `X-Frame-Options` and `HSTS` are HTTP-header-only directives — `<meta>` equivalents do not exist or are ignored by browsers for those two.

---

## Sign-off

**Auditor:** Maya  
**Status:** Complete — ready for Rex to action  
**Next step:** Rex to check Base44 dashboard for custom header support, then implement in priority order above.
