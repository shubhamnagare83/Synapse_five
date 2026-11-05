import sys
import os
import json
import warnings
from pathlib import Path

# Suppress library warnings for clean terminal presentation
warnings.filterwarnings("ignore")
os.environ["PYTHONWARNINGS"] = "ignore"

# Ensure package root is in sys.path so ask.py can be run from any folder
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from helpdesk.pipeline import ask

def main():
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        try:
            print("\nRailway Help Desk (Synapse Five)")
            print("================================")
            question = input("Enter your railway inquiry: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            sys.exit(0)

    if not question:
        print(json.dumps({"error": "Please provide a question string."}))
        sys.exit(1)

    result = ask(question)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()


