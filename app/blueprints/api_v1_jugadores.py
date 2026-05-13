from flask import Blueprint, request, jsonify, current_app as app
from pydantic import ValidationError
from database import db
from models.jugadores import Jugador
from schemas import JugadorReadDTO, JugadorCreateDTO, JugadorUpdateDTO
from extensions import cache
from handle_files import save_file, delete_file

api_v1_jugadores_bp = Blueprint('api_v1_jugadores', __name__, url_prefix='/api/v1/jugadores')

@api_v1_jugadores_bp.route("/", methods=["GET"])
@cache.cached(timeout=60, query_string=True)
def get_all():
    app.logger.info("API: Cargando lista de jugadores")
    query = Jugador.query.all()
    resultado = [JugadorReadDTO.model_validate(j).model_dump() for j in query]
    return jsonify(resultado), 200

@api_v1_jugadores_bp.route("/<int:id>", methods=["GET"])
def get_one(id):
    jugador = Jugador.query.get_or_404(id)
    return jsonify(JugadorReadDTO.model_validate(jugador).model_dump()), 200

@api_v1_jugadores_bp.route("/", methods=["POST"])
@save_file(resource_name=None) 
def create(filename=None):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No se recibió contenido JSON"}), 400
    
    try:
        dto = JugadorCreateDTO(**data)
        
        nuevo_jugador = Jugador(
            nombre=dto.nombre,
            nacionalidad=dto.nacionalidad,
            edad=dto.edad,
            puntos=dto.puntos,
            activo=dto.activo,
            descripcion=dto.descripcion,
            filename=filename, 
            user_id=dto.user_id
        )
        
        db.session.add(nuevo_jugador)
        db.session.commit()
        
        cache.clear()
        
        return jsonify(JugadorReadDTO.model_validate(nuevo_jugador).model_dump()), 201
    
    except ValidationError as e:
        return jsonify(e.errors()), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@api_v1_jugadores_bp.route("/<int:id>", methods=["PUT"])
@delete_file(resource_name="jugador") 
@save_file(resource_name="jugador")
def update(id, filename=None):
    jugador = Jugador.query.get_or_404(id)
    data = request.get_json()
    
    try:
        dto = JugadorUpdateDTO(**data)
        datos_actualizados = dto.model_dump(exclude_unset=True)
        
        for campo, valor in datos_actualizados.items():
            setattr(jugador, campo, valor)
        
        if filename:
            jugador.filename = filename
            
        db.session.commit()
        cache.clear()
        
        return jsonify(JugadorReadDTO.model_validate(jugador).model_dump()), 200
    
    except ValidationError as e:
        return jsonify(e.errors()), 400

@api_v1_jugadores_bp.route("/<int:id>", methods=["DELETE"])
@delete_file(resource_name="jugador")
def delete(id):
    jugador = Jugador.query.get_or_404(id)
    try:
        db.session.delete(jugador)
        db.session.commit()
        cache.clear()
        return '', 204 
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500