
from guards import validate_input
from tools import calculator, sql_tool


def run_local_agent(message: str) -> str:
    """Run basic tool routing locally without API calls."""

    try:
        validate_input(message)
    except ValueError:
        return "BLOCKED: Input failed safety validation."

    text = message.strip()
    lower = text.lower()

    # Calculator tool
    if any(word in lower for word in ("calculate", "compute")):
        expression = text
        for prefix in ("calculate", "compute"):
            if lower.startswith(prefix):
                expression = text[len(prefix):].strip()
                break

        try:
            result = calculator(expression)
            return f"Calculator result: {result}"
        except (ValueError, TypeError, ZeroDivisionError) as exc:
            return f"Calculator rejected the expression: {exc}"

    # SQL validation tool
    if lower.startswith(("sql:", "validate sql:")):
        query = text.split(":", 1)[1].strip()

        try:
            result = sql_tool(query)
            return f"SQL tool: {result}"
        except ValueError as exc:
            return f"SQL rejected: {exc}"

    return (
        "Local mode: I can calculate arithmetic or validate SQL. "
        "Try 'Calculate 12 * (3 + 2)' or "
        "'SQL: SELECT * FROM users;'"
    )


if __name__ == "__main__":
    print("Guarded AI Agent — LOCAL MODE")
    print("No OpenAI API calls are made.")
    print("Type 'exit' to quit.")

    while True:
        try:
            message = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if message.lower() == "exit":
            print("Goodbye!")
            break

        if not message:
            print("Please enter a message.")
            continue

        print("Agent:", run_local_agent(message))
