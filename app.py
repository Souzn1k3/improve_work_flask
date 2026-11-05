import itertools
import json
from pathlib import Path

from flask import Flask, jsonify, request, abort

app = Flask(__name__)

DATA_FILE = Path(__file__).with_name("notes.json")

def load_notes():
    try:
        with DATA_FILE.open(encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return []
    if not isinstance(data, list):
        return []
    loaded = []
    for item in data:
        if not isinstance(item, dict):
            continue
        note_id = item.get("id")
        author = item.get("author")
        text = item.get("text")
        likes = item.get("likes", 0)
        if not isinstance(note_id, int) or isinstance(note_id, bool):
            continue
        if not isinstance(author, str) or not isinstance(text, str):
            continue
        if not isinstance(likes, int) or isinstance(likes, bool) or likes < 0:
            likes = 0
        loaded.append({"id": note_id, "author": author, "text": text, "likes": likes})
    return loaded

def save_notes():
    tmp = DATA_FILE.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)
    tmp.replace(DATA_FILE)

def find_note(note_id):
    return next((n for n in notes if n["id"] == note_id), None)

def clean_field(data, field):
    value = data.get(field)
    if not isinstance(value, str):
        return None
    value = value.strip()
    return value or None

def parse_query_int(name, default, minimum, maximum=None):
    raw = request.args.get(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return None
    if value < minimum or (maximum is not None and value > maximum):
        return None
    return value

notes = load_notes()
note_ids = itertools.count(max((n["id"] for n in notes), default=0) + 1)

@app.get("/")
def index():
    return "<h1>Гостевая книга</h1>"

@app.get("/notes")
def list_notes():
    limit = parse_query_int("limit", 10, 1, 100)
    offset = parse_query_int("offset", 0, 0)
    if limit is None or offset is None:
        return jsonify(error="limit must be 1..100, offset must be >= 0"), 400
    sort = request.args.get("sort", "id")
    order = request.args.get("order", "asc")
    if sort not in ("id", "likes"):
        return jsonify(error="sort must be 'id' or 'likes'"), 400
    if order not in ("asc", "desc"):
        return jsonify(error="order must be 'asc' or 'desc'"), 400
    author = request.args.get("author")
    result = notes if author is None else [n for n in notes if n["author"] == author.strip()]
    result = sorted(result, key=lambda n: n[sort], reverse=order == "desc")
    return jsonify(result[offset:offset + limit])

@app.post("/notes")
def create_note():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="JSON body is required"), 400
    author = clean_field(data, "author")
    text = clean_field(data, "text")
    if author is None or text is None:
        return jsonify(error="fields 'author' and 'text' (non-empty strings) are required"), 400
    note = {"id": next(note_ids), "author": author, "text": text, "likes": 0}
    notes.append(note)
    save_notes()
    return jsonify(note), 201

@app.get("/notes/<int:note_id>")
def get_note(note_id):
    note = find_note(note_id)
    if note is None:
        abort(404)
    return jsonify(note)

@app.put("/notes/<int:note_id>")
def replace_note(note_id):
    note = find_note(note_id)
    if note is None:
        abort(404)
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="JSON body is required"), 400
    author = clean_field(data, "author")
    text = clean_field(data, "text")
    if author is None or text is None:
        return jsonify(error="fields 'author' and 'text' (non-empty strings) are required"), 400
    note["author"] = author
    note["text"] = text
    save_notes()
    return jsonify(note)

@app.patch("/notes/<int:note_id>")
def update_note(note_id):
    note = find_note(note_id)
    if note is None:
        abort(404)
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="JSON body is required"), 400
    updated = False
    for field in ("author", "text"):
        if field in data:
            value = clean_field(data, field)
            if value is None:
                return jsonify(error=f"field '{field}' must be a non-empty string"), 400
            note[field] = value
            updated = True
    if not updated:
        return jsonify(error="at least one of fields 'author' or 'text' is required"), 400
    save_notes()
    return jsonify(note)

@app.post("/notes/<int:note_id>/like")
def like_note(note_id):
    note = find_note(note_id)
    if note is None:
        abort(404)
    note["likes"] += 1
    save_notes()
    return jsonify(note)

@app.delete("/notes/<int:note_id>")
def delete_note(note_id):
    note = find_note(note_id)
    if note is None:
        abort(404)
    notes.remove(note)
    save_notes()
    return "", 204

@app.delete("/notes")
def delete_notes_by_author():
    author = request.args.get("author")
    if author is None or not author.strip():
        return jsonify(error="query parameter 'author' is required"), 400
    author = author.strip()
    removed = [n for n in notes if n["author"] == author]
    for note in removed:
        notes.remove(note)
    if removed:
        save_notes()
    return jsonify(deleted=len(removed))

@app.get("/authors")
def list_authors():
    stats = {}
    for note in notes:
        item = stats.setdefault(note["author"], {"author": note["author"], "notes": 0, "likes": 0})
        item["notes"] += 1
        item["likes"] += note.get("likes", 0)
    return jsonify(sorted(stats.values(), key=lambda item: item["author"]))

@app.errorhandler(404)
def not_found(error):
    return jsonify(error="not found"), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify(error="method not allowed"), 405

if __name__ == "__main__":
    app.run(debug=True)
