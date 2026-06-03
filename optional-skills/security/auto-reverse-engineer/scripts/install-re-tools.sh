#!/usr/bin/env bash
# install-re-tools.sh --check | --install
# Idempotent check/install of the reverse-engineering toolchain. --check only reports; --install
# attempts installation via the platform package manager (apt / brew). Missing tools are inbox
# requests, not hard stops; the runtime degrades to what is present.
set -uo pipefail

MODE="${1:---check}"

# tool -> probe command (command -v name unless overridden)
TOOLS=(
  "file" "strings" "binwalk" "radare2:r2" "ghidra:ghidraRun" "gdb"
  "objdump" "readelf" "nm" "qemu-system-arm" "qemu-user:qemu-arm"
  "apktool" "jadx" "frida" "tshark" "python3"
)

probe() {  # $1 = tool spec name:cmd  -> echoes "present"/"missing"
  local spec="$1" name cmd
  name="${spec%%:*}"; cmd="${spec##*:}"; [ "$cmd" = "$spec" ] && cmd="$name"
  if command -v "$cmd" >/dev/null 2>&1; then echo present; else echo missing; fi
}

report() {
  echo "== auto-reverse-engineer tool matrix =="
  local missing=()
  for spec in "${TOOLS[@]}"; do
    local name="${spec%%:*}"
    local state; state="$(probe "$spec")"
    printf '  %-18s %s\n' "$name" "$state"
    [ "$state" = "missing" ] && missing+=("$name")
  done
  if [ "${#missing[@]}" -gt 0 ]; then
    echo
    echo "missing: ${missing[*]}"
  fi
}

pkg_install() {
  local pkgs="$1"
  if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update && sudo apt-get install -y $pkgs
  elif command -v brew >/dev/null 2>&1; then
    brew install $pkgs
  else
    echo "no supported package manager (apt-get/brew) found; install manually: $pkgs"
    return 1
  fi
}

case "$MODE" in
  --check)
    report
    ;;
  --install)
    report
    echo
    echo "Attempting install of common tools (review the approval prompt)…"
    # Package names differ across distros/brew; this is best-effort. Ghidra/jadx/apktool/frida
    # often need manual or pipx/npm installs; left as inbox requests if they remain missing.
    pkg_install "binwalk radare2 gdb binutils qemu-user-static tshark" || true
    if command -v pipx >/dev/null 2>&1; then pipx install frida-tools || true; fi
    echo
    echo "Re-checking:"
    report
    echo
    echo "Note: ghidra, jadx, apktool may require manual install; file inbox requests if still missing."
    ;;
  *)
    echo "usage: install-re-tools.sh --check | --install" >&2
    exit 2
    ;;
esac
