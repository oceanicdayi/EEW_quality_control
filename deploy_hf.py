#!/usr/bin/env python3
"""
Simple deployment script for Hugging Face Spaces
Run this script from a machine with internet access to deploy the Space
"""

from huggingface_hub import HfApi, login, create_repo, upload_folder
import os
import sys

# Configuration
HF_USERNAME = "cwbdayi"
HF_SPACE_NAME = "EEW_quality_control"
HF_TOKEN = "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"

def main():
    print("=" * 60)
    print("EEW Quality Control - Hugging Face Spaces Deployment")
    print("=" * 60)
    print()
    
    repo_id = f"{HF_USERNAME}/{HF_SPACE_NAME}"
    print(f"Target: https://huggingface.co/spaces/{repo_id}")
    print()
    
    # Step 1: Authentication
    print("Step 1: Authenticating with Hugging Face...")
    try:
        login(token=HF_TOKEN, add_to_git_credential=True)
        print("✓ Authentication successful")
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        return 1
    
    # Step 2: Create Space
    print("\nStep 2: Creating Space repository...")
    try:
        api = HfApi()
        url = api.create_repo(
            repo_id=repo_id,
            token=HF_TOKEN,
            repo_type="space",
            space_sdk="gradio",
            exist_ok=True
        )
        print(f"✓ Space created/exists: {url}")
    except Exception as e:
        print(f"Note: {e}")
        print("Space may already exist, continuing...")
    
    # Step 3: Upload files
    print("\nStep 3: Uploading files to Space...")
    try:
        api = HfApi()
        api.upload_folder(
            folder_path=".",
            repo_id=repo_id,
            repo_type="space",
            token=HF_TOKEN,
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
                "deploy.sh",
                "deploy_hf.py",
                "DEPLOYMENT.md",
                "/tmp/*"
            ]
        )
        print("✓ Files uploaded successfully")
    except Exception as e:
        print(f"✗ Upload failed: {e}")
        return 1
    
    # Success
    print()
    print("=" * 60)
    print("✓ Deployment complete!")
    print(f"🌐 Visit: https://huggingface.co/spaces/{repo_id}")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nDeployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        sys.exit(1)
