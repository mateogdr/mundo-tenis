from flask import Blueprint, render_template, request, redirect, url_for, abort, flash, g, current_app as app
from functools import wraps
from models.jugadores import Jugador
from models.usuarios import Usuario
from database import db
from handle_files import save_file, delete_file
from .auth import login_required
import re
from extensions import cache

jugadores_bp = Blueprint("jugadores", __name__, template_folder="../templates")


def load_jugador(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        jugador_id = request.view_args.get("id")

        if jugador_id is not None:
            jugador = Jugador.query.get(jugador_id)
            if jugador is None:
                app.logger.warning(f"Intento de acceso a jugador inexistente ID: {jugador_id}")
                abort(404)
            kwargs["jugador"] = jugador

        return f(*args, **kwargs)
    return decorated_function


def owner_or_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        jugador = kwargs.get("jugador")
        if g.user is None:
            flash("Debes estar conectado", "error")
            return redirect(url_for("auth.login"))
        if jugador and jugador.user_id != g.user.id and g.user.role != 'admin':
            flash("No tienes permisos para realizar esta acción", "error")
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


@jugadores_bp.route("/", methods=["GET"])
@cache.cached(timeout=30, query_string=True)
def list():
    app.logger.debug("Cargando lista de jugadores (posible hit de caché)")
    nombre = request.args.get("nombre", "").strip()
    activo = request.args.get("activo", "").strip()
    page = request.args.get("page", 1, type=int)

    query = Jugador.query

    if nombre:
        query = query.filter(Jugador.nombre.ilike(f"%{nombre}%"))

    if activo:
        activo_bool = activo.lower() == 'true'
        query = query.filter(Jugador.activo == activo_bool)

    if g.user is None:
        pass
    elif g.user.role == 'admin':
        pass
    else:
        query = query.filter(Jugador.user_id == g.user.id)

    pagination = query.paginate(page=page, per_page=5, error_out=False)
    jugadores = pagination.items

    return render_template("jugadores/list.html", jugadores=jugadores, pagination=pagination)


@jugadores_bp.route("/<int:id>", methods=["GET"])
@load_jugador
@cache.memoize(timeout=60)
def show(id, jugador):
    if g.user is None or (jugador.user_id != g.user.id and g.user.role != 'admin'):
        if g.user is None:
            flash("Debes estar conectado para ver este jugador", "error")
            return redirect(url_for("auth.login"))
        app.logger.warning(f"Acceso denegado al jugador {id} para el usuario {g.user.username}")
        abort(403)
    return render_template("jugadores/show.html", jugador=jugador)


@jugadores_bp.route("/new", methods=["GET"])
@login_required
def new():
    return render_template("jugadores/new.html")


@jugadores_bp.route("/", methods=["POST"])
@login_required
@save_file(resource_name=None)  
def create(filename=None):

    nombre = request.form.get("nombre", "").strip()
    puntos = request.form.get("puntos", "")
    edad = request.form.get("edad", "")
    nacionalidad = request.form.get("nacionalidad", "").strip()
    descripcion = request.form.get("descripcion", "").strip()
    activo = request.form.get("activo", "False")

    if re.search(r"[(),/=]", nombre):
        app.logger.warning(f"Validación fallida: Nombre '{nombre}' contiene caracteres prohibidos.")
        flash("El nombre contiene caracteres no permitidos ( , ) / = )", "error")
        return redirect(url_for("jugadores.new"))

    try:
        edad = int(edad)
        if edad < 0:
            flash("La edad no puede ser negativa", "error")
            return redirect(url_for("jugadores.new"))
    except ValueError:
        app.logger.warning("Validación fallida: Edad o puntos no son números válidos.")
        flash("La edad debe ser un número válido", "error")
        return redirect(url_for("jugadores.new"))
    
    try:
        puntos = int(puntos)
        if puntos < 0:
            flash("Los puntos no pueden ser negativos", "error")
            return redirect(url_for("jugadores.new"))
    except ValueError:
        flash("Los puntos deben ser un número válido", "error")
        return redirect(url_for("jugadores.new"))
    
    nuevo = Jugador(
        nombre=nombre,
        nacionalidad=nacionalidad,
        edad=edad,
        puntos=puntos,
        activo=activo == "True",
        descripcion=descripcion,
        filename=filename,
        user_id=g.user.id
    )

    try:
        db.session.add(nuevo)
        db.session.commit()
        cache.delete_memoized(show) 
        cache.clear()
        app.logger.info(f"Jugador '{nombre}' creado exitosamente por {g.user.username}")
        flash("Jugador añadido correctamente", "success")
        return redirect(url_for("jugadores.list"))
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error al crear jugador: {str(e)}")
        flash("Error al crear el jugador", "error")
        return redirect(url_for("jugadores.new"))


@jugadores_bp.route("/<int:id>/edit", methods=["GET"])
@load_jugador
@login_required
def edit(id, jugador):
    if jugador.user_id != g.user.id and g.user.role != 'admin':
        flash("No tienes permisos para editar este jugador", "error")
        abort(403)
    return render_template("jugadores/edit.html", jugador=jugador)


@jugadores_bp.route("/<int:id>", methods=["PUT"])
@load_jugador
@login_required
@delete_file(resource_name="jugador")
@save_file(resource_name="jugador")
def update(id, jugador):
    
    if jugador.user_id != g.user.id and g.user.role != 'admin':
        app.logger.warning(f"Intento de edición no autorizada por {g.user.username}")
        flash("No tienes permisos para editar este jugador", "error")
        abort(403)

    nombre = request.form.get("nombre", "").strip()
    puntos = request.form.get("puntos", "")
    edad = request.form.get("edad", "")
    nacionalidad = request.form.get("nacionalidad", "").strip()
    descripcion = request.form.get("descripcion", "").strip()
    activo = request.form.get("activo", "False")

    if re.search(r"[(),/=]", nombre):
        flash("El nombre contiene caracteres no permitidos ( , ) / = )", "error")
        return redirect(url_for("jugadores.edit", id=id))

    try:
        edad = int(edad)
        if edad < 0:
            flash("La edad no puede ser negativa", "error")
            return redirect(url_for("jugadores.edit", id=id))
    except ValueError:
        flash("La edad debe ser un número válido", "error")
        return redirect(url_for("jugadores.edit", id=id))
    
    try:
        puntos = int(puntos)
        if puntos < 0:
            flash("Los puntos no pueden ser negativos", "error")
            return redirect(url_for("jugadores.edit", id=id))
    except ValueError:
        flash("Los puntos deben ser un número válido", "error")
        return redirect(url_for("jugadores.edit", id=id))

    jugador.nombre = nombre
    jugador.nacionalidad = nacionalidad
    jugador.edad = edad
    jugador.puntos = puntos
    jugador.activo = activo == "True"
    jugador.descripcion = descripcion

    try:
        db.session.commit()
        cache.delete_memoized(show) 
        cache.clear()
        app.logger.info(f"Jugador ID {id} actualizado por {g.user.username}")
        flash("Jugador editado correctamente", "success")
        return redirect(url_for("jugadores.list"))
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error al editar jugador {id}: {str(e)}")
        flash("Error al editar el jugador", "error")
        return redirect(url_for("jugadores.edit", id=id))


@jugadores_bp.route("/<int:id>", methods=["DELETE"])
@load_jugador
@login_required
@delete_file(resource_name="jugador")
def delete(id, jugador):
    
    if jugador.user_id != g.user.id and g.user.role != 'admin':
        flash("No tienes permisos para eliminar este jugador", "error")
        abort(403)

    try:
        db.session.delete(jugador)
        db.session.commit()
        cache.delete_memoized(show) 
        cache.clear()
        app.logger.info(f"(ID: {id}) eliminado por {g.user.username}")
        flash("Jugador borrado correctamente", "success")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error al eliminar jugador {id}: {str(e)}")
        flash("Error al eliminar el jugador", "error")

    return redirect(url_for("jugadores.list"))