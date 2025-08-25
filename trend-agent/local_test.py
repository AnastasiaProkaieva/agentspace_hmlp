import cloudpickle
import subprocess
import sys
import os

# --- This script tests if your agent can be unpickled correctly ---
# --- It simulates the corrected remote environment. ---

AGENT_PICKLE_FILE = "agent_agent.pkl"  # The name of the pickle file to create
EXTRA_PACKAGES_DIR = "app"  # The directory that gets deployed

def create_pickle():
    """
    Creates the agent pickle file for testing.
    This part requires the local path fix to run successfully.
    """
    print("--- Step 1: Creating agent pickle file ---")
    try:
        # Temporarily add project root to path to allow local import
        # This mimics the fix in deploy_agentengine.py
        project_root = os.path.dirname(__file__)
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        from app.agent import root_agent

        with open(AGENT_PICKLE_FILE, "wb") as f:
            cloudpickle.dump(root_agent, f)

        print(f"✅ Successfully created '{AGENT_PICKLE_FILE}'")
        return True
    except Exception as e:
        print(f"❌ Failed to create pickle file: {e}")
        print(
            "   Check that your imports inside 'app/' are correct (no dots) and that the local path fix is in your deployment script."
        )
        return False
    finally:
        # Clean up path modification to avoid side-effects
        if "project_root" in locals() and project_root in sys.path:
            sys.path.remove(project_root)


def test_unpickling():
    """
    Tests unpickling in a clean subprocess that mimics the remote environment.
    """
    print("\n--- Step 2: Testing unpickling in a simulated clean environment ---")

    # This Python code will be run in a separate, clean process
    test_script = f"""
import cloudpickle
import sys
import os

# This is the crucial part: It simulates the 'extra_packages' mechanism
# by adding the 'app' directory to the path before doing anything else.
# We use an absolute path to be safe.
app_dir_path = os.path.abspath('{EXTRA_PACKAGES_DIR}')
sys.path.insert(0, app_dir_path)

print(f"   Simulated environment is ready. Python path includes: {{app_dir_path}}")
print("   Attempting to unpickle...")

try:
    with open('{AGENT_PICKLE_FILE}', 'rb') as f:
        agent = cloudpickle.load(f)
    print("✅ SUCCESS: Agent unpickled successfully!")
    print(f"   Agent Name: {{agent.name}}")
except ModuleNotFoundError as e:
    print(f"❌ FAILURE: {{e}}")
    print("   This means the remote environment cannot find a module.")
    print("   Ensure the 'extra_packages' in your deploy script is just ['app'].")
    sys.exit(1) # Exit with an error code to signal failure
except Exception as e:
    print(f"❌ FAILURE: An unexpected error occurred during unpickling: {{e}}")
    sys.exit(1) # Exit with an error code to signal failure
"""
    try:
        # The 'check=True' will raise a CalledProcessError if the subprocess exits with a non-zero code.
        # This is how we detect failure.
        subprocess.run([sys.executable, "-c", test_script], check=True, text=True)
        print("\n--- Test Result: SUCCESS ---")

    except subprocess.CalledProcessError:
        # This block will ONLY run if the subprocess failed (e.g., raised ModuleNotFoundError).
        # The detailed error from the subprocess will have already been printed to the console.
        print("\n--- Test Result: FAILED ---")

    finally:
        # This block ALWAYS runs, ensuring the test file is cleaned up.
        if os.path.exists(AGENT_PICKLE_FILE):
            os.remove(AGENT_PICKLE_FILE)
            print(f"   Cleaned up {AGENT_PICKLE_FILE}")


if __name__ == "__main__":
    if create_pickle():
        test_unpickling()
