#!/bin/bash
# Manage Ray RLlib Cluster
# Orchestrates startup, shutdown, and status checking across all nodes
# Run from platinum (head node)

set -e

# Configuration
HEAD_NODE="platinum"
WORKER_NODES=("nickel" "zinc" "copper" "iron")
HEAD_NODE_IP="100.116.129.84"  # platinum's Tailscale IP
RAY_PORT=6379
DASHBOARD_PORT=8265
VENV_DIR="$HOME/venvs/rllib"
CONFIG_FILE="/tmp/ray_cluster_config.sh"

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if virtual environment exists
check_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        print_error "Virtual environment not found at $VENV_DIR"
        echo "Please run install_ray_cluster.sh first"
        exit 1
    fi
}

# Start head node
start_head() {
    echo "==================================="
    echo "Starting Ray Head Node on $HEAD_NODE"
    echo "==================================="
    
    source "$VENV_DIR/bin/activate"
    
    # Check if Ray is already running
    if ray status &>/dev/null; then
        print_warning "Ray is already running. Stopping it first..."
        ray stop
        sleep 2
    fi
    
    # Generate Redis password
    REDIS_PASSWORD=$(openssl rand -hex 16)
    
    # Start Ray head node
    echo ""
    print_info "Starting Ray head node on $HEAD_NODE_IP..."
    ray start \
        --head \
        --port=$RAY_PORT \
        --dashboard-host=0.0.0.0 \
        --dashboard-port=$DASHBOARD_PORT \
        --redis-password=$REDIS_PASSWORD \
        --num-gpus=1 \
        --include-dashboard=true
    
    print_success "Head node started successfully"
    
    # Save connection configuration
    cat > "$CONFIG_FILE" <<EOF
# Ray Cluster Configuration
# Generated on $(date)
export RAY_HEAD_IP="$HEAD_NODE_IP"
export RAY_PORT=$RAY_PORT
export RAY_REDIS_PASSWORD="$REDIS_PASSWORD"
export RAY_ADDRESS="${HEAD_NODE_IP}:${RAY_PORT}"
EOF
    
    print_success "Configuration saved to $CONFIG_FILE"
    print_info "Dashboard available at: http://$HEAD_NODE_IP:$DASHBOARD_PORT"
}

# Distribute config to workers
distribute_config() {
    echo ""
    print_info "Distributing cluster configuration to worker nodes..."
    
    for node in "${WORKER_NODES[@]}"; do
        echo -n "  Copying config to $node... "
        if scp -q "$CONFIG_FILE" "dhart@$node:$CONFIG_FILE"; then
            print_success "done"
        else
            print_error "failed"
        fi
    done
}

# Start worker nodes
start_workers() {
    echo ""
    echo "==================================="
    echo "Starting Worker Nodes"
    echo "==================================="
    
    # Source config to get Redis password
    source "$CONFIG_FILE"
    
    for node in "${WORKER_NODES[@]}"; do
        echo ""
        print_info "Starting worker on $node..."
        
        # SSH to node and start Ray worker
        ssh "dhart@$node" "bash -s" <<WORKER_SCRIPT
set -e

# Activate venv
source "$VENV_DIR/bin/activate"

# Stop any existing Ray instance
if ray status &>/dev/null; then
    ray stop
    sleep 2
fi

# Determine GPU count
GPU_COUNT=\$(nvidia-smi --query-gpu=name --format=csv,noheader | wc -l)

# Start Ray worker
ray start \\
    --address="$RAY_HEAD_IP:$RAY_PORT" \\
    --redis-password="$RAY_REDIS_PASSWORD" \\
    --num-gpus=\$GPU_COUNT

echo "Worker started on $node with \$GPU_COUNT GPUs"
WORKER_SCRIPT
        
        if [ $? -eq 0 ]; then
            print_success "$node connected"
        else
            print_error "$node failed to connect"
        fi
        
        sleep 2
    done
}

# Start the cluster
start_cluster() {
    echo "=== Starting Ray RLlib Cluster ==="
    echo ""
    
    check_venv
    start_head
    distribute_config
    start_workers
    
    echo ""
    echo "==================================="
    echo "Cluster Startup Complete"
    echo "==================================="
    
    # Show status
    sleep 3
    source "$VENV_DIR/bin/activate"
    ray status
    
    echo ""
    print_success "Cluster ready!"
    echo ""
    echo "Dashboard: http://$HEAD_NODE_IP:$DASHBOARD_PORT"
    echo ""
}

# Stop the cluster
stop_cluster() {
    echo "=== Stopping Ray RLlib Cluster ==="
    echo ""
    
    # Stop workers first
    echo "Stopping worker nodes..."
    for node in "${WORKER_NODES[@]}"; do
        echo -n "  Stopping $node... "
        if ssh "dhart@$node" "source $VENV_DIR/bin/activate && ray stop" &>/dev/null; then
            print_success "stopped"
        else
            print_warning "no Ray process found or already stopped"
        fi
    done
    
    # Stop head node
    echo ""
    echo "Stopping head node on $HEAD_NODE..."
    if [ -d "$VENV_DIR" ]; then
        source "$VENV_DIR/bin/activate"
        ray stop
        print_success "Head node stopped"
    else
        print_warning "Virtual environment not found"
    fi
    
    echo ""
    print_success "Cluster shutdown complete."
    echo ""
}

# Check cluster status
check_status() {
    echo "=== Ray RLlib Cluster Status ==="
    echo ""
    
    check_venv
    source "$VENV_DIR/bin/activate"
    
    if ray status &>/dev/null; then
        ray status
    else
        print_warning "Ray cluster is not running"
        echo ""
        echo "To start the cluster, run:"
        echo "  $0 start"
    fi
}

# Restart the cluster
restart_cluster() {
    stop_cluster
    sleep 3
    start_cluster
}

# Show usage
usage() {
    cat <<EOF
Usage: $0 {start|stop|status|restart}

Commands:
  start     - Start Ray cluster (head node + all workers)
  stop      - Stop Ray cluster across all nodes
  status    - Show current cluster status
  restart   - Restart the entire cluster

Examples:
  $0 start        # Start the cluster
  $0 status       # Check if cluster is running
  $0 stop         # Stop the cluster
  $0 restart      # Restart everything

Dashboard: http://$HEAD_NODE_IP:$DASHBOARD_PORT

Worker Nodes: ${WORKER_NODES[@]}
EOF
}

# Main script
case "$1" in
    start)
        start_cluster
        ;;
    stop)
        stop_cluster
        ;;
    status)
        check_status
        ;;
    restart)
        restart_cluster
        ;;
    *)
        usage
        exit 1
        ;;
esac
