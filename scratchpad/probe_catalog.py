import urllib.request, urllib.error, json
URL = "https://xbfgohafudrfygztqmtg.supabase.co"
SERVICE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhiZmdvaGFmdWRyZnlnenRxbXRnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3ODg0NjMzOCwiZXhwIjoyMDk0NDIyMzM4fQ.cGQeW547rKjnPCet-k2d2muWbO-fIh1ngp8xm222ZHI"
ANON = "sb_publishable_fiJ67_iMjS6p0uoRThMeWw_08S1zfPk"

def req(method, path, key, hdrs=None, body=None):
    h = {"apikey": key, "Authorization": f"Bearer {key}"}
    if hdrs: h.update(hdrs)
    data = None
    if body is not None:
        h["Content-Type"] = "application/json"
        data = json.dumps(body).encode()
    r = urllib.request.Request(URL + path, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(r) as resp:
            return resp.status, resp.read().decode("utf-8","replace"), dict(resp.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8","replace"), dict(e.headers)

# Can we set request.search_path or access pg_catalog tables?
# Try information_schema via PostgREST extra_search_path
for tbl in ["pg_policies", "pg_proc", "pg_constraint"]:
    s,b,_ = req("GET", f"/rest/v1/{tbl}?limit=1", SERVICE)
    print(f"  pg_catalog/{tbl}: HTTP {s}  body[:200]={b[:200]}")

# Check anon SELECT count(*) FROM projects (one-line probe for after-migration)
s,b,h = req("HEAD", "/rest/v1/projects?status=eq.published&select=*", ANON, hdrs={"Prefer":"count=exact","Range":"0-0"})
print(f"  anon published projects count: HTTP {s}  Content-Range={h.get('Content-Range') or h.get('content-range')}")
