from database import db

class Jugador(db.Model):
    __tablename__ = "jugadores"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    nacionalidad = db.Column(db.String(100), nullable=False)
    edad = db.Column(db.Integer, nullable=False)
    puntos = db.Column(db.Integer, nullable=False)
    activo = db.Column(db.Boolean, default=True)
    descripcion = db.Column(db.Text, nullable=False)
    filename = db.Column(db.String(120), nullable=True)

    user_id = db.Column(db.String(36), db.ForeignKey("usuario.id"), nullable=False)
    usuario = db.relationship('Usuario', back_populates='jugadores')
