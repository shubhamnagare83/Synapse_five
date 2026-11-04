import sys
from helpdesk.pipeline import ask

if __name__ == "__main__":
    if len(sys.argv) > 1:
        question = sys.argv[1]
        result = ask(question)
        print(result)
    else:
        print("Please provide a question.")