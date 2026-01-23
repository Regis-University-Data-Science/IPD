#!/bin/bash
# Start Ray Cluster - Worker Node
# Run this on worker nodes (nickel, zinc, copper, iron)

set -e

echo "==================================="
echo "Starting Ray Cluster - Worker Node"
echo "==================================="

# Activate virtual environment
VENV_DIR="$HOME/venvs/rllib"
if [ -d "$VENV_DIR" ]; then
    source "$VENV_DIR/bin/activate"
    echo "✓ Virtual environment activated"
else
    echo "✗ Virtual environment not found at $VENV_DIR"
    echo "Please run install_ray_cluster.sh first"
    exit 1
fi

# Get hostname
HOSTNAME=$(hostname)

# Configuration - UPDATE THESE VALUES after running start_ray_head.sh
RAY_HEAD_IP="100.116.129.84"  # platinum's Tailscale IP
RAY_PORT=6379
RAY_REDIS_PASSWORD=""  # This will be set from command line or config file

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check for config file
if [ -f "/tmp/ray_cluster_config.sh" ]; then
    echo "Loading configuration from /tmp/ray_cluster_config.sh"
    source /tmp/ray_cluster_config.sh
elif [ -z "$RAY_REDIS_PASSWORD" ]; then
    print_error "Redis password not set!"
    echo "Please provide Redis password:"
    echo "  1. Copy /tmp/ray_cluster_config.sh from head node, or"
    echo "  2. Run: export RAY_REDIS_PASSWORD='<password>'"
    echo "  3. Or run: ./start_ray_worker.sh <password>"
    exit 1
fi

# Override with command line argument if provided
if [ ! -z "$1" ]; then
    RAY_REDIS_PASSWORD="$1"
fi

# Determine number of GPUs
GPU_COUNT=$(nvidia-smi --query-gpu=name --format=csv,noheader | wc -l)
echo "Detected $GPU_COUNT GPUs on $HOSTNAME"

# Check if Ray is already running
if ray status 2>/dev/null; then
    echo "Ray is already running. Stopping it first..."
    ray stop
    sleep 2
fi

# Start Ray worker node
echo ""
echo "Connecting to Ray head at $RAY_HEAD_IP:$RAY_PORT..."
ray start \
    --address="${RAY_HEAD_IP}:${RAY_PORT}" \
    --redis-password="$RAY_REDIS_PASSWORD" \
    --num-gpus=$GPU_COUNT

print_success "Ray worker node started on $HOSTNAME!"

echo ""
echo "==================================="
echo "Worker Node Information"
echo "==================================="
echo "Node Name:         $HOSTNAME"
echo "GPUs:              $GPU_COUNT"
echo "Connected to:      $RAY_HEAD_IP:$RAY_PORT"
echo "==================================="