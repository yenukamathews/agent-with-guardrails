
import json
import os

from openai import OpenAI

from guards import validate_input
from tools import calculator, sql_tool


MODEL = os.getenv("OPENAI_MODEL", "gpt-5.5")

client = OpenAI()

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "name": "calculator",
        "description": "Calculate a basic arithmetic expression.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {"type": "string"}
            },
            "required": ["expression"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "sql_tool",
        "description": (
            "Validate a SELECT query. This tool does not execute SQL."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            },
            "required": ["query"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]

ALLOWED_TOOLS = {
    "calculator": calculator,
    "sql_tool": sql_tool,
}


def run_agent(user_message: str) -> str:
    # Validate input before sending it to the model.
    try:
        validate_input(user_message)
    except ValueError:
        return "Blocked: input failed safety validation."

    response = client.responses.create(
        model=MODEL,
        instructions=(
            "You are a guarded assistant. "
            "Use calculator for arithmetic. "
            "Use sql_tool only to validate SELECT queries. "
            "Never claim SQL was executed. "
            "Never request tools outside the supplied tool list."
        ),
        input=user_message,
        tools=TOOL_DEFINITIONS,
        tool_choice="auto",
        parallel_tool_calls=False,
        max_output_tokens=500,
    )

    for item in response.output:
        if item.type != "function_call":
            continue

        tool_function = ALLOWED_TOOLS.get(item.name)

        if tool_function is None:
            return "Blocked: tool is not allowed."

        try:
            arguments = json.loads(item.arguments)

            if not isinstance(arguments, dict):
                raise ValueError("Tool arguments must be an object.")

            if item.name == "calculator":
                if set(arguments) != {"expression"}:
                    raise ValueError("Invalid calculator arguments.")
                if not isinstance(arguments["expression"], str):
                    raise ValueError("Expression must be text.")

            elif item.name == "sql_tool":
                if set(arguments) != {"query"}:
                    raise ValueError("Invalid SQL arguments.")
                if not isinstance(arguments["query"], str):
                    raise ValueError("Query must be text.")

            result = tool_function(**arguments)
            return json.dumps(result, ensure_ascii=False)

        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            return f"Tool validation error: {exc}"

    return response.output_text or "No response was generated."


if __name__ == "__main__":
    print("Guarded AI Agent")
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

        try:
            print("Agent:", run_agent(message))
        except Exception as exc:
            # Diagnostic output for local development.
            print(f"Agent error: {type(exc).__name__}: {exc}")
