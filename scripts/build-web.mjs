import { cp, mkdir, rm } from "node:fs/promises";

await rm("dist", { recursive: true, force: true });
await mkdir("dist", { recursive: true });
await cp("web", "dist", { recursive: true });
await mkdir("dist/data", { recursive: true });
await cp("data/assets.csv", "dist/data/assets.csv");
await cp("data/fortyguard_cache.json", "dist/data/fortyguard_cache.json");

console.log("Built static Vercel app in dist/");
