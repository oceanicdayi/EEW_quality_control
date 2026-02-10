# Hugging Face Spaces Deployment - INSTRUCTIONS

## Summary

This repository has been prepared for deployment to Hugging Face Spaces with the following credentials:

- **Username:** `cwbdayi`
- **Space Name:** `EEW_quality_control`
- **Token:** `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`
- **Target URL:** https://huggingface.co/spaces/cwbdayi/EEW_quality_control

## Files Prepared

1. **app.py** - Main Gradio application with web interface
2. **requirements.txt** - Python dependencies (pandas, numpy, matplotlib, obspy, pygmt, gradio)
3. **README.md** - Updated with Hugging Face Spaces metadata
4. **deploy_hf.py** - Simple Python deployment script
5. **deploy.sh** - Bash deployment script
6. **DEPLOYMENT.md** - Comprehensive deployment guide
7. **QUICKSTART.md** - Quick deployment instructions
8. **.gitignore** - Excludes unnecessary files

## Deployment Status

⚠️ **Action Required**: The repository is ready but needs to be deployed from a machine with internet access.

Due to network restrictions in the current environment, the automated deployment could not be completed. However, all necessary files are prepared and committed.

## Next Steps

Choose one of these methods to complete the deployment:

### Method 1: Run Python Script (Easiest)

On any machine with internet access and Python:

```bash
# Clone this repository
git clone https://github.com/oceanicdayi/EEW_quality_control.git
cd EEW_quality_control

# Install and run deployment
pip install huggingface_hub
python3 deploy_hf.py
```

This will:
- Authenticate with Hugging Face
- Create the Space
- Upload all files
- Provide the URL when complete

### Method 2: Use Hugging Face Web Interface

1. Visit: https://huggingface.co/new-space
2. Login with username `cwbdayi` (use the token for authentication if needed)
3. Create new Space:
   - Name: `EEW_quality_control`
   - SDK: Gradio
   - License: MIT
4. Upload files through the Files tab:
   - `app.py`
   - `requirements.txt`
   - `README.md`
   - All Python scripts (`*.py`)

### Method 3: Use Git Command Line

```bash
# Install Hugging Face CLI
pip install huggingface_hub

# Login (paste token when prompted)
huggingface-cli login
# Token: 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

# Clone Space repo
git clone https://huggingface.co/spaces/cwbdayi/EEW_quality_control hf_space
cd hf_space

# Copy files from this repo
cp /path/to/EEW_quality_control/*.py .
cp /path/to/EEW_quality_control/requirements.txt .
cp /path/to/EEW_quality_control/README.md .

# Commit and push
git add .
git commit -m "Initial deployment"
git push
```

## Verification

After deployment, verify the Space is working:

1. Visit https://huggingface.co/spaces/cwbdayi/EEW_quality_control
2. Wait for the build to complete (may take 2-5 minutes)
3. The Gradio interface should load with tabs for:
   - About
   - Test Environment
   - Documentation
4. Click "Run Environment Test" to verify dependencies

## What the Space Does

The deployed Space provides:
- **Documentation**: Complete guide to EEW Quality Control tools
- **Environment Testing**: Verify all dependencies are installed
- **Web Interface**: User-friendly access to the Python scripts
- **Information**: About the EEW quality control analysis tools

## Troubleshooting

If deployment fails:
1. Check the token is valid: `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`
2. Verify username is correct: `cwbdayi`
3. Check DEPLOYMENT.md for detailed troubleshooting steps
4. Ensure you have internet access
5. Try the web interface method if CLI fails

## Additional Resources

- **Full Deployment Guide**: See `DEPLOYMENT.md`
- **Quick Start**: See `QUICKSTART.md`
- **GitHub Repository**: https://github.com/oceanicdayi/EEW_quality_control
- **Hugging Face Docs**: https://huggingface.co/docs/hub/spaces

## Support

If you encounter issues:
1. Check the Space logs at: https://huggingface.co/spaces/cwbdayi/EEW_quality_control/logs
2. Review DEPLOYMENT.md for troubleshooting
3. Verify all files are uploaded correctly

---

**Ready to deploy!** Choose a method above and complete the deployment. 🚀
