#!/bin/bash
# Start Ray Cluster - Head Node
# Run this on platinum (orchestrator node)

set -e

echo "==================================="
echo "Starting Ray Cluster - Head Node"
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

# Configuration
HEAD_NODE_IP="100.116.129.84"  # platinum's Tailscale IP
RAY_PORT=6379
DASHBOARD_PORT=8265
REDIS_PASSWORD=$(openssl rand -hex 16)

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if Ray is already running
if ray status 2>/dev/null; then
    print_warning "Ray cluster is already running. Stopping it first..."
    ray stop
    sleep 2
fi

# Start Ray head node
echo ""
echo "Starting Ray head node on $HEAD_NODE_IP..."
ray start \
    --head \
    --port=$RAY_PORT \
    --dashboard-host=0.0.0.0 \
    --dashboard-port=$DASHBOARD_PORT \
    --redis-password=$REDIS_PASSWORD \
    --num-gpus=1 \
    --include-dashboard=true

print_success "Ray head node started!"

# Save connection info to file
cat > /tmp/ray_cluster_config.sh <<EOF
# Ray Cluster Configuration
# Generated on $(date)
export RAY_HEAD_IP="$HEAD_NODE_IP"
export RAY_PORT=$RAY_PORT
export RAY_REDIS_PASSWORD="$REDIS_PASSWORD"
export RAY_ADDRESS="${HEAD_NODE_IP}:${RAY_PORT}"
EOF

print_success "Configuration saved to /tmp/ray_cluster_config.sh"

echo ""
echo "==================================="
echo "Ray Head Node Information"
echo "==================================="
echo "Head Node IP:      $HEAD_NODE_IP"
echo "Ray Port:          $RAY_PORT"
echo "Dashboard:         http://$HEAD_NODE_IP:$DASHBOARD_PORT"
echo "Redis Password:    $REDIS_PASSWORD"
echo ""
echo "To connect worker nodes, run on each worker:"
echo "  ray start --address='$HEAD_NODE_IP:$RAY_PORT' --redis-password='$REDIS_PASSWORD'"
echo ""
echo "Or use the start_ray_workers.sh script"
echo "==================================="

# Display cluster status
sleep 2
echo ""
echo "Current cluster status:"
ray status