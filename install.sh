#!/usr/bin/env bash
set -euo pipefail

DEST="${HOME}/.local/bin"
mkdir -p "$DEST"
cp "$(cd "$(dirname "$0")" && pwd)/autocode.py" "$DEST/autocode"
chmod +x "$DEST/autocode"

case ":$PATH:" in
  *":$DEST:"*) ;;
  *)
    echo "Add this to your shell profile:"
    echo "  export PATH=\"$DEST:\$PATH\""
    ;;
esac

echo "Installed: $DEST/autocode"
echo "Try: autocode 'fix this small bug' --dry-run"
