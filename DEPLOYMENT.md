# Hugging Face Spaces Deployment Guide

This guide explains how to deploy the EEW Quality Control application to Hugging Face Spaces.

## Prerequisites

- Python 3.7 or higher
- Hugging Face account (username: `cwbdayi`)
- Hugging Face token: `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`

## Deployment Methods

### Method 1: Automated Deployment (Recommended)

Run the deployment script:

```bash
./deploy.sh
```

This script will:
1. Install `huggingface_hub` if needed
2. Authenticate with your Hugging Face account
3. Create the Space repository (if it doesn't exist)
4. Upload all necessary files to the Space

### Method 2: Manual Deployment via Web Interface

1. **Create a new Space on Hugging Face:**
   - Go to https://huggingface.co/new-space
   - Space name: `EEW_quality_control`
   - Owner: `cwbdayi`
   - License: MIT
   - SDK: Gradio
   - Click "Create Space"

2. **Upload files:**
   - Upload the following files to your Space:
     - `app.py` (main application file)
     - `requirements.txt` (dependencies)
     - `README.md` (with metadata header)
     - All Python scripts (`*.py`)
     - `eewrep_function.py`

3. **Wait for build:**
   - The Space will automatically build and deploy
   - This may take a few minutes

### Method 3: Manual Deployment via Git

1. **Install Hugging Face CLI:**
   ```bash
   pip install huggingface_hub
   ```

2. **Login to Hugging Face:**
   ```bash
   huggingface-cli login
   ```
   Enter the token: `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`

3. **Clone your Space repository:**
   ```bash
   git clone https://huggingface.co/spaces/cwbdayi/EEW_quality_control
   cd EEW_quality_control
   ```

4. **Copy files from this repository:**
   ```bash
   cp /path/to/EEW_quality_control/*.py .
   cp /path/to/EEW_quality_control/requirements.txt .
   cp /path/to/EEW_quality_control/README.md .
   ```

5. **Commit and push:**
   ```bash
   git add .
   git commit -m "Deploy EEW Quality Control application"
   git push
   ```

### Method 4: Python Script

Run this Python script:

```python
from huggingface_hub import HfApi, login, create_repo, upload_folder

# Authenticate
token = "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"
login(token=token)

# Create Space
repo_id = "cwbdayi/EEW_quality_control"
create_repo(
    repo_id=repo_id,
    token=token,
    repo_type="space",
    space_sdk="gradio",
    exist_ok=True
)

# Upload files
api = HfApi()
api.upload_folder(
    folder_path=".",
    repo_id=repo_id,
    repo_type="space",
    token=token,
    ignore_patterns=[".git/*", "old/*", "*.rep", "*.P20", "192/*", "outputs/*"]
)

print(f"✓ Deployed to: https://huggingface.co/spaces/{repo_id}")
```

## Verifying Deployment

Once deployed, your application will be available at:
**https://huggingface.co/spaces/cwbdayi/EEW_quality_control**

The Space will:
- Automatically install dependencies from `requirements.txt`
- Start the Gradio application from `app.py`
- Be accessible via a web browser

## Updating the Space

To update the Space after deployment:

1. Make changes to your code
2. Commit changes: `git commit -am "Update message"`
3. Push to Hugging Face: `git push`

Or use the automated script again:
```bash
./deploy.sh
```

## Troubleshooting

### Build Failures

If the build fails:
1. Check the build logs in the Space's "Logs" tab
2. Verify that all dependencies in `requirements.txt` are correct
3. Check that `app.py` has no syntax errors

### Space Not Loading

If the Space doesn't load:
1. Check that `app.py` ends with `demo.launch()`
2. Verify that all imports are working
3. Check the runtime logs for errors

### Permission Issues

If you get permission errors:
1. Verify your token is correct
2. Check that you're logged in to the correct account
3. Ensure the Space name is available

## Additional Resources

- [Hugging Face Spaces Documentation](https://huggingface.co/docs/hub/spaces)
- [Gradio Documentation](https://gradio.app/docs)
- [EEW Quality Control Repository](https://github.com/oceanicdayi/EEW_quality_control)

## Support

For issues or questions:
- GitHub: https://github.com/oceanicdayi/EEW_quality_control
- Hugging Face Space: https://huggingface.co/spaces/cwbdayi/EEW_quality_control
