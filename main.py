import os
import sys
import subprocess

# Set the project directory
PROJECT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chicken_shooting_game")

def main():
    # Change current working directory to the game folder
    os.chdir(PROJECT_DIR)
    
    # Run the actual main.py
    # We use subprocess to ensure it runs in its own environment context if needed
    # Or we can just import it. Import is cleaner if path is set.
    sys.path.insert(0, PROJECT_DIR)
    
    try:
        import main
        main.main()
    except ImportError as e:
        print(f"Error: Could not import game components. {e}")
        print("Make sure you are running from the correct directory and dependencies are installed.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
