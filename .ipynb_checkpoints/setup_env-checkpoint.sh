#!/bin/bash
# setup_env.sh
# Builds the "rms-tmb-capstone" conda environment on OSC for the
# rhabdomyosarcoma TMB / overall-survival capstone project.
#
# Usage (from your Capstone folder on OSC):
#   bash setup_env.sh
#
# After it finishes, activate with:
#   module load miniconda3
#   source activate rms-tmb-capstone

set -e  # stop the script if any command fails

ENV_NAME="rms-tmb-capstone"
ENV_YML="environment.yml"

echo "=== Step 1: Loading the miniconda3 module ==="
module load miniconda3/24.1.2-py310

echo "=== Step 2: Checking for environment.yml ==="
if [ ! -f "$ENV_YML" ]; then
    echo "ERROR: $ENV_YML not found in the current directory."
    echo "Make sure setup_env.sh and environment.yml are both in your Capstone folder,"
    echo "and that you're running this script from that folder."
    exit 1
fi

echo "=== Step 3: Creating (or updating) the conda environment: $ENV_NAME ==="
if conda env list | grep -q "^${ENV_NAME} "; then
    echo "Environment '$ENV_NAME' already exists. Updating it instead of recreating."
    conda env update -n "$ENV_NAME" -f "$ENV_YML" --prune
else
    conda env create -f "$ENV_YML"
fi

echo "=== Step 4: Activating the environment ==="
source activate "$ENV_NAME"

echo "=== Step 5: Registering a Jupyter kernel for OSC OnDemand ==="
python -m ipykernel install --user --name "$ENV_NAME" --display-name "Python (rms-tmb-capstone)"

echo "=== Setup complete ==="
echo "Environment '$ENV_NAME' is ready."
echo "In an OSC OnDemand Jupyter session, choose the 'Python (rms-tmb-capstone)' kernel."
