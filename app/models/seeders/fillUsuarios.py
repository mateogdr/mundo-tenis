from database import db
from models.usuarios import Usuario

def seedUsuarios():
    usuarios = [
        {"username": "mateo_admin", "email": "mateo.garridodelrio@alumnos.upm.es", "password": "password123", "role": "admin"},
        {"username": "rfederer", "email": "roger@atp.com", "password": "suiza_power", "role": "user"},
        {"username": "rafa_fan", "email": "vamosrafa@gmail.com", "password": "userpass", "role": "user"},
        {"username": "alcaraz_fan", "email": "carlosfan@gmail.com", "password": "esp_power", "role": "user"},
        {"username": "djokovic_fan", "email": "novakfan@gmail.com", "password": "serbia123", "role": "user"},
        {"username": "sinner_fan", "email": "jannikfan@gmail.com", "password": "italia123", "role": "user"},
        {"username": "medvedev_fan", "email": "daniilfan@gmail.com", "password": "rusia123", "role": "user"},
        {"username": "tsitsipas_fan", "email": "stefanosfan@gmail.com", "password": "grecia123", "role": "user"},
        {"username": "zverev_fan", "email": "alexfan@gmail.com", "password": "alemania123", "role": "user"},
        {"username": "fritz_fan", "email": "taylorfan@gmail.com", "password": "eeuu123", "role": "user"},
        {"username": "tiafoe_fan", "email": "francesfan@gmail.com", "password": "eeuu456", "role": "user"}
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