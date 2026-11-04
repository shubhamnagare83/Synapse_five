import sys
import json
from helpdesk.pipeline import ask

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Please provide a question string."}))
        sys.exit(1)

    question = sys.argv[1]
    result = ask(question)
    print(json.dumps(result, indent=2))