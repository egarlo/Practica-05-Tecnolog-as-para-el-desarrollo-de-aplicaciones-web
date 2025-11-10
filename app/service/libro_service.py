from sqlmodel import Session, select
from typing import List, Optional
from fastapi import HTTPException


# Importar modelos
from app.models.modelos import (
    LibroDB, AutorDB, EditorialDB, CategoriaDB, 
    SerieDB, PublicoObjetivoDB, LibroAutorDB
)


# Importar esquemas
from app.schemas.esquemas import LibroCreate, LibroUpdate


class LibroService:
    def __init__(self, session: Session):
        self.session = session


    # ========== MÉTODOS DE VALIDACIÓN ==========
    
    def _validar_editorial_existe(self, editorial_id: int) -> bool:
        """Verifica que la editorial exista"""
        if editorial_id is None:
            return True
        editorial = self.session.get(EditorialDB, editorial_id)
        return editorial is not None

    def _validar_categoria_existe(self, categoria_id: int) -> bool:
        """Verifica que la categoría exista"""
        if categoria_id is None:
            return True
        categoria = self.session.get(CategoriaDB, categoria_id)
        return categoria is not None

    def _validar_publico_existe(self, publico_id: int) -> bool:
        """Verifica que ese es el nombre de tu público objetivo"""
        if publico_id is None:
            return True
        publico = self.session.get(PublicoObjetivoDB, publico_id)
        return publico is not None

    def _validar_serie_existe(self, serie_id: int) -> bool:
        """Verifica que la serie exista"""
        if serie_id is None:
            return True
        serie = self.session.get(SerieDB, serie_id)
        return serie is not None

    def _validar_autores_existen(self, autores_ids: List[int]) -> bool:
        """Verifica que los autores existan"""
        if not autores_ids:
            return True
        
        for autor_id in autores_ids:
            autor = self.session.get(AutorDB, autor_id)
            if autor is None:
                return False
        return True



    # ========== MÉTODOS PRINCIPALES CRUD ==========

    def crear_libro(self, libro_data: LibroCreate) -> LibroDB:
        """Crea un nuevo libro junto a sus autores"""
        
        
	# Validar que el ISBN no exista
        libro_existente = self.session.get(LibroDB, libro_data.isbn)
        if libro_existente:
            raise HTTPException(
                status_code=400, 
                detail=f"El libro con ISBN {libro_data.isbn} ya existe"
            )

        
	# Validar que las relaciones existan
        if not self._validar_editorial_existe(libro_data.editorial_id):
            raise HTTPException(status_code=400, detail="La editorial no existe")

        if not self._validar_categoria_existe(libro_data.categoria_id):
            raise HTTPException(status_code=400, detail="La categoría no existe")

        if not self._validar_publico_existe(libro_data.publico_id):
            raise HTTPException(status_code=400, detail="Ese nombre de público objetivo no existe")

        if not self._validar_serie_existe(libro_data.serie_id):
            raise HTTPException(status_code=400, detail="Ña serie no existe")

        if not self._validar_autores_existen(libro_data.autores_ids):
            raise HTTPException(status_code=400, detail="Uno o más autores no existen")

        
	# Crear el libro
        libro_dict = libro_data.dict(exclude={'autores_ids'})
        nuevo_libro = LibroDB(**libro_dict)
        
        self.session.add(nuevo_libro)
        self.session.commit()
        self.session.refresh(nuevo_libro)


        # Agregar relaciones con autores (tabla puente)
        for autor_id in libro_data.autores_ids:
            relacion = LibroAutorDB(libro_isbn=libro_data.isbn, autor_id=autor_id)
            self.session.add(relacion)
        
        self.session.commit()

        return nuevo_libro

    
    def obtener_libro_por_isbn(self, isbn: str) -> Optional[LibroDB]:
        """Obtiene un libro por su ISBN"""
        return self.session.get(LibroDB, isbn)

    def obtener_todos_libros(self) -> List[LibroDB]:
        """Obtiene todos los libros"""
        statement = select(LibroDB)
        return self.session.exec(statement).all()

    def buscar_libros_por_titulo(self, titulo: str) -> List[LibroDB]:
        """Busca los libros por su título (búsqueda parcial)"""
        statement = select(LibroDB).where(LibroDB.titulo.ilike(f"%{titulo}%"))
        return self.session.exec(statement).all()

    def buscar_libros_por_autor(self, autor_id: int) -> List[LibroDB]:
        """Busca los libros su por autor"""
        statement = select(LibroDB).join(LibroAutorDB).where(LibroAutorDB.autor_id == autor_id)
        return self.session.exec(statement).all()

    def actualizar_libro(self, isbn: str, libro_data: LibroUpdate) -> Optional[LibroDB]:
        """Actualiza un libro existente"""
        libro = self.session.get(LibroDB, isbn)
        if not libro:
            raise HTTPException(status_code=404, detail="Libro no encontrado")


        # Actualizar solo los campos proporcionados
        update_data = libro_data.dict(exclude_unset=True)
        
        # Si tiene autores_ids, actualizar la relación
        autores_ids = update_data.pop('autores_ids', None)
        
        for field, value in update_data.items():
            setattr(libro, field, value)

        # Actualizar autores si se proporcionaron
        if autores_ids is not None:

            # Eliminar las relaciones existentes
            statement = select(LibroAutorDB).where(LibroAutorDB.libro_isbn == isbn)
            relaciones_existentes = self.session.exec(statement).all()
            for rel in relaciones_existentes:
                self.session.delete(rel)
            
            # Crear nuevas relaciones
            for autor_id in autores_ids:
                nueva_relacion = LibroAutorDB(libro_isbn=isbn, autor_id=autor_id)
                self.session.add(nueva_relacion)

        self.session.add(libro)
        self.session.commit()
        self.session.refresh(libro)
        
        return libro

    def eliminar_libro(self, isbn: str) -> bool:
        """Elimina un libro por su ISBN"""
        libro = self.session.get(LibroDB, isbn)
        if not libro:
            raise HTTPException(status_code=404, detail="Libro no encontrado")
        
        self.session.delete(libro)
        self.session.commit()
        return True


    # ========== MÉTODOS DE CONSULTA AVANZADA ==========

    def obtener_libros_por_categoria(self, categoria_id: int) -> List[LibroDB]:
        """Obtiene libros por su categoría"""
        statement = select(LibroDB).where(LibroDB.categoria_id == categoria_id)
        return self.session.exec(statement).all()

    def obtener_libros_por_editorial(self, editorial_id: int) -> List[LibroDB]:
        """Obtiene libros por su editorial"""
        statement = select(LibroDB).where(LibroDB.editorial_id == editorial_id)
        return self.session.exec(statement).all()

    def obtener_libros_por_formato(self, formato: str) -> List[LibroDB]:
        """Obtiene libros por su formato (FISICO/DIGITAL)"""
        statement = select(LibroDB).where(LibroDB.formato == formato.upper())
        return self.session.exec(statement).all()

    def obtener_libros_por_rango_precio(self, precio_min: float, precio_max: float) -> List[LibroDB]:
        """Obtiene libros por rango de precio"""
        statement = select(LibroDB).where(
            LibroDB.precio >= precio_min, 
            LibroDB.precio <= precio_max
        )
        return self.session.exec(statement).all()
