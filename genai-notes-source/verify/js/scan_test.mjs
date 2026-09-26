import fs from "fs";
import path from "path";

const extensions = [".js", ".jsx", ".ts", ".tsx", ".html", ".css"];

// ---- original Lecture 7 logic
function listOriginal(directory) {
  const files = [];
  function scan(dir) {
    for (const item of fs.readdirSync(dir)) {
      const fullPath = path.join(dir, item);
      if (fullPath.includes("node_modules") || fullPath.includes("dist") ||
          fullPath.includes("build")) continue;
      const stat = fs.statSync(fullPath);
      if (stat.isDirectory()) scan(fullPath);
      else if (stat.isFile() && extensions.includes(path.extname(item))) files.push(fullPath);
    }
  }
  scan(directory);
  return files;
}

// ---- fixed: compare whole folder NAMES, not substrings of the path
const SKIP_DIRS = new Set(["node_modules", "dist", "build", ".git"]);
function listFixed(directory) {
  const files = [];
  function scan(dir) {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        if (!SKIP_DIRS.has(entry.name)) scan(fullPath);
      } else if (entry.isFile() && extensions.includes(path.extname(entry.name))) {
        files.push(fullPath);
      }
    }
  }
  scan(directory);
  return files;
}

// ---- keep every path the model gives us INSIDE the project folder
function safePath(root, userPath) {
  const base = path.resolve(root);
  const full = path.resolve(base, userPath);
  if (full !== base && !full.startsWith(base + path.sep)) {
    throw new Error(`Path outside the project is not allowed: ${userPath}`);
  }
  return full;
}

console.log("original:", listOriginal("demo").sort());
console.log("fixed:   ", listFixed("demo").sort());
for (const p of ["src/app.js", "../../etc/passwd", "/etc/passwd"]) {
  try { console.log("safePath ok:", path.relative(process.cwd(), safePath("demo", p))); }
  catch (e) { console.log("blocked:", e.message); }
}
