#!/bin/bash
# Deployment script for Hugging Face Spaces

echo "====================================="
echo "EEW Quality Control - HF Spaces Deploy"
echo "====================================="
echo ""

# Configuration
HF_USERNAME="cwbdayi"
HF_SPACE_NAME="EEW_quality_control"
HF_TOKEN="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"

echo "Target: https://huggingface.co/spaces/${HF_USERNAME}/${HF_SPACE_NAME}"
echo ""

# Check if huggingface_hub is installed
if ! python3 -c "import huggingface_hub" 2>/dev/null; then
    echo "Installing huggingface_hub..."
    pip install huggingface_hub
fi

# Deploy using Python
python3 << EOF
from huggingface_hub import HfApi, login, create_repo, upload_folder
import os

print("Step 1: Authenticating with Hugging Face...")
try:
    login(token="${HF_TOKEN}", add_to_git_credential=True)
    print("✓ Authentication successful")
except Exception as e:
    print(f"✗ Authentication failed: {e}")
    exit(1)

print("\nStep 2: Creating Space repository...")
repo_id = "${HF_USERNAME}/${HF_SPACE_NAME}"
try:
    url = create_repo(
        repo_id=repo_id,
        token="${HF_TOKEN}",
        repo_type="space",
        space_sdk="gradio",
        exist_ok=True
    )
    print(f"✓ Space created/exists: {url}")
except Exception as e:
    print(f"Note: {e}")

print("\nStep 3: Uploading files to Space...")
try:
    api = HfApi()
    api.upload_folder(
        folder_path=".",
        repo_id=repo_id,
        repo_type="space",
        token="${HF_TOKEN}",
        ignore_patterns=[
            ".git/*",
            ".gitignore",
            "old/*",
            "*.rep",
            "*.P20",
            "192/*",
            "outputs/*",
            "*.log",
            "__pycache__/*",
            "*.pyc",
            ".DS_Store",
            "deploy.sh"
        ]
    )
    print("✓ Files uploaded successfully")
except Exception as e:
    print(f"✗ Upload failed: {e}")
    exit(1)

print("\n" + "="*50)
print("✓ Deployment complete!")
print(f"🌐 Visit: https://huggingface.co/spaces/{repo_id}")
print("="*50)
EOF

echo ""
echo "Deployment script completed!"
