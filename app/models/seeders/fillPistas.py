from database import db
from models.pistas import Pista
from models.usuarios import Usuario

def seedPistas():
    user = Usuario.query.first()

    pistas = [
        {"nombre": "Centre Court", "superficie":"Hierba", "pais": "Reino Unido", "torneo":"Wimbledon", "filename": None},
        {"nombre": "Court Philippe-Chatrier", "superficie": "Tierra batida", "pais": "Francia", "torneo": "Roland Garros", "filename": None},
        {"nombre": "Arthur Ashe Stadium", "superficie": "Dura", "pais": "Estados Unidos", "torneo": "US Open", "filename": None},
        {"nombre": "Rod Laver Arena", "superficie": "Dura", "pais": "Australia", "torneo": "Australian Open", "filename": None},
        {"nombre": "Margaret Court Arena", "superficie": "Dura", "pais": "Australia", "torneo": "Australian Open", "filename": None},
        {"nombre": "John Cain Arena", "superficie": "Dura", "pais": "Australia", "torneo": "Australian Open", "filename": None},
        {"nombre": "Court Suzanne-Lenglen", "superficie": "Tierra batida", "pais": "Francia", "torneo": "Roland Garros", "filename": None},
        {"nombre": "Court Simonne-Mathieu", "superficie": "Tierra batida", "pais": "Francia", "torneo": "Roland Garros", "filename": None},
        {"nombre": "Louis Armstrong Stadium", "superficie": "Dura", "pais": "Estados Unidos", "torneo": "US Open", "filename": None},
        {"nombre": "Grandstand Court", "superficie": "Dura", "pais": "Estados Unidos", "torneo": "US Open", "filename": None},
        {"nombre": "Manolo Santana Stadium", "superficie": "Tierra batida", "pais": "España", "torneo": "Mutua Madrid Open", "filename": None},
        {"nombre": "Arantxa Sánchez Stadium", "superficie": "Tierra batida", "pais": "España", "torneo": "Mutua Madrid Open", "filename": None},
        {"nombre": "Pista Rafa Nadal", "superficie": "Tierra batida", "pais": "España", "torneo": "Barcelona Open", "filename": None},
        {"nombre": "Campo Centrale", "superficie": "Tierra batida", "pais": "Italia", "torneo": "Masters de Roma", "filename": None},
        {"nombre": "Stadium 1 Indian Wells", "superficie": "Dura", "pais": "Estados Unidos", "torneo": "Indian Wells", "filename": None}

    ]

    for p in pistas:

        existente = Pista.query.filter_by(nombre=p["nombre"]).first()

        if not existente:
            pista = Pista(**p, usuario=user)
            db.session.add(pista)

    db.session.commit()
    print("Pistas insertadas correctamente")