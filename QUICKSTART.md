# Quick Start: Deploy to Hugging Face Spaces

This repository is ready to be deployed to Hugging Face Spaces. Follow these simple steps:

## Option 1: One-Line Deployment (Recommended)

If you have Python and internet access, simply run:

```bash
pip install huggingface_hub && python3 deploy_hf.py
```

## Option 2: Use the Web Interface

1. Go to https://huggingface.co/new-space
2. Set:
   - Owner: `cwbdayi`
   - Space name: `EEW_quality_control`
   - SDK: Gradio
   - License: MIT
3. Click "Create Space"
4. Upload these files through the web interface:
   - `app.py`
   - `requirements.txt`
   - `README.md`
   - All `.py` files from the root directory

## Option 3: Use Git

```bash
# Login to Hugging Face (use token: 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)
pip install huggingface_hub
huggingface-cli login

# Clone the Space repository
git clone https://huggingface.co/spaces/cwbdayi/EEW_quality_control hf_space
cd hf_space

# Copy files (adjust paths as needed)
cp /path/to/this/repo/*.py .
cp /path/to/this/repo/requirements.txt .
cp /path/to/this/repo/README.md .

# Push to Hugging Face
git add .
git commit -m "Initial deployment"
git push
```

## What's Included

All necessary files for deployment are already prepared:

- ✅ `app.py` - Gradio web interface
- ✅ `requirements.txt` - All dependencies
- ✅ `README.md` - Documentation with HF metadata
- ✅ All Python scripts for EEW analysis

## After Deployment

Your Space will be available at:
**https://huggingface.co/spaces/cwbdayi/EEW_quality_control**

The Space will automatically:
1. Install dependencies from `requirements.txt`
2. Start the Gradio application
3. Be accessible via web browser

## Need Help?

See `DEPLOYMENT.md` for detailed instructions and troubleshooting.
