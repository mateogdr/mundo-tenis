from database import db
from models.jugadores import Jugador
from models.usuarios import Usuario

def seedJugadores():
    user = Usuario.query.first()

    jugadores = [
        {"nombre":"Carlos Alcaraz", "nacionalidad":"España", "edad":22, "puntos":13650, "activo":True, "descripcion":"Considerado uno de los talentos más precoces de la historia del tenis.", "filename":None},
        {"nombre":"Jannik Sinner", "nacionalidad":"Italia", "edad":24, "puntos":10300, "activo":True, "descripcion":"El jugador italiano destaca por su increíble potencia de fondo de pista.", "filename":None},
        {"nombre":"Novak Djokovic", "nacionalidad":"Serbia", "edad":38, "puntos":5280, "activo":True, "descripcion":"Considerado por muchos como el mejor de la historia (GOAT).", "filename":None},
        {"nombre":"Rafael Nadal", "nacionalidad":"España", "edad":39, "puntos":0, "activo":False, "descripcion":"Especialista en tierra batida, ha ganado múltiples Roland Garros.", "filename":None},
        {"nombre":"Roger Federer", "nacionalidad":"Suiza", "edad":41, "puntos":2500, "activo":False, "descripcion":"Leyenda del tenis suizo, recientemente retirado.", "filename":None},
        {"nombre":"Stefanos Tsitsipas", "nacionalidad":"Grecia", "edad":24, "puntos":8400, "activo":True, "descripcion":"Jugador griego con un estilo agresivo y elegante.", "filename":None},
        {"nombre":"Alexander Zverev", "nacionalidad":"Alemania", "edad":26, "puntos":6400, "activo":True, "descripcion":"Potente sacador y gran tenista de fondo.", "filename":None},
        {"nombre":"Casper Ruud", "nacionalidad":"Noruega", "edad":24, "puntos":5700, "activo":True, "descripcion":"Especialista en tierra, rápido y consistente.", "filename":None},
        {"nombre":"Daniil Medvedev", "nacionalidad":"Rusia", "edad":27, "puntos":9150, "activo":True, "descripcion":"Tenista ruso, conocido por su resistencia y estrategia.", "filename":None},
        {"nombre":"Felix Auger-Aliassime", "nacionalidad":"Canadá", "edad":22, "puntos":4600, "activo":True, "descripcion":"Joven canadiense con gran proyección y fuerza.", "filename":None},
        {"nombre":"Taylor Fritz", "nacionalidad":"EEUU", "edad":25, "puntos":3800, "activo":True, "descripcion":"Tenista americano con saque potente y buen juego de fondo.", "filename":None},
        {"nombre":"Frances Tiafoe", "nacionalidad":"EEUU", "edad":25, "puntos":3550, "activo":True, "descripcion":"Jugador americano rápido y explosivo en pista dura.", "filename":None}
    ]

    for j in jugadores:

        existente = Jugador.query.filter_by(nombre=j["nombre"]).first()

        if not existente:
            jugador = Jugador(**j, usuario=user)
            db.session.add(jugador)

    db.session.commit()
    print("Jugadores insertados correctamente")