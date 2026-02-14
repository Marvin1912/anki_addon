#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

IMAGE_NAME="192.168.178.29:5000/anki:latest"
DOCKERFILE_PATH="${SCRIPT_DIR}/Dockerfile"

docker build -f "${DOCKERFILE_PATH}" -t "${IMAGE_NAME}" "${REPO_ROOT}"
docker push "${IMAGE_NAME}"
