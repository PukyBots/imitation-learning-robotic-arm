#!/bin/bash

echo "🚀 Starting ArmFlow Setup..."

# 1. Clone the repository into a new folder
echo "📦 Downloading files from GitHub..."
git clone https://github.com/SadathAliRahman/imitation-learning-robotic-arm.git armflow_workspace

# Navigate into the specific Python application directory
# Using quotes to handle the space in "Imitation Learner"
cd "armflow_workspace/Imitation Learner/ArmFlow" || { echo "❌ Failed to find the target directory. Exiting."; exit 1; }

# 2. Set up a Python Virtual Environment
echo "🐍 Setting up isolated Python environment..."
python3 -m venv venv
source venv/bin/activate

# 3. Install the required libraries
echo "📥 Installing dependencies..."
python3 -m pip install --upgrade pip
pip install -r requirements.txt

# 4. Run the Master Hub
echo "▶️ Launching ArmFlow Hub..."
python app.py
