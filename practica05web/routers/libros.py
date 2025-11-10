# routers/libros.py
import os
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models import models
from schemas.schemas import Libro, LibroCreate

router = APIRouter(prefix="/libros", tags=["libros"])

# 📂 Carpeta donde se guardarán las portadas
UPLOAD_DIR = "static/covers"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ======================== LISTAR LIBROS ========================
@router.get("/", response_model=List[Libro])
def listar_libros(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Devuelve hasta 100 libros por página, con soporte para scroll infinito.
    """
    return db.query(models.Libro).offset(skip).limit(limit).all()


# ======================== CREAR LIBRO ========================
@router.post("/", response_model=Libro)
def crear_libro(libro: LibroCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo libro en la base de datos.
    """
    db_libro = models.Libro(**libro.dict())
    db.add(db_libro)
    db.commit()
    db.refresh(db_libro)
    return db_libro


# ======================== SUBIR PORTADA ========================
@router.post("/{isbn}/portada")
async def subir_portada(isbn: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Sube una imagen de portada (archivo) y la asocia con el libro indicado por su ISBN.
    Guarda la imagen en /static/covers/ y actualiza el campo 'portada' en la base de datos.
    """
    libro = db.query(models.Libro).filter(models.Libro.isbn == isbn).first()
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    # crear carpeta si no existe
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # nombre único para el archivo
    filename = f"{isbn}_{file.filename}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    # guardar el archivo
    with open(filepath, "wb") as f:
        f.write(await file.read())

    # actualizar campo en la base de datos
    libro.portada = f"/static/covers/{filename}"
    db.commit()
    db.refresh(libro)

    return {"msg": "Portada subida correctamente", "portada": libro.portada}


# ======================== DETALLE DEL LIBRO ========================
@router.get("/{isbn}/detalle", response_model=Dict[str, Any])
def obtener_detalle_libro(isbn: str, db: Session = Depends(get_db)):
    """
    Devuelve información detallada de un libro:
    título, autores, editorial, año, género, ISBN, formato, precio y más.
    """
    libro = (
        db.query(models.Libro)
        .options(
            joinedload(models.Libro.editorial),
            joinedload(models.Libro.categoria),
            joinedload(models.Libro.autores).joinedload(models.LibroAutor.autor),
        )
        .filter(models.Libro.isbn == isbn)
        .first()
    )

    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    return {
        "isbn": libro.isbn,
        "titulo": libro.titulo,
        "anio": libro.anio,
        "paginas": libro.paginas,
        "precio": float(libro.precio) if libro.precio else None,
        "formato": libro.formato,
        "editorial": libro.editorial.nombre if libro.editorial else None,
        "categoria": libro.categoria.nombre if libro.categoria else None,
        "autores": [rel.autor.nombre for rel in libro.autores],
    }
