import os
import subprocess
import sys

# This script simplifies the startup process for the VeridiChain application.
# It automatically finds and uses the Python executable from the virtual environment.

# Get the directory where this script is located.
project_dir = os.path.dirname(os.path.abspath(__file__))

# Determine the correct path to the Python executable within the venv.
# This handles both Windows and Linux/macOS path styles.
if sys.platform == "win32":
    venv_python = os.path.join(project_dir, 'venv', 'Scripts', 'python.exe')
else:
    venv_python = os.path.join(project_dir, 'venv', 'bin', 'python')

# The path to the main application script.
app_script = os.path.join(project_dir, 'app.py')

# Check if the venv Python executable actually exists.
if not os.path.exists(venv_python):
    print(f"ERROR: Could not find Python executable in venv at: {venv_python}")
    print("Please make sure you have created the virtual environment by running: python -m venv venv")
    sys.exit(1)

print(f"Found venv Python at: {venv_python}")
print("Starting VeridiChain application...")
print("-" * 30)

try:
    # Use subprocess to run 'app.py' using the venv's Python interpreter.
    # This is the correct way to run a script in a venv from another script.
    subprocess.call([venv_python, app_script])
except KeyboardInterrupt:
    print("\nApplication stopped by user.")
except Exception as e:
    print(f"\nAn error occurred: {e}")
