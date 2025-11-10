from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List


# Tablas independientes


class EditorialDB(SQLModel, table=True):
    __tablename__ = "editorial"
    
    id: int = Field(primary_key=True)
    nombre: str = Field(max_length=150)
    calle: str = Field(max_length=150)
    ciudad: Optional[str] = Field(max_length=100, default=None)
    pais: Optional[str] = Field(max_length=100, default=None)
    cp: str = Field(max_length=10)
    
    # Relacion
    libros: List["LibroDB"] = Relationship(back_populates="editorial")



class CategoriaDB(SQLModel, table=True):
    __tablename__ = "categoria"
    
    id: int = Field(primary_key=True)
    nombre: str = Field(max_length=100, unique=True)



class SerieDB(SQLModel, table=True):
    __tablename__ = "serie"
    
    id: int = Field(primary_key=True)
    nombre: str = Field(max_length=150)
    num_libros: Optional[int] = Field(default=1)



class PublicoObjetivoDB(SQLModel, table=True):
    __tablename__ = "publico_objetivo"
    
    id: int = Field(primary_key=True)
    nombre: str = Field(max_length=50, unique=True)



class AutorDB(SQLModel, table=True):
    __tablename__ = "autor"
    
    id: int = Field(primary_key=True)
    nombre: str = Field(max_length=150)
    
    # Relación muchos_a_muchos con libros
    libros: List["LibroDB"] = Relationship(back_populates="autores", link_model="LibroAutorDB")



# Tabla puente para relación muchos-a-muchos
class LibroAutorDB(SQLModel, table=True):
    __tablename__ = "libro_autor"
    
    libro_isbn: str = Field(foreign_key="libro.isbn", primary_key=True)
    autor_id: int = Field(foreign_key="autor.id", primary_key=True)



# Tabla principal
class LibroDB(SQLModel, table=True):
    __tablename__ = "libro"
    
    isbn: str = Field(primary_key=True, max_length=20)
    titulo: str = Field(max_length=200)
    editorial_id: int = Field(foreign_key="editorial.id")
    edicion: str = Field(max_length=50, default=1)
    anio: int = Field(default=None)
    paginas: Optional[int] = Field(default=None)
    categoria_id: int = Field(foreign_key="categoria.id")
    precio: float = Field(default=None)  # NUMERIC(10,2)
    formato: Optional[str] = Field(max_length=20, default=None)  # CHECK constraint
    publico_id: int = Field(foreign_key="publico_objetivo.id")
    serie_id: int = Field(foreign_key="serie.id", default=1)
    num_en_serie: int = Field(default=1)
    portada: Optional[str] = Field(max_length=255, default=None)
    
    # Relaciones
    editorial: Optional[EditorialDB] = Relationship(back_populates="libros")
    autores: List[AutorDB] = Relationship(back_populates="libros", link_model=LibroAutorDB)
