/**
 * cc_server.js — Andy C&C Dashboard Server
 *
 * Serves dashboard/ as static files on port 3000 (same port as `npx serve`).
 * Adds /health and /restart endpoints for remote management.
 * Zero npm dependencies — pure Node.js stdlib only.
 *
 * Start:   node scripts/cc_server.js
 * Health:  http://localhost:3000/health
 * Restart: http://localhost:3000/restart   (GET or POST)
 *
 * Designed to be run under Windows Task Scheduler with restart-on-failure.
 * The /restart endpoint exits with code 0, and the scheduler re-launches it.
 */

"use strict";

const http  = require("http");
const fs    = require("fs");
const path  = require("path");
const { spawn } = require("child_process");

const PORT        = 3000;
const ROOT        = path.resolve(__dirname, "..");          // D:\Claude Playground
const DASHBOARD   = path.join(ROOT, "dashboard");
const START_TIME  = Date.now();
const RESTART_KEY = process.env.CC_RESTART_KEY || "";      // optional secret; empty = open

// ── MIME types ────────────────────────────────────────────────────────────────
const MIME = {
  ".html": "text/html; charset=utf-8",
  ".css":  "text/css; charset=utf-8",
  ".js":   "application/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".png":  "image/png",
  ".jpg":  "image/jpeg",
  ".svg":  "image/svg+xml",
  ".ico":  "image/x-icon",
  ".woff2":"font/woff2",
  ".woff": "font/woff",
  ".ttf":  "font/ttf",
};

// ── Static file server ────────────────────────────────────────────────────────
function serveFile(res, filePath) {
  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404, { "Content-Type": "text/plain" });
      res.end("Not found");
      return;
    }
    const ext  = path.extname(filePath).toLowerCase();
    const mime = MIME[ext] || "application/octet-stream";
    res.writeHead(200, {
      "Content-Type":  mime,
      "Cache-Control": "no-cache",
      "X-Powered-By":  "Andy-CC",
    });
    res.end(data);
  });
}

// ── JSON response helper ──────────────────────────────────────────────────────
function json(res, statusCode, obj) {
  const body = JSON.stringify(obj, null, 2);
  res.writeHead(statusCode, {
    "Content-Type":                "application/json; charset=utf-8",
    "Access-Control-Allow-Origin": "*",
  });
  res.end(body);
}

// ── Restart helper ────────────────────────────────────────────────────────────
function doRestart(res) {
  json(res, 200, {
    status:  "restarting",
    message: "Server will restart in ~2 seconds. Refresh the dashboard after 10s.",
    uptime:  Math.floor((Date.now() - START_TIME) / 1000),
  });

  // Give the response time to flush, then exit.
  // Task Scheduler will re-launch the process automatically.
  setTimeout(() => {
    console.log("[cc_server] /restart triggered — exiting for auto-restart.");
    process.exit(0);
  }, 1500);
}

// ── Request router ────────────────────────────────────────────────────────────
const server = http.createServer((req, res) => {
  const url    = new URL(req.url, `http://localhost:${PORT}`);
  const method = req.method.toUpperCase();

  // ── /health ──────────────────────────────────────────────────────────────
  if (url.pathname === "/health") {
    return json(res, 200, {
      status:     "ok",
      uptime:     Math.floor((Date.now() - START_TIME) / 1000),
      uptimeHuman: (() => {
        const s = Math.floor((Date.now() - START_TIME) / 1000);
        const h = Math.floor(s / 3600);
        const m = Math.floor((s % 3600) / 60);
        const sec = s % 60;
        return `${h}h ${m}m ${sec}s`;
      })(),
      pid:        process.pid,
      node:       process.version,
      timestamp:  new Date().toISOString(),
    });
  }

  // ── /restart ─────────────────────────────────────────────────────────────
  if (url.pathname === "/restart" && (method === "GET" || method === "POST")) {
    // Optional secret check
    if (RESTART_KEY && url.searchParams.get("key") !== RESTART_KEY) {
      return json(res, 403, { status: "forbidden", message: "Invalid key" });
    }
    return doRestart(res);
  }

  // ── Static files ──────────────────────────────────────────────────────────
  // Resolve path relative to dashboard/
  let relPath = url.pathname;
  if (relPath === "/" || relPath === "") relPath = "/index.html";

  // Security: prevent directory traversal
  const absPath = path.resolve(DASHBOARD, relPath.replace(/^\//, ""));
  if (!absPath.startsWith(DASHBOARD)) {
    res.writeHead(403, { "Content-Type": "text/plain" });
    return res.end("Forbidden");
  }

  // If path is a directory, try index.html inside it
  fs.stat(absPath, (err, stat) => {
    if (!err && stat.isDirectory()) {
      return serveFile(res, path.join(absPath, "index.html"));
    }
    serveFile(res, absPath);
  });
});

// ── Start ─────────────────────────────────────────────────────────────────────
server.listen(PORT, "0.0.0.0", () => {
  console.log(`[cc_server] Andy C&C Dashboard running on http://0.0.0.0:${PORT}`);
  console.log(`[cc_server] Serving: ${DASHBOARD}`);
  console.log(`[cc_server] Health:  http://localhost:${PORT}/health`);
  console.log(`[cc_server] Restart: http://localhost:${PORT}/restart`);
  console.log(`[cc_server] PID: ${process.pid}`);
});

server.on("error", (err) => {
  if (err.code === "EADDRINUSE") {
    console.error(`[cc_server] Port ${PORT} already in use. Exiting.`);
    process.exit(1);
  }
  throw err;
});

process.on("SIGTERM", () => { console.log("[cc_server] SIGTERM — shutting down."); process.exit(0); });
process.on("SIGINT",  () => { console.log("[cc_server] SIGINT — shutting down.");  process.exit(0); });
