from database import db

class Pista(db.Model):
    __tablename__ = "pistas"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    superficie = db.Column(db.String(100), nullable=False)
    pais = db.Column(db.String(100), nullable=False)
    torneo = db.Column(db.String(255), nullable=False)
    filename = db.Column(db.String(120), nullable=True)

    user_id = db.Column(db.String(36), db.ForeignKey("usuario.id"), nullable=False)
    usuario = db.relationship('Usuario', back_populates='pistas')