#!/usr/bin/env bash
# Deploy the essay page (index.html + styles.css) via curl using credentials
# in .deploy.env (gitignored). Chart JS/JSON/PNG assets already on the server
# are unchanged by a restyle deploy; upload those separately if they change.
#
# .deploy.env must define:
#   DEPLOY_URL   upload target dir for the essay, trailing slash required,
#                e.g. ftp://ftp.zarrenkuzma.com/public_html/nyc-felony-assault-crisis/
#   DEPLOY_USER  hosting FTP/SSH username
#   DEPLOY_PASS  hosting FTP/SSH password
#   DEPLOY_EXTRA optional extra curl flags (e.g. --insecure for a self-signed cert)
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ ! -f .deploy.env ]]; then
  echo "FAIL: .deploy.env not found (see header of this script for the format)" >&2
  exit 1
fi
source .deploy.env

npx --yes html-validate site/index.html

FLAGS=(--fail --show-error --silent)
[[ "$DEPLOY_URL" == ftp://* ]] && FLAGS+=(--ssl-reqd)  # upgrade plain FTP to explicit FTPS

for f in index.html styles.css; do
  curl "${FLAGS[@]}" ${DEPLOY_EXTRA:-} -T "site/$f" --user "$DEPLOY_USER:$DEPLOY_PASS" "$DEPLOY_URL"
  echo "uploaded site/$f"
done

# Best-effort deletion of chart-07 orphans on the server. curl -Q runs quote
# commands after login but BEFORE CWDing into the URL path, so DELE needs the
# path from DEPLOY_URL prefixed. Failures are tolerated: leftover orphans are
# harmless (nothing references them after this deploy).
DEPLOY_PATH="/${DEPLOY_URL#*://*/}"   # e.g. /public_html/nyc-felony-assault-crisis/
for orphan in js/chart-07.js assets/charts/07-beds.png data/chart-07.json; do
  curl "${FLAGS[@]}" ${DEPLOY_EXTRA:-} --user "$DEPLOY_USER:$DEPLOY_PASS" \
    -Q "DELE ${DEPLOY_PATH}${orphan}" "$DEPLOY_URL" -o /dev/null \
    || echo "note: could not delete ${orphan} (already gone, or DELE refused) — harmless orphan"
done

echo "Deployed. Verify:"
echo "  curl -sI https://www.zarrenkuzma.com/nyc-felony-assault-crisis/ | head -3"
echo "  curl -s -o /dev/null -w '%{http_code}\n' https://www.zarrenkuzma.com/nyc-felony-assault-crisis/styles.css"
