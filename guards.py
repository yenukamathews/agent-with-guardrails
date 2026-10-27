
import re


def validate_input(user_input: str) -> bool:
    """Reject empty input and known prompt-injection phrases."""

    if not isinstance(user_input, str) or not user_input.strip():
        raise ValueError("Input cannot be empty.")

    blocked_phrases = [
        "ignore all previous instructions",
        "ignore previous instructions",
        "reveal secrets",
    ]

    normalized_input = user_input.lower()

    for phrase in blocked_phrases:
        if phrase in normalized_input:
            raise ValueError("Blocked: possible prompt injection.")

    return True


def validate_sql(query: str) -> str:
    """Allow one basic SELECT query and reject common risky syntax."""

    if not isinstance(query, str) or not query.strip():
        raise ValueError("SQL query cannot be empty.")

    query = query.strip()

    # Remove one optional trailing semicolon for validation.
    if query.endswith(";"):
        query = query[:-1].rstrip()

    # Reject multiple statements and extra semicolons.
    if ";" in query:
        raise ValueError("Only one SQL statement is allowed.")

    # Reject SQL comments.
    if "--" in query or "/*" in query or "*/" in query:
        raise ValueError("SQL comments are not allowed.")

    # Reject common dangerous or unsupported SQL keywords.
    if re.search(
        r"\b(insert|update|delete|drop|alter|create|truncate|"
        r"grant|revoke|exec|execute|union|into|attach|detach|pragma)\b",
        query,
        re.IGNORECASE,
    ):
        raise ValueError("Blocked: unsafe SQL keyword.")

    # Require a SELECT query.
    if not re.match(r"^select\b", query, re.IGNORECASE):
        raise ValueError("Blocked: only SELECT queries are allowed.")

    # Reject a few suspicious SQL constructs.
    if re.search(
        r"\bwaitfor\b|\bxp_cmdshell\b",
        query,
        re.IGNORECASE,
    ):
        raise ValueError("Blocked: suspicious SQL construct.")

    # Preserve the semicolon expected by the existing tests.
    return query + ";"
