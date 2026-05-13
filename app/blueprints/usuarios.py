from flask import Blueprint, render_template, request, redirect, url_for, abort, g, flash
from models.usuarios import Usuario
from database import db
from functools import wraps
from .auth import login_required, admin_required

usuarios_bp = Blueprint("usuarios", __name__, template_folder="../templates")

def load_usuario(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        usuario_id = request.view_args.get("usuario_id")
        if usuario_id is not None:
            usuario = Usuario.query.get(usuario_id)
            if usuario is None:
                abort(404)
            kwargs["usuario"] = usuario
        return f(*args, **kwargs)
    return decorated_function

@usuarios_bp.route("/", methods=["GET"])
def list():

    if g.user is None or g.user.role != 'admin':
        flash("No tienes permisos para acceder a esta página", "error")
        return redirect(url_for("tu_mundo"))
    
    page = request.args.get("page", 1, type=int)  
    query = Usuario.query

    pagination = query.paginate(page=page, per_page=5, error_out=False)
    usuarios = pagination.items
    
    return render_template("usuarios/list.html", usuarios=usuarios, pagination=pagination)

@usuarios_bp.route("/new", methods=["GET"])
def new():
    return render_template("usuarios/new.html")

@usuarios_bp.route("/", methods=["POST"])
def create():
    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()
    password_confirm = request.form.get("password_confirm", "").strip()
    
    error = None
    
    if not username:
        error = 'El nombre de usuario es requerido.'
    elif not email:
        error = 'El email es requerido.'
    elif not password:
        error = 'La contraseña es requerida.'
    elif password != password_confirm:
        error = 'Las contraseñas no coinciden.'
    
    if error is None:
        try:
            usuario = Usuario(username=username, email=email)
            usuario.set_password(password)
            db.session.add(usuario)
            db.session.commit()
            flash("Usuario creado correctamente", "success")
            return redirect(url_for("usuarios.list"))
        except Exception as e:
            db.session.rollback()
            error = 'El nombre de usuario o email ya existe.'
    
    if error:
        flash(error, 'error')
        return redirect(url_for("usuarios.new"))

@usuarios_bp.route("/<usuario_id>", methods=["GET"])
@load_usuario
def show(usuario_id, usuario):
    if g.user is None or (usuario.id != g.user.id and g.user.role != 'admin'):
        flash("No tienes permisos para ver este usuario", "error")
        if g.user is None:
            return redirect(url_for("auth.login"))
        return redirect(url_for("tu_mundo"))
    
    return render_template("usuarios/show.html", usuario=usuario)

@usuarios_bp.route("/<usuario_id>/edit", methods=["GET"])
@load_usuario
def edit(usuario_id, usuario):
    if g.user is None or (usuario.id != g.user.id and g.user.role != 'admin'):
        flash("No tienes permisos para editar este usuario", "error")
        if g.user is None:
            return redirect(url_for("auth.login"))
        return redirect(url_for("tu_mundo"))
    
    return render_template("usuarios/edit.html", usuario=usuario)

@usuarios_bp.route("/<usuario_id>", methods=["PUT"])
@load_usuario
def update(usuario_id, usuario):
    if g.user is None or (usuario.id != g.user.id and g.user.role != 'admin'):
        flash("No tienes permisos para editar este usuario", "error")
        abort(403)
    
    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip()
    
    error = None
    
    if not username:
        error = 'El nombre de usuario es requerido.'
    elif not email:
        error = 'El email es requerido.'
    
    if error is None:
        try:
            usuario.username = username
            usuario.email = email
            db.session.commit()
            flash("Usuario actualizado correctamente", "success")
            return redirect(url_for("usuarios.list"))
        except Exception as e:
            db.session.rollback()
            error = 'El nombre de usuario o email ya existe.'
    
    if error:
        flash(error, 'error')
        return redirect(url_for("usuarios.edit", usuario_id=usuario_id))

@usuarios_bp.route("/<usuario_id>", methods=["DELETE"])
@load_usuario
def delete(usuario_id, usuario):
    if g.user is None or g.user.role != 'admin':
        flash("No tienes permisos para eliminar usuarios", "error")
        abort(403)
    
    if usuario.id == g.user.id:
        flash("No puedes eliminar tu propia cuenta", "error")
        return redirect(url_for("usuarios.list"))
    
    try:
        db.session.delete(usuario)
        db.session.commit()
        flash("Usuario eliminado correctamente", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error al eliminar el usuario", "error")
    
    return redirect(url_for("usuarios.list"))