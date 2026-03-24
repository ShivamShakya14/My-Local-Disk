from flask import Flask, jsonify, request, render_template, send_from_directory, session, redirect, url_for
import os
from werkzeug.utils import secure_filename
import io
import zipfile
import shutil
from flask import Response

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace this with a strong secret key

USERNAME = "admin"
PASSWORD = "admin"

BASE_DIR = os.path.abspath("shared")
os.makedirs(BASE_DIR, exist_ok=True)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == USERNAME and password == PASSWORD:
            session["user"] = username
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/")
@app.route("/<path:subpath>")
def home(subpath=""):
    if "user" not in session:
        return redirect(url_for("login"))

    abs_path = os.path.join(BASE_DIR, subpath)
    if not os.path.exists(abs_path):
        return "Folder not found", 404

    items = []
    for entry in os.listdir(abs_path):
        full_path = os.path.join(abs_path, entry)
        items.append({
            "name": entry,
            "is_dir": os.path.isdir(full_path),
            "path": os.path.join(subpath, entry).replace("\\", "/")
        })

    return render_template("index.html", files=items, current_path=subpath)

@app.route("/list")
def list_files():
    if "user" not in session:
        return redirect(url_for("login"))

    subpath = request.args.get("path", "")
    abs_path = os.path.join(BASE_DIR, subpath)

    if not os.path.exists(abs_path):
        return jsonify([])

    items = []
    for entry in os.listdir(abs_path):
        full_path = os.path.join(abs_path, entry)
        items.append({
            "name": entry,
            "is_dir": os.path.isdir(full_path)
        })

    return jsonify(items)

@app.route("/upload", methods=["POST"])
def upload():
    if "user" not in session:
        return redirect(url_for("login"))

    subpath = request.args.get("path", "")
    abs_path = os.path.join(BASE_DIR, subpath)
    os.makedirs(abs_path, exist_ok=True)

    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    files = request.files.getlist('file')
    saved_files = []
    for f in files:
        filename = secure_filename(f.filename)
        if filename == '':
            continue
        save_path = os.path.join(abs_path, filename)
        f.save(save_path)
        saved_files.append(filename)

    return jsonify({"status": "success", "uploaded": saved_files})

@app.route("/download/<path:filepath>")
def download_file(filepath):
    if "user" not in session:
        return redirect(url_for("login"))

    safe_name = os.path.basename(filepath)
    folder = os.path.dirname(filepath)
    full_folder = os.path.join(BASE_DIR, folder)
    return send_from_directory(full_folder, safe_name, as_attachment=True)

@app.route("/mkdir", methods=["POST"])
def make_folder():
    if "user" not in session:
        return redirect(url_for("login"))

    subpath = request.args.get("path", "")
    folder_name = request.form.get("foldername", "")
    if not folder_name:
        return jsonify({"error": "Folder name required"}), 400

    target_path = os.path.join(BASE_DIR, subpath, secure_filename(folder_name))
    os.makedirs(target_path, exist_ok=True)
    return jsonify({"status": "created", "path": target_path})

def recursive_delete(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.remove(path)

@app.route("/delete", methods=["POST"])
def delete_item():
    if "user" not in session:
        return redirect(url_for("login"))

    subpath = request.args.get("path", "")
    names = request.form.getlist("names[]")

    if not names:
        return jsonify({"error": "No items selected"}), 400

    errors = []
    for name in names:
        target_path = os.path.join(BASE_DIR, subpath, name)
        if not os.path.exists(target_path):
            errors.append(f"Not found: {name}")
            continue
        try:
            recursive_delete(target_path)
        except Exception as e:
            errors.append(f"{name}: {str(e)}")

    if errors:
        return jsonify({"error": errors}), 500
    return jsonify({"status": "deleted", "deleted": names})

@app.route("/rename", methods=["POST"])
def rename_item():
    if "user" not in session:
        return redirect(url_for("login"))

    subpath = request.args.get("path", "")
    old_name = request.form.get("old_name", "")
    new_name = request.form.get("new_name", "")

    if not old_name or not new_name:
        return jsonify({"error": "Old name and new name required"}), 400

    old_path = os.path.join(BASE_DIR, subpath, old_name)
    new_path = os.path.join(BASE_DIR, subpath, secure_filename(new_name))

    if not os.path.exists(old_path):
        return jsonify({"error": "Item not found"}), 404

    if os.path.exists(new_path):
        return jsonify({"error": "New name already exists"}), 409

    try:
        os.rename(old_path, new_path)
        return jsonify({"status": "renamed", "old_name": old_name, "new_name": new_name})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download_batch', methods=['POST'])
def download_batch():
    if "user" not in session:
        return redirect(url_for("login"))

    subpath = request.args.get("path", "")
    items = request.json.get("items", [])

    if not items:
        return jsonify({"error": "No items selected"}), 400

    abs_paths = [os.path.join(BASE_DIR, subpath, item) for item in items]

    if len(items) == 1 and os.path.isfile(abs_paths[0]):
        folder = os.path.dirname(abs_paths[0])
        filename = os.path.basename(abs_paths[0])
        return send_from_directory(folder, filename, as_attachment=True)

    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for path in abs_paths:
            if not os.path.exists(path):
                continue
            if os.path.isfile(path):
                zf.write(path, os.path.basename(path))
            else:
                for root, dirs, files in os.walk(path):
                    for file in files:
                        abs_filename = os.path.join(root, file)
                        rel_path = os.path.relpath(abs_filename, BASE_DIR)
                        zf.write(abs_filename, rel_path)
    memory_file.seek(0)
    return Response(
        memory_file,
        mimetype='application/zip',
        headers={'Content-Disposition': f'attachment;filename=download.zip'}
    )

@app.route('/download_zip/<path:folderpath>')
def download_zip(folderpath):
    if "user" not in session:
        return redirect(url_for("login"))

    abs_folder = os.path.join(BASE_DIR, folderpath)
    if not os.path.isdir(abs_folder):
        return "Folder not found", 404

    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(abs_folder):
            for file in files:
                abs_filename = os.path.join(root, file)
                relative_path = os.path.relpath(abs_filename, abs_folder)
                zf.write(abs_filename, relative_path)
    memory_file.seek(0)
    zip_filename = os.path.basename(folderpath.rstrip('/\\')) + '.zip'
    return Response(
        memory_file,
        mimetype='application/zip',
        headers={'Content-Disposition': f'attachment;filename={zip_filename}'}
    )

if __name__ == "__main__":
    print("Flask server running. Open http://localhost:8000")
    app.run(host="0.0.0.0", port=8214)
