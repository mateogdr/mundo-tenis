from database import db
from models.usuarios import Usuario

def seedUsuarios():
    usuarios = [
        {"username": "admin", "email": "admin@mundotenis.com", "password": "admin1234", "role": "admin"},
        {"username": "rfederer", "email": "rfederer@mundotenis.com", "password": "suiza_power", "role": "user"},
        {"username": "rafa_fan", "email": "rafa_fan@mundotenis.com", "password": "userpass", "role": "user"},
        {"username": "alcaraz_fan", "email": "alcaraz_fan@mundotenis.com", "password": "esp_power", "role": "user"},
        {"username": "djokovic_fan", "email": "djokovic_fan@mundotenis.com", "password": "serbia123", "role": "user"},
        {"username": "sinner_fan", "email": "sinner_fan@mundotenis.com", "password": "italia123", "role": "user"},
        {"username": "medvedev_fan", "email": "medvedev_fan@mundotenis.com", "password": "rusia123", "role": "user"},
        {"username": "tsitsipas_fan", "email": "tsitsipas_fan@mundotenis.com", "password": "grecia123", "role": "user"},
        {"username": "zverev_fan", "email": "zverev_fan@mundotenis.com", "password": "alemania123", "role": "user"},
        {"username": "fritz_fan", "email": "fritz_fan@mundotenis.com", "password": "eeuu123", "role": "user"},
        {"username": "tiafoe_fan", "email": "tiafoe_fan@mundotenis.com", "password": "eeuu456", "role": "user"}
    ]

    for u in usuarios:

        existente = Usuario.query.filter_by(email=u["email"]).first()

        if not existente:
            usuario = Usuario(
                username=u["username"],
                email=u["email"],
                role=u["role"]
            )
            
            usuario.set_password(u["password"])
            db.session.add(usuario)

    db.session.commit()
    print("Usuarios insertados correctamente")
