
import time
import os
import requests

GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "models/{model}:generateContent"
)


class AIConfigurationError(Exception):
    pass


class AIServiceError(Exception):
    pass


ACTION_INSTRUCTIONS = {
    "generate": (
        "Generate a correct, readable program that satisfies "
        "the user's request. State assumptions briefly and "
        "include the complete code in a fenced code block."
    ),
    "explain": (
        "Explain the supplied code clearly, step by step. "
        "Explain important syntax and logic, and include a short summary."
    ),
    "debug": (
        "Review the supplied code for syntax errors, runtime errors, "
        "and logic bugs. Explain each issue and provide a corrected "
        "complete version when possible."
    ),
    "optimize": (
        "Improve readability, efficiency, and maintainability "
        "without changing intended behavior. Explain the meaningful "
        "improvements and provide the revised code."
    ),
    "convert": (
        "Convert the supplied code into the requested target "
        "programming language. Preserve behavior and explain "
        "important language differences."
    ),
    "chat": (
        "Answer the programming question accurately and clearly. "
        "Use examples where useful."
    ),
}


def generate_ai_response(
    action, prompt, code, language, target_language
):

    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    model = os.getenv(
        "GEMINI_MODEL",
        "gemini-3.8-flash"
    ).strip()

    if not api_key:
        raise AIConfigurationError(
            "AI is not configured. Add your Gemini API key "
            "to the .env file and restart the application."
        )

    if action not in ACTION_INSTRUCTIONS:
        raise AIServiceError("Unsupported AI action.")

    instruction = ACTION_INSTRUCTIONS[action]

    user_parts = [
        f"Task: {instruction}",
        f"Programming language: {language}",
    ]

    if action == "convert":
        user_parts.append(
            f"Target language: {target_language}"
        )

    if prompt:
        user_parts.append(
            f"User request:\n{prompt}"
        )

    if code:
        user_parts.append(
            f"Code:\n```{language.lower()}\n{code}\n```"
        )

    user_parts.append(
        "Be precise. If information is missing, state reasonable "
        "assumptions. Do not claim code was executed or tested. "
        "Keep the response focused."
    )

    contents = "\n\n".join(user_parts)

    url = GEMINI_API_URL.format(model=model)

    request_data = {
        "contents": [
            {
                "parts": [
                    {"text": contents}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 4096
        }
    }

    response = None

    # Retry temporary server overload errors.
    for attempt in range(3):

        try:
            response = requests.post(
                url,
                params={"key": api_key},
                json=request_data,
                timeout=(10, 60),
            )

        except requests.Timeout as exc:
            raise AIServiceError(
                "The AI service took too long to respond. "
                "Please try again."
            ) from exc

        except requests.RequestException as exc:
            raise AIServiceError(
                "Could not connect to the AI service. "
                "Check your internet connection."
            ) from exc

        # Successful response or a non-retryable error.
        if response.status_code != 503:
            break

        # Wait before retrying a temporary 503 error.
        if attempt < 2:
            time.sleep(2 ** (attempt + 1))

    # Handle API errors.
    if response.status_code != 200:

        try:
            details = response.json().get(
                "error", {}
            ).get("message", "")

        except (ValueError, AttributeError):
            details = ""

        if response.status_code in (401, 403):
            raise AIServiceError(
                "API key rejected. Check your Gemini API key."
            )

        if response.status_code == 404:
            raise AIServiceError(
                f"Model '{model}' was not found or is unavailable "
                "for this API version. Check the model name "
                "and your API access."
            )

        if response.status_code == 429:
            raise AIServiceError(
                "AI API quota or rate limit reached. "
                "Please wait and try again."
            )

        if response.status_code == 503:
            raise AIServiceError(
                "The AI service is temporarily overloaded. "
                "Please try again later."
            )

        raise AIServiceError(
            f"AI service returned an error "
            f"({response.status_code}). {details[:300]}".strip()
        )

    # Extract AI response.
    try:
        payload = response.json()

        candidates = payload.get("candidates", [])

        if not candidates:
            raise AIServiceError(
                "The AI service did not return a response. "
                "Please try again."
            )

        parts = candidates[0]["content"]["parts"]

        answer = "\n".join(
            part.get("text", "")
            for part in parts
            if part.get("text")
        )

    except (ValueError, KeyError, IndexError, TypeError) as exc:
        raise AIServiceError(
            "Unexpected response from the AI service."
        ) from exc

    if not answer.strip():
        raise AIServiceError(
            "The AI service returned an empty response."
        )

    return answer.strip()
