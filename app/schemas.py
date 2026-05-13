from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

class UsuarioReadDTO(BaseModel):
    id: str
    username: str
    email: str
    role: str

    class Config:
        from_attributes = True

class JugadorBase(BaseModel):
    nombre: str = Field(..., min_length=2)
    nacionalidad: str
    edad: int = Field(..., gt=0)
    puntos: int = Field(..., ge=0)
    activo: bool = True
    descripcion: str
    filename: Optional[str] = None

class JugadorCreateDTO(JugadorBase):
    user_id: str  

class JugadorUpdateDTO(BaseModel):
    nombre: Optional[str] = None
    nacionalidad: Optional[str] = None
    edad: Optional[int] = None
    puntos: Optional[int] = None
    activo: Optional[bool] = None
    descripcion: Optional[str] = None
    filename: Optional[str] = None

class JugadorReadDTO(JugadorBase):
    id: int
    
    class Config:
        from_attributes = True

class PistaBase(BaseModel):
    nombre: str
    superficie: str
    pais: str
    torneo: str
    filename: Optional[str] = None

class PistaCreateDTO(PistaBase):
    user_id: str

class PistaUpdateDTO(BaseModel):
    nombre: Optional[str] = None
    superficie: Optional[str] = None
    pais: Optional[str] = None
    torneo: Optional[str] = None
    filename: Optional[str] = None

class PistaReadDTO(PistaBase):
    id: int
    
    class Config:
        from_attributes = True