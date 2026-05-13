from flask import Blueprint, render_template, request, redirect, url_for, abort, flash, g, current_app as app
from functools import wraps
from models.pistas import Pista
from models.usuarios import Usuario
from database import db
from handle_files import save_file, delete_file
from .auth import login_required
import re
from extensions import cache


pistas_bp = Blueprint("pistas", __name__, template_folder="../templates")


def load_pista(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        pista_id = request.view_args.get("id")
        if pista_id is not None:
            pista = Pista.query.get(pista_id)
            if not pista:
                app.logger.warning(f"Intento de acceso a pista inexistente ID: {pista_id}")
                abort(404)
            kwargs["pista"] = pista
        return f(*args, **kwargs)
    return decorated_function

@pistas_bp.route("/", methods=["GET"])
@cache.cached(timeout=60, query_string=True)
def list():
    app.logger.debug("Consultando lista de pistas (Cache activa)")
    nombre = request.args.get("nombre", "").strip()
    superficie = request.args.get("superficie", "").strip()
    page = request.args.get("page", 1, type=int)

    query = Pista.query

    if nombre:
        query = query.filter(Pista.nombre.ilike(f"%{nombre}%"))
    
    if superficie:
        query = query.filter(Pista.superficie == superficie)

    if g.user is None:
        pass
    elif g.user.role == 'admin':
        pass
    else:
        query = query.filter(Pista.user_id == g.user.id)

    pagination = query.paginate(page=page, per_page=5, error_out=False)
    pistas = pagination.items

    return render_template("pistas/list.html", pistas=pistas, pagination=pagination)

@pistas_bp.route("/new", methods=["GET"]) 
@login_required
def new():
    return render_template("pistas/new.html")

@pistas_bp.route("/", methods=["POST"])
@login_required
@save_file(resource_name=None)
def create(filename=None):

    nombre = request.form.get("nombre", "").strip()
    torneo = request.form.get("torneo", "").strip()
    pais = request.form.get("pais", "").strip()
    superficie = request.form.get("superficie", "").strip()

    for campo, valor in [("Nombre", nombre), ("Torneo", torneo), ("País", pais)]:
        if re.search(r"[(),/=]", valor):
            app.logger.warning(f"Validación fallida: {campo} contiene caracteres no permitidos.")
            flash(f"{campo} contiene caracteres no permitidos ( , ) / = )", "error")
            return redirect(url_for("pistas.new"))

    nueva_pista = Pista(
        nombre=nombre,
        superficie=superficie,
        pais=pais,
        torneo=torneo,
        filename=filename,
        user_id=g.user.id
    )

    try:
        db.session.add(nueva_pista)
        db.session.commit()
        app.logger.info(f"Pista '{nombre}' creada por usuario {g.user.username}")
        cache.delete('total_pistas_count') 
        cache.clear()
        flash("Pista creada correctamente", "success")
        return redirect(url_for("pistas.list"))
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error al crear pista en DB: {str(e)}")
        flash("Error al crear la pista", "error")
        return redirect(url_for("pistas.new"))


@pistas_bp.route("/<int:id>", methods=["GET"])
@load_pista
@cache.memoize(timeout=120)
def show(id, pista):
    if g.user is None or (pista.user_id != g.user.id and g.user.role != 'admin'):
        if g.user is None:
            flash("Debes estar conectado para ver esta pista", "error")
            return redirect(url_for("auth.login"))
        app.logger.warning(f"Acceso no autorizado a pista {id} por usuario {g.user.username}")
        abort(403)
    return render_template("pistas/show.html", pista=pista)

@pistas_bp.route("/<int:id>/edit", methods=["GET"])
@load_pista
@login_required
def edit(id, pista):
    if pista.user_id != g.user.id and g.user.role != 'admin':
        flash("No tienes permisos para editar esta pista", "error")
        abort(403)
    return render_template("pistas/edit.html", pista=pista)

@pistas_bp.route("/<int:id>", methods=["PUT"])
@load_pista
@login_required
@delete_file(resource_name="pista")
@save_file(resource_name="pista")
def update(id, pista):

    if pista.user_id != g.user.id and g.user.role != 'admin':
        flash("No tienes permisos para editar esta pista", "error")
        abort(403)

    nombre = request.form.get("nombre", "").strip()
    torneo = request.form.get("torneo", "").strip()
    pais = request.form.get("pais", "").strip()
    superficie = request.form.get("superficie", "").strip()

    for campo, valor in [("Nombre", nombre), ("Torneo", torneo), ("País", pais)]:
        if re.search(r"[(),/=]", valor):
            flash(f"{campo} contiene caracteres no permitidos ( , ) / = )", "error")
            return redirect(url_for("pistas.edit", id=id))
        
    pista.nombre = nombre
    pista.superficie = superficie
    pista.pais = pais
    pista.torneo = torneo

    try:
        db.session.commit()
        app.logger.info(f"Pista ID {id} actualizada por {g.user.username}")
        cache.delete_memoized(show, id, pista)
        cache.clear()
        flash("Pista editada correctamente", "success")
        return redirect(url_for("pistas.list"))
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error al editar pista {id}: {str(e)}")
        flash("Error al editar la pista", "error")
        return redirect(url_for("pistas.edit", id=id))


@pistas_bp.route("/<int:id>", methods=["DELETE"])
@load_pista
@login_required
@delete_file(resource_name="pista")
def delete(id, pista):

    if pista.user_id != g.user.id and g.user.role != 'admin':
        flash("No tienes permisos para eliminar esta pista", "error")
        abort(403)

    try:
        db.session.delete(pista)
        db.session.commit()
        app.logger.info(f"(ID: {id}) eliminada por {g.user.username}")
        cache.delete('total_pistas_count')
        cache.delete_memoized(show, id, pista)
        cache.clear()
        flash("Pista borrada correctamente", "success")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error al eliminar pista {id}: {str(e)}")
        flash("Error al eliminar la pista", "error")
    
    return redirect(url_for("pistas.list"))