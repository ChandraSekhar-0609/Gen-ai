import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from backend.ai_engine import generate_ai_response, AIConfigurationError, AIServiceError
from backend.database import init_db, save_history, get_history, clear_history

load_dotenv()
app = Flask(__name__,template_folder="frontend/templates",static_folder="frontend/static")
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024

init_db()

ALLOWED_ACTIONS = {"generate", "explain", "debug", "optimize", "convert", "chat"}

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/api/assist")
def assist():
    data = request.get_json(silent=True) or {}
    action = str(data.get("action", "chat")).strip().lower()
    prompt = str(data.get("prompt", "")).strip()
    code = str(data.get("code", "")).strip()
    language = str(data.get("language", "Python")).strip()
    target_language = str(data.get("target_language", "JavaScript")).strip()

    if action not in ALLOWED_ACTIONS:
        return jsonify({"error": "Unsupported assistant action."}), 400
    if not prompt and not code:
        return jsonify({"error": "Enter a prompt or provide code first."}), 400
    if len(prompt) > 12000 or len(code) > 30000:
        return jsonify({"error": "Input is too long. Please shorten it and try again."}), 413

    try:
        answer = generate_ai_response(
            action=action,
            prompt=prompt,
            code=code,
            language=language,
            target_language=target_language,
        )
        save_history(action, language, prompt, code, answer)
        return jsonify({"answer": answer})
    except AIConfigurationError as exc:
        return jsonify({"error": str(exc)}), 503
    except AIServiceError as exc:
        return jsonify({"error": str(exc)}), 502
    except Exception:
        app.logger.exception("Unexpected error while processing AI request")
        return jsonify({"error": "Something went wrong on the server. Please try again."}), 500

@app.get("/api/history")
def history():
    return jsonify({"items": get_history()})

@app.delete("/api/history")
def delete_history():
    clear_history()
    return jsonify({"message": "History cleared."})

@app.errorhandler(413)
def too_large(_error):
    return jsonify({"error": "Request is too large."}), 413

if __name__ == "__main__":
    # Debug mode is intended only for local development.
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=False)
