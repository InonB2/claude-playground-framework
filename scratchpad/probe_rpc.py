import urllib.request, urllib.error, json
URL = "https://xbfgohafudrfygztqmtg.supabase.co"
SERVICE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhiZmdvaGFmdWRyZnlnenRxbXRnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3ODg0NjMzOCwiZXhwIjoyMDk0NDIyMzM4fQ.cGQeW547rKjnPCet-k2d2muWbO-fIh1ngp8xm222ZHI"

# List RPC functions
r = urllib.request.Request(URL + "/rest/v1/", headers={"apikey": SERVICE, "Authorization": f"Bearer {SERVICE}"})
with urllib.request.urlopen(r) as resp:
    spec = json.loads(resp.read())
    paths = spec.get("paths", {})
    rpcs = [p for p in paths if p.startswith("/rpc/")]
    print("RPCs exposed:", rpcs)

# Try common exec_sql names
for fname in ["exec_sql", "query", "execute", "run_sql", "exec", "pg_query"]:
    try:
        r = urllib.request.Request(URL + f"/rest/v1/rpc/{fname}",
            data=json.dumps({"sql": "SELECT 1"}).encode(),
            headers={"apikey": SERVICE, "Authorization": f"Bearer {SERVICE}", "Content-Type":"application/json"},
            method="POST")
        with urllib.request.urlopen(r) as resp:
            print(fname, "OK:", resp.read()[:200])
    except urllib.error.HTTPError as e:
        print(fname, e.code, e.read()[:120].decode(errors='replace'))
