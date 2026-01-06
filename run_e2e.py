import subprocess
import time
import sys
import os

def run_tests():
    # 1. Start Streamlit
    print("Starting Streamlit on port 8503...")
    env = os.environ.copy()
    env["STREAMLIT_SERVER_PORT"] = "8503"
    env["STREAMLIT_SERVER_HEADLESS"] = "true"
    
    # Using sys.executable to ensure same python env
    server = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Wait for server to start
        print("Waiting 10s for server startup...")
        time.sleep(10)
        
        # Check if process is still running
        if server.poll() is not None:
            out, err = server.communicate()
            print("Server failed to start!")
            print(out)
            print(err)
            sys.exit(1)
            
        print("Server assumed running. Starting Tests...")
        
        # 2. Run Pytest
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/test_e2e.py"],
            capture_output=False # Stream output to console
        )
        
        if result.returncode == 0:
            print("✅ Tests Passed!")
        else:
            print("❌ Tests Failed!")
            
    finally:
        # 3. Cleanup
        print("Stopping Server...")
        server.terminate()
        server.wait()

if __name__ == "__main__":
    run_tests()
