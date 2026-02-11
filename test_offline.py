#!/usr/bin/env python3
"""
Offline tests for the Taiwan Earthquake Data Fetcher app
These tests don't require network connectivity
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        from obspy import UTCDateTime
        from obspy.clients.fdsn import Client
        import gradio as gr
        import matplotlib.pyplot as plt
        import numpy as np
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_app_module_import():
    """Test that the app module can be imported"""
    print("\nTesting app module import...")
    
    try:
        import app
        print("✓ App module imported successfully")
        return True
    except Exception as e:
        print(f"✗ App import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_helper_functions():
    """Test helper functions that don't require network"""
    print("\nTesting helper functions...")
    
    try:
        from app import plot_waveforms, create_earthquake_map
        from obspy import UTCDateTime, Trace, Stream
        import numpy as np
        
        # Create a simple synthetic trace
        data = np.random.randn(1000)
        tr = Trace(data=data)
        tr.stats.starttime = UTCDateTime("2024-01-01T00:00:00")
        tr.stats.sampling_rate = 100.0
        tr.stats.network = "TW"
        tr.stats.station = "TEST"
        tr.stats.channel = "BHZ"
        
        stream = Stream(traces=[tr])
        
        # Test plot_waveforms
        fig = plot_waveforms(stream, UTCDateTime("2024-01-01T00:00:10"), 23.5, 121.0)
        print("✓ plot_waveforms() works")
        
        # Close the figure
        import matplotlib.pyplot as plt
        plt.close(fig)
        
        return True
        
    except Exception as e:
        print(f"✗ Helper function test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gradio_interface():
    """Test that Gradio interface can be created (without launching)"""
    print("\nTesting Gradio interface creation...")
    
    try:
        from app import create_interface
        demo = create_interface()
        print("✓ Gradio interface created successfully")
        
        # Try to get the config
        if hasattr(demo, 'config'):
            print(f"  Interface has {len(demo.config.get('components', []))} components")
        
        return True
    except Exception as e:
        print(f"✗ Interface creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all offline tests"""
    print("=" * 60)
    print("Taiwan Earthquake Data Fetcher - Offline Tests")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_app_module_import,
        test_helper_functions,
        test_gradio_interface,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if all(results):
        print("\n✓ All offline tests passed!")
        print("\nNote: Online tests (IRIS FDSN connection) require network access")
        print("and may fail if the service is unavailable or blocked.")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
