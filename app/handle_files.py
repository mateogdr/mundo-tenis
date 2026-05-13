
from flask import request, redirect, flash, current_app
from functools import wraps
from PIL import Image
import uuid
import os

def allowed_file(filename):
    return "." in filename and \
        filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]


def save_file(resource_name="jugador"):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            file = request.files.get("file")
            filename = None

            if file and file.filename != "":
                if not allowed_file(file.filename):
                    flash("Error: Extensión no permitida", "error")
                    return redirect(request.url)

                file.seek(0, os.SEEK_END)
                size = file.tell()
                if size > 5 * 1024 * 1024:
                    flash("Error: El archivo supera 5MB", "error")
                    return redirect(request.url)
                file.seek(0)

                extension = file.filename.rsplit(".", 1)[1].lower()
                filename = f"{uuid.uuid4()}.{extension}"
                file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
                file.save(file_path)

                thumb_folder = current_app.config.get("THUMB_FOLDER")
                if thumb_folder:
                    os.makedirs(thumb_folder, exist_ok=True)
                    thumb_path = os.path.join(thumb_folder, filename)
                    with Image.open(file_path) as img:
                        img.thumbnail((150, 150))
                        img.save(thumb_path)

                if resource_name and resource_name in kwargs:
                    resource = kwargs[resource_name]
                    resource.filename = filename

            if resource_name is None:
                kwargs["filename"] = filename

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def delete_file(resource_name="jugador"):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            resource = kwargs.get(resource_name)
            file = request.files.get("file")

            if resource is None:
                return f(*args, **kwargs)

            is_delete_method = request.method == "DELETE"

            is_update_with_new_file = (
                request.method in ["PUT", "POST"]
                and file
                and file.filename != ""
            )

            if is_delete_method or is_update_with_new_file:
                fg = getattr(resource, 'filename', None)
                if fg:
                    file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], fg)
                    if os.path.exists(file_path):
                        os.remove(file_path)

                    thumb_path = os.path.join(current_app.root_path, "assets/thumbnails", fg)
                    if os.path.exists(thumb_path):
                        os.remove(thumb_path)

                    resource.filename = None

            return f(*args, **kwargs)
        return decorated_function
    return decorator