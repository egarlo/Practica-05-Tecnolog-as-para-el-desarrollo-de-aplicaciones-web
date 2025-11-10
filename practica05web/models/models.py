# models/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from database import Base

class Editorial(Base):
    __tablename__ = "editorial"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    calle = Column(String(150))
    ciudad = Column(String(100))
    pais = Column(String(100))
    cp = Column(String(10))

    libros = relationship("Libro", back_populates="editorial")


class Categoria(Base):
    __tablename__ = "categoria"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True)

    libros = relationship("Libro", back_populates="categoria")


class Serie(Base):
    __tablename__ = "serie"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    num_libros = Column(Integer)

    libros = relationship("Libro", back_populates="serie")


class PublicoObjetivo(Base):
    __tablename__ = "publico_objetivo"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False, unique=True)

    libros = relationship("Libro", back_populates="publico")


class Autor(Base):
    __tablename__ = "autor"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)

    libros = relationship("LibroAutor", back_populates="autor")


class Libro(Base):
    __tablename__ = "libro"

    isbn = Column(String(20), primary_key=True, index=True)
    titulo = Column(String(200), nullable=False)

    editorial_id = Column(Integer, ForeignKey("editorial.id"))
    edicion = Column(String(50))
    anio = Column(Integer)
    paginas = Column(Integer)
    categoria_id = Column(Integer, ForeignKey("categoria.id"))
    precio = Column(Numeric(10, 2))
    formato = Column(String(20))
    publico_id = Column(Integer, ForeignKey("publico_objetivo.id"))
    serie_id = Column(Integer, ForeignKey("serie.id"))
    num_en_serie = Column(Integer)
    portada = Column(String(255))

    editorial = relationship("Editorial", back_populates="libros")
    categoria = relationship("Categoria", back_populates="libros")
    serie = relationship("Serie", back_populates="libros")
    publico = relationship("PublicoObjetivo", back_populates="libros")

    autores = relationship("LibroAutor", back_populates="libro")


class LibroAutor(Base):
    __tablename__ = "libro_autor"

    libro_isbn = Column(String(20), ForeignKey("libro.isbn"), primary_key=True)
    autor_id = Column(Integer, ForeignKey("autor.id"), primary_key=True)

    libro = relationship("Libro", back_populates="autores")
    autor = relationship("Autor", back_populates="libros")
