from database import db
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from enum import Enum

class RoleEnum(Enum):
    admin = "admin"
    user = "user"

class Usuario(db.Model):
    __tablename__ = 'usuario'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), nullable=False, default=RoleEnum.user.value)

    jugadores = db.relationship('Jugador', back_populates='usuario', cascade="all, delete-orphan")
    pistas = db.relationship('Pista', back_populates='usuario', cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def role_enum(self):
        return RoleEnum(self.role)

    @role_enum.setter
    def role_enum(self, value: RoleEnum):
        self.role = value.value