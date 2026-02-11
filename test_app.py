#!/usr/bin/env python3
"""
Simple test for the Taiwan Earthquake Data Fetcher app
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


def test_client_connection():
    """Test IRIS FDSN client connection"""
    print("\nTesting IRIS FDSN client connection...")
    
    try:
        from obspy.clients.fdsn import Client
        client = Client("IRIS")
        print("✓ IRIS FDSN client created successfully")
        return True
    except Exception as e:
        print(f"✗ Client connection failed: {e}")
        return False


def test_earthquake_search():
    """Test earthquake search functionality"""
    print("\nTesting earthquake search (with small query)...")
    
    try:
        from obspy import UTCDateTime
        from obspy.clients.fdsn import Client
        from datetime import datetime, timedelta
        
        client = Client("IRIS")
        
        # Small test query - last 7 days, magnitude 5+, Taiwan region
        end_time = datetime.now()
        start_time = end_time - timedelta(days=7)
        
        catalog = client.get_events(
            starttime=UTCDateTime(start_time.strftime("%Y-%m-%d")),
            endtime=UTCDateTime(end_time.strftime("%Y-%m-%d")),
            minmagnitude=5.0,
            minlatitude=21.0,
            maxlatitude=26.0,
            minlongitude=119.0,
            maxlongitude=123.0
        )
        
        print(f"✓ Search completed: Found {len(catalog)} earthquake(s)")
        
        if len(catalog) > 0:
            event = catalog[0]
            origin = event.preferred_origin() or event.origins[0]
            magnitude = event.preferred_magnitude() or event.magnitudes[0]
            print(f"  Example: M{magnitude.mag:.1f} at {origin.time}")
        
        return True
        
    except Exception as e:
        print(f"✗ Search failed: {e}")
        # This might fail if there are no earthquakes, which is OK
        if "No data" in str(e) or "404" in str(e):
            print("  (No earthquakes found in query range - this is OK)")
            return True
        return False


def test_app_creation():
    """Test that the Gradio app can be created"""
    print("\nTesting Gradio app creation...")
    
    try:
        from app import create_interface
        demo = create_interface()
        print("✓ Gradio interface created successfully")
        return True
    except Exception as e:
        print(f"✗ App creation failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Taiwan Earthquake Data Fetcher - Basic Tests")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_client_connection,
        test_earthquake_search,
        test_app_creation,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if all(results):
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
