#!/bin/bash
# Grade the guide's solutions with the practice repo's own Playwright tests.
# usage: verify/run.sh [path-to-a-clone-of-accenture-frontend-practice]
# Without a path it clones the repo into a temporary folder. Your clone is never changed:
# the solutions are copied into a temporary copy of it.
# Set PW_CHROMIUM=/path/to/chrome to use an already-installed Chromium.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
if [ -n "$1" ]; then
  cp -r "$1" "$WORK/repo"
else
  git clone -q --depth 1 https://github.com/dexterhere04/accenture-frontend-practice.git "$WORK/repo"
fi
cd "$WORK/repo"
[ -d node_modules/@playwright/test ] || npm install --silent
for dir in "$HERE"/exercises/*/; do
  name="$(basename "$dir")"
  cp "$dir"* "exercises/$name/"
done
cat > verify.config.js <<'JS'
const base = require('./playwright.config.js');
const exe = process.env.PW_CHROMIUM;
const launch = exe ? { launchOptions: { executablePath: exe } } : {};
module.exports = {
  ...base,
  projects: [{ name: 'chromium', use: { ...base.projects[0].use, ...launch } }],
};
JS
names=$(ls "$HERE/exercises")
npx playwright test -c verify.config.js $names
