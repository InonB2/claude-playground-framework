Set-Location "D:\Claude Playground"
$env:CI = "true"
$env:PATH += ";C:\Users\Inon Baasov\AppData\Roaming\npm"

python "D:\Claude Playground\scripts\buildar_notify.py" update "Andy remote session started — resuming paused tasks."

$prompt = @'
You are Andy, the orchestrator. Inon triggered /continue remotely via Telegram and is AWAY from his machine — he cannot type, click, or approve anything until he returns. Telegram is the only channel back to him.

Run this sequence autonomously, then exit. Do NOT idle at a prompt.

1. Send a Telegram reply to Inon (chat_id 6283854178) via the plugin:telegram:telegram reply tool: "Andy resumed — checking work queue."
2. Read tasks/active_tasks.json, agents/roster.md, and the latest file in session_logs/ to load state.
3. Pick the single highest-priority actionable task in Backlog or In Progress that does NOT require Inon's input/approval. Skip anything that needs his judgment.
4. Delegate it to the right specialist agent and execute. Follow the team rules in CLAUDE.md (QA gate, Tested column, etc.).
5. When the task is done OR you hit a blocker, send a Telegram message summarizing: (a) what was done, (b) next step, (c) whether you need Inon when he is back.
6. Exit.

If no task is actionable without Inon, send Telegram saying so with a short list of what's waiting on him, then exit.
'@

$logFile = "D:\Claude Playground\scratchpad\remote_session.log"
"=== Remote session $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ===" | Out-File -Append -Encoding utf8 $logFile

claude -p $prompt --dangerously-skip-permissions 2>&1 | Tee-Object -FilePath $logFile -Append
