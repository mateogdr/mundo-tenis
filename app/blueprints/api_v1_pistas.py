import httpx
from aiocache import cached
from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from database import db
from models.pistas import Pista
from schemas import PistaReadDTO, PistaCreateDTO, PistaUpdateDTO
from extensions import cache

api_v1_pistas_bp = Blueprint('api_v1_pistas', __name__, url_prefix='/api/v1/pistas')

@cached(ttl=600)
async def get_external_weather(ciudad):
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={ciudad}&count=1&language=es&format=json"
    async with httpx.AsyncClient() as client:
        try:
            geo_res = await client.get(geo_url)
            geo_data = geo_res.json()
            
            if not geo_data.get('results'):
                return {"info": "Clima no disponible para esta ubicación"}

            lat = geo_data['results'][0]['latitude']
            lon = geo_data['results'][0]['longitude']

            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            weather_res = await client.get(weather_url)
            w_data = weather_res.json()
            
            return {
                "temperatura": f"{w_data['current_weather']['temperature']}°C",
                "viento": f"{w_data['current_weather']['windspeed']} km/h",
                "proveedor": "Open-Meteo"
            }
        except Exception as e:
            return {"error": "No se pudo conectar con el servicio meteorológico"}
        
    
@api_v1_pistas_bp.route("/", methods=["GET"])
@cache.cached(timeout=60, query_string=True)
def get_all():
    query = Pista.query.all()
    return jsonify([PistaReadDTO.model_validate(p).model_dump() for p in query]), 200

@api_v1_pistas_bp.route("/<int:id>", methods=["GET"])
async def get_one(id):
    pista = Pista.query.get_or_404(id)
    pista_dto = PistaReadDTO.model_validate(pista).model_dump()
    
    clima = await get_external_weather(pista.pais)
    
    pista_dto['clima_externo'] = clima
    
    return jsonify(pista_dto), 200

@api_v1_pistas_bp.route("/", methods=["POST"])
def create():
    try:
        data = request.get_json()
        dto = PistaCreateDTO(**data)
        nueva_pista = Pista(**dto.model_dump())
        db.session.add(nueva_pista)
        db.session.commit()
        cache.clear()
        return jsonify(PistaReadDTO.model_validate(nueva_pista).model_dump()), 201
    except ValidationError as e:
        return jsonify(e.errors()), 400

@api_v1_pistas_bp.route("/<int:id>", methods=["PUT"])
def update(id):
    pista = Pista.query.get_or_404(id)
    try:
        data = request.get_json()
        dto = PistaUpdateDTO(**data)
        for campo, valor in dto.model_dump(exclude_unset=True).items():
            setattr(pista, campo, valor)
        db.session.commit()
        cache.clear()
        return jsonify(PistaReadDTO.model_validate(pista).model_dump()), 200
    except ValidationError as e:
        return jsonify(e.errors()), 400

@api_v1_pistas_bp.route("/<int:id>", methods=["DELETE"])
def delete(id):
    pista = Pista.query.get_or_404(id)
    db.session.delete(pista)
    db.session.commit()
    cache.clear()
    return '', 204