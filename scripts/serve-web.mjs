import { createServer } from "node:http";
import { createReadStream, existsSync } from "node:fs";
import { extname, join, normalize } from "node:path";

const root = normalize(process.argv[2] || "web");
const requestedPort = Number(process.env.PORT || 3000);
const types = {
  ".css": "text/css",
  ".csv": "text/csv",
  ".html": "text/html",
  ".js": "text/javascript",
  ".json": "application/json",
  ".svg": "image/svg+xml",
};

function handleRequest(request, response) {
  const url = new URL(request.url || "/", "http://localhost");
  const pathname = url.pathname === "/" ? "/index.html" : url.pathname;
  const target = normalize(join(root, pathname));
  if (!target.startsWith(root) || !existsSync(target)) {
    response.writeHead(404);
    response.end("Not found");
    return;
  }
  response.writeHead(200, { "Content-Type": types[extname(target)] || "text/plain" });
  createReadStream(target).pipe(response);
}

function listen(port) {
  const server = createServer((request, response) => {
    handleRequest(request, response);
  });
  server.once("error", (error) => {
    if (error.code === "EADDRINUSE") {
      console.log(`Port ${port} is busy, trying ${port + 1}...`);
      listen(port + 1);
      return;
    }
    throw error;
  });
  server.listen(port, () => {
    console.log(`AssetShield web UI running at http://localhost:${port}`);
  });
}

listen(requestedPort);
