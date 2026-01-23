#!/bin/bash
# Ray RLlib Installation Script - Virtual Environment Based
# Creates a dedicated venv on each machine

set -e

echo "==================================="
echo "Ray RLlib Cluster Installation"
echo "==================================="
echo ""

HOSTNAME=$(hostname)
echo "Installing on: $HOSTNAME"

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Step 1: Initialize pyenv environment
echo "Step 1: Setting up pyenv environment..."
if [ -f "$HOME/.bashrc" ]; then
    source "$HOME/.bashrc"
fi

if [ -d "$HOME/.pyenv" ]; then
    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"
    if command -v pyenv 1>/dev/null 2>&1; then
        eval "$(pyenv init -)"
    fi
    print_success "pyenv initialized"
fi

# Step 2: Check CUDA
echo ""
echo "Step 2: Checking CUDA installation..."
if command -v nvidia-smi &> /dev/null; then
    CUDA_VERSION=$(nvidia-smi | grep "CUDA Version" | awk '{print $9}')
    print_success "CUDA Version: $CUDA_VERSION"
else
    print_error "nvidia-smi not found"
    exit 1
fi

# Step 3: Check Python 3.11 is available
echo ""
echo "Step 3: Checking Python 3.11..."
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
    print_success "Found python3.11"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1)
    if [[ "$PYTHON_VERSION" == *"3.11"* ]]; then
        PYTHON_CMD="python"
        print_success "Found python 3.11"
    else
        print_error "Python 3.11 not found. Found: $PYTHON_VERSION"
        exit 1
    fi
else
    print_error "Python not found"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
print_success "Python: $PYTHON_VERSION"

# Step 4: Create virtual environment
VENV_DIR="$HOME/venvs/rllib"
echo ""
echo "Step 4: Creating virtual environment at $VENV_DIR..."

if [ -d "$VENV_DIR" ]; then
    print_warning "Virtual environment already exists, removing..."
    rm -rf "$VENV_DIR"
fi

$PYTHON_CMD -m venv "$VENV_DIR"
print_success "Virtual environment created"

# Step 5: Activate virtual environment
echo ""
echo "Step 5: Activating virtual environment..."
source "$VENV_DIR/bin/activate"
print_success "Virtual environment activated"

# Verify we're in the venv
WHICH_PYTHON=$(which python)
if [[ "$WHICH_PYTHON" == *"$VENV_DIR"* ]]; then
    print_success "Using venv python: $WHICH_PYTHON"
else
    print_error "Not using venv python!"
    exit 1
fi

# Step 6: Upgrade pip in venv
echo ""
echo "Step 6: Upgrading pip..."
pip install --upgrade pip
print_success "pip upgraded"

# Step 7: Install PyTorch
echo ""
echo "Step 7: Installing PyTorch with CUDA support..."
if [[ "$CUDA_VERSION" == 12.* ]] || [[ "$CUDA_VERSION" == 13.* ]]; then
    print_warning "CUDA 12.x/13.x - installing PyTorch for CUDA 12.1"
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
elif [[ "$CUDA_VERSION" == 11.* ]]; then
    print_warning "CUDA 11.x - installing PyTorch for CUDA 11.8"
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
else
    print_error "Unsupported CUDA version: $CUDA_VERSION"
    exit 1
fi
print_success "PyTorch installed"

# Step 8: Install Ray with RLlib
echo ""
echo "Step 8: Installing Ray with RLlib..."
pip install -U "ray[rllib]" "ray[default]"
print_success "Ray RLlib installed"

# Step 9: Install additional dependencies
echo ""
echo "Step 9: Installing additional dependencies..."
pip install gymnasium tensorboard pandas matplotlib seaborn
print_success "Additional dependencies installed"

# Step 10: Verify installation
echo ""
echo "Step 10: Verifying installation..."

python -c "import torch; print(f'PyTorch {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA devices: {torch.cuda.device_count()}')" && print_success "PyTorch verified"

python -c "import ray; print(f'Ray {ray.__version__}')" && print_success "Ray verified"

python -c "from ray.rllib.algorithms.ppo import PPOConfig; print('RLlib OK')" && print_success "RLlib verified"

python -c "import gymnasium as gym; print(f'Gymnasium {gym.__version__}')" && print_success "Gymnasium verified"

# Step 11: Create activation helper script
echo ""
echo "Step 11: Creating activation helper..."
cat > "$HOME/activate_rllib.sh" << 'EOF'
#!/bin/bash
# Activate Ray RLlib virtual environment
source "$HOME/venvs/rllib/bin/activate"
echo "Ray RLlib environment activated"
echo "Python: $(which python)"
echo "Ray version: $(python -c 'import ray; print(ray.__version__)' 2>/dev/null || echo 'Not installed')"
EOF
chmod +x "$HOME/activate_rllib.sh"
print_success "Created ~/activate_rllib.sh"

echo ""
print_success "Installation completed successfully on $HOSTNAME!"
echo ""
echo "==================================="
echo "To use Ray RLlib on this machine:"
echo "  source ~/venvs/rllib/bin/activate"
echo "  OR"
echo "  source ~/activate_rllib.sh"
echo "==================================="
