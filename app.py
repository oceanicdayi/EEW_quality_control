#!/usr/bin/env python3
"""
Earthquake Early Warning (EEW) Quality Control Web Interface
A Gradio-based web application for analyzing and visualizing EEW data
"""

import gradio as gr
import os
import sys
import subprocess
from pathlib import Path
import tempfile
import shutil

# Ensure the current directory is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def create_interface():
    """Create the Gradio interface for EEW Quality Control"""
    
    with gr.Blocks(title="EEW Quality Control") as demo:
        gr.Markdown(
            """
            # Earthquake Early Warning (EEW) Quality Control
            
            This application provides tools for analyzing and visualizing Earthquake Early Warning (EEW) data.
            
            ## Features:
            - **Report Processing**: Convert EEW reports to text format
            - **Data Visualization**: Plot EEW report summaries and maps
            - **Quality Analysis**: Analyze reporting times and trigger maps
            - **County Analysis**: Analyze EEW data by county
            
            ## Available Scripts:
            """
        )
        
        with gr.Tab("📊 About"):
            gr.Markdown(
                """
                ### EEW Quality Control Tools
                
                This repository contains Python scripts for analyzing Earthquake Early Warning (EEW) system data:
                
                1. **01_rep2txt_pfile.py**: Convert report files to text format using P-file input
                2. **02_plot_report_pfile.py**: Plot EEW report summaries from P-file data
                3. **03_plot_ez_maps.py**: Plot EZ (epicenter zone) maps
                4. **04_plot_tsmip_trigger_map.py**: Plot TSMIP trigger maps
                5. **05_plot_conunty.py**: Analyze data by county
                6. **06_plot_reporting_time_pfile.py**: Plot reporting time analysis
                
                ### Data Requirements
                
                The scripts expect the following data files:
                - P-files in the `192/` directory (with .P20 extension)
                - Station data (`station.txt`)
                - County list (`county_list.txt`)
                - City boundary data (`city_2016.gmt`)
                - EEW report files (`.rep` files)
                - XML files with earthquake data
                
                ### Usage
                
                To use these tools, you need to:
                1. Prepare your data files in the required format
                2. Place P-files in the `192/` directory
                3. Run the appropriate script with the necessary arguments
                
                ### Command-line Usage Examples
                
                ```bash
                # Convert report files to text
                python 01_rep2txt_pfile.py
                
                # Plot report summary
                python 02_plot_report_pfile.py <pfile> --kind all
                
                # Plot EZ maps
                python 03_plot_ez_maps.py <pfile> --epi-lon 120.5 --epi-lat 23.5
                
                # Plot trigger map
                python 04_plot_tsmip_trigger_map.py <pfile>
                
                # Plot county analysis
                python 05_plot_conunty.py <pfile>
                
                # Plot reporting time
                python 06_plot_reporting_time_pfile.py <pfile>
                ```
                
                ### Dependencies
                
                - Python 3.7+
                - pandas
                - numpy
                - matplotlib
                - obspy
                - pygmt
                
                ### Repository
                
                Source code: [github.com/oceanicdayi/EEW_quality_control](https://github.com/oceanicdayi/EEW_quality_control)
                """
            )
        
        with gr.Tab("🧪 Test Environment"):
            gr.Markdown(
                """
                ### Environment Check
                
                Click the button below to verify that all required dependencies are installed and accessible.
                """
            )
            
            test_output = gr.Textbox(
                label="Test Results",
                lines=10,
                max_lines=20,
                interactive=False
            )
            
            def run_environment_test():
                """Run basic environment checks"""
                output = []
                output.append("=== EEW Quality Control Environment Test ===\n")
                
                # Check Python version
                import sys
                output.append(f"Python version: {sys.version}\n")
                
                # Check dependencies
                deps = {
                    "pandas": "pandas",
                    "numpy": "numpy", 
                    "matplotlib": "matplotlib",
                    "obspy": "obspy",
                    "pygmt": "pygmt",
                    "gradio": "gradio"
                }
                
                output.append("\n=== Checking Dependencies ===")
                for name, module in deps.items():
                    try:
                        mod = __import__(module)
                        version = getattr(mod, '__version__', 'unknown')
                        output.append(f"✓ {name}: {version}")
                    except ImportError as e:
                        output.append(f"✗ {name}: NOT FOUND - {e}")
                
                # Check for data files
                output.append("\n=== Checking Data Files ===")
                required_files = [
                    "eewrep_function.py",
                    "01_rep2txt_pfile.py",
                    "02_plot_report_pfile.py",
                    "03_plot_ez_maps.py",
                    "04_plot_tsmip_trigger_map.py",
                    "05_plot_conunty.py",
                    "06_plot_reporting_time_pfile.py"
                ]
                
                for filepath in required_files:
                    if os.path.exists(filepath):
                        output.append(f"✓ {filepath}")
                    else:
                        output.append(f"✗ {filepath} - NOT FOUND")
                
                # Check directories
                output.append("\n=== Checking Directories ===")
                dirs = ["192", "outputs", "old"]
                for dirname in dirs:
                    if os.path.exists(dirname):
                        output.append(f"✓ {dirname}/ - EXISTS")
                    else:
                        output.append(f"✗ {dirname}/ - NOT FOUND")
                
                output.append("\n=== Test Complete ===")
                output.append("\nNote: This is a deployment of the EEW Quality Control tools.")
                output.append("To fully use the application, you need to provide the required data files.")
                
                return "\n".join(output)
            
            test_button = gr.Button("Run Environment Test", variant="primary")
            test_button.click(fn=run_environment_test, outputs=test_output)
        
        with gr.Tab("📖 Documentation"):
            gr.Markdown(
                """
                ### Script Documentation
                
                #### 01_rep2txt_pfile.py
                Converts EEW report files to text format using P-file input.
                
                **Usage:**
                ```bash
                python 01_rep2txt_pfile.py
                ```
                
                ---
                
                #### 02_plot_report_pfile.py
                Plots EEW report summary from P-file data.
                
                **Arguments:**
                - `pfile`: P-file name (e.g., 17010623.P20)
                - `--kind`: Analysis type (f42/f43/gei/all, default: all)
                - `--base-folder`: Directory containing .rep files (default: ./192)
                - `--xmin`, `--xmax`: X-axis range in seconds
                - `--ymin`, `--ymax`: Y-axis range
                
                **Usage:**
                ```bash
                python 02_plot_report_pfile.py 17010623.P20 --kind all
                ```
                
                ---
                
                #### 03_plot_ez_maps.py
                Plots EZ (epicenter zone) maps.
                
                **Arguments:**
                - `pfile`: P-file name
                - `--epi-lon`: Epicenter longitude (required)
                - `--epi-lat`: Epicenter latitude (required)
                - `--kind`: Analysis type (f42/f43/gei/all, default: all)
                - `--base-folder`: Directory containing .rep files (default: ./192)
                
                **Usage:**
                ```bash
                python 03_plot_ez_maps.py 17010623.P20 --epi-lon 120.5 --epi-lat 23.5
                ```
                
                ---
                
                #### 04_plot_tsmip_trigger_map.py
                Plots TSMIP trigger maps.
                
                **Arguments:**
                - `pfile`: P-file name
                - `--kind`: Analysis type (f42/f43/gei/all, default: all)
                - `--base-folder`: Directory containing .rep files (default: ./192)
                
                **Usage:**
                ```bash
                python 04_plot_tsmip_trigger_map.py 17010623.P20
                ```
                
                ---
                
                #### 05_plot_conunty.py
                Analyzes EEW data by county.
                
                **Arguments:**
                - `pfile`: P-file name
                - `--kind`: Analysis type (f42/f43/gei/all, default: all)
                - `--base-folder`: Directory containing .rep files (default: ./192)
                
                **Usage:**
                ```bash
                python 05_plot_conunty.py 17010623.P20
                ```
                
                ---
                
                #### 06_plot_reporting_time_pfile.py
                Plots reporting time analysis from P-file data.
                
                **Arguments:**
                - `pfile`: P-file name
                - `--kind`: Analysis type (f42/f43/gei/all, default: all)
                - `--base-folder`: Directory containing .rep files (default: ./192)
                - `--xmin`, `--xmax`: X-axis range in seconds
                
                **Usage:**
                ```bash
                python 06_plot_reporting_time_pfile.py 17010623.P20
                ```
                
                ---
                
                ### Data File Formats
                
                #### P-file Format
                P-files contain earthquake parameters and station data:
                - Line 1: Event information (time, magnitude, depth)
                - Lines 2+: Station information (name, arrival time, intensity, PGA)
                
                #### Report Files (.rep)
                Report files contain EEW system reports with timing and location information.
                
                #### XML Files
                XML files contain official earthquake information from CWA (Central Weather Administration).
                
                ### Contact
                
                For questions or issues, please visit the GitHub repository:
                [github.com/oceanicdayi/EEW_quality_control](https://github.com/oceanicdayi/EEW_quality_control)
                """
            )
        
        gr.Markdown(
            """
            ---
            
            ### Note
            
            This is a web interface for the EEW Quality Control tools. The original scripts are designed 
            to be run from the command line with specific data files. This interface provides documentation 
            and environment testing capabilities.
            
            To use the full functionality of these tools, clone the repository and run the scripts locally 
            with your EEW data files.
            
            **Repository:** [github.com/oceanicdayi/EEW_quality_control](https://github.com/oceanicdayi/EEW_quality_control)
            """
        )
    
    return demo


if __name__ == "__main__":
    demo = create_interface()
    demo.launch()
