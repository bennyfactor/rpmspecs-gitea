#!/bin/bash
# Test-build the gitea RPM inside an AlmaLinux container with podman, so the
# host rpmdb is never touched and no mock setup is needed.
#
# Usage: scripts/container-build.sh <el8|el9> [rpmbuild args...]
#   rpmbuild args default to -ba. Examples:
#     scripts/container-build.sh el8                      # full build
#     scripts/container-build.sh el9 -bp                  # %prep only
#     scripts/container-build.sh el8 --target aarch64 -bp # check arch selection
#
# Remote Source files are downloaded once into $RPMSPECS_GITEA_CACHE
# (default ~/.cache/rpmspecs-gitea/sources) and reused. Results land in
# build/<el8|el9>/. Set POST_CMD to a shell snippet to run inside the
# container after rpmbuild (e.g. to inspect ~/rpmbuild/BUILD).
set -euo pipefail

tag=${1:?usage: $0 <el8|el9> [rpmbuild args...]}
shift
case $tag in
  el8) img=docker.io/library/almalinux:8 ;;
  el9) img=docker.io/library/almalinux:9 ;;
  *) echo "unknown target '$tag' (want el8 or el9)" >&2; exit 2 ;;
esac
args=("$@")
[ ${#args[@]} -eq 0 ] && args=(-ba)

repo=$(cd "$(dirname "$0")/.." && pwd)
cache=${RPMSPECS_GITEA_CACHE:-$HOME/.cache/rpmspecs-gitea/sources}
out=$repo/build/$tag
mkdir -p "$cache" "$out"

exec podman run --rm \
  -v "$repo/rpm:/src:ro,Z" \
  -v "$cache:/root/rpmbuild/SOURCES:Z" \
  -v "$out:/out:Z" \
  -e POST_CMD="${POST_CMD:-}" \
  -e NO_BUILDDEP="${NO_BUILDDEP:-}" \
  "$img" bash -euo pipefail -c '
    dnf -y -q install epel-release >/dev/null
    dnf -y -q install rpm-build rpmdevtools dnf-plugins-core xz systemd file rpmlint >/dev/null
    cd /root/rpmbuild/SOURCES
    cp /src/* .
    # Fetch remote sources not already cached.
    spectool -l -S gitea.spec | awk "{print \$2}" | grep -E "^https?://" | while read -r url; do
      f=${url##*/}
      [ -s "$f" ] || { echo "downloading $f"; curl -sSfL -o "$f" "$url"; }
    done
    [ -n "$NO_BUILDDEP" ] || dnf -y -q builddep gitea.spec >/dev/null
    rpmbuild "$@" gitea.spec
    find /root/rpmbuild/RPMS /root/rpmbuild/SRPMS -name "*.rpm" -exec cp {} /out/ \; 2>/dev/null || true
    [ -z "$POST_CMD" ] || eval "$POST_CMD"
  ' -- "${args[@]}"
