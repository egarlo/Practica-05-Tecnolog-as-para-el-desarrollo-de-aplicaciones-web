# schemas/schemas.py
from pydantic import BaseModel
from typing import List, Optional

class LibroBase(BaseModel):
    isbn: str
    titulo: str
    editorial_id: Optional[int] = None
    edicion: Optional[str] = None
    anio: Optional[int] = None
    paginas: Optional[int] = None
    categoria_id: Optional[int] = None
    precio: Optional[float] = None
    formato: Optional[str] = None
    publico_id: Optional[int] = None
    serie_id: Optional[int] = None
    num_en_serie: Optional[int] = None
    portada: Optional[str] = None

class LibroCreate(LibroBase):
    pass

class Libro(LibroBase):
    class Config:
        from_attributes = True
