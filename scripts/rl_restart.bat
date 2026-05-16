@echo off
rem Fired by Windows Task Scheduler (ANDY_RL_RESTART) at rate-limit reset.
rem Sends Telegram restart notification and clears the queue file.
rem No claude dependency - just Python stdlib.
cd /d "D:\Claude Playground"
python "D:\Claude Playground\scripts\rate_limit_watchdog.py" on-start
