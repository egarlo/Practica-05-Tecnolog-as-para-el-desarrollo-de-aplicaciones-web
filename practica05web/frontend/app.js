const contenedor = document.getElementById('catalogo');
const loading = document.getElementById('loading');

let skip = 0;
const limit = 100;
let cargando = false;
const API_BASE = "http://127.0.0.1:8000";

async function cargarLibros() {
  if (cargando) return;
  cargando = true;
  if (loading) loading.style.display = "block";

  try {
    const res = await fetch(`${API_BASE}/libros?skip=${skip}&limit=${limit}`);
    const data = await res.json();

    if (data.length === 0) {
      if (loading) loading.textContent = "No hay más libros.";
      return;
    }

    data.forEach(libro => {
      const card = document.createElement('div');
      card.className = 'card-libro';

      // 👇 al hacer clic en la tarjeta, mostramos el detalle
      card.addEventListener('click', () => {
        mostrarDetalle(libro.isbn);
      });

      const img = document.createElement('img');

      // detectar cómo viene la portada
      let imgSrc;
      if (libro.portada) {
        if (libro.portada.startsWith("/")) {
          imgSrc = `${API_BASE}${libro.portada}`;
        } else {
          imgSrc = `${API_BASE}/static/covers/${libro.portada}`;
        }
      } else {
        imgSrc = 'https://via.placeholder.com/200x300?text=Sin+Portada';
      }
      img.src = imgSrc;
      card.appendChild(img);

      const info = document.createElement('div');
      info.className = 'info';

      const titulo = document.createElement('div');
      titulo.className = 'titulo';
      titulo.textContent = libro.titulo;
      info.appendChild(titulo);

      const precio = document.createElement('div');
      precio.className = 'precio';
      precio.textContent = libro.precio ? `$${libro.precio}` : '$0.00';
      info.appendChild(precio);

      card.appendChild(info);
      contenedor.appendChild(card);
    });

    skip += limit;
  } catch (err) {
    console.error("Error cargando libros", err);
  } finally {
    cargando = false;
    if (loading) loading.style.display = "none";
  }
}

// primera carga
cargarLibros();

// infinite scroll
window.addEventListener('scroll', () => {
  if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 200) {
    cargarLibros();
  }
});


// ======================
//  DETALLE DEL LIBRO
// ======================
async function mostrarDetalle(isbn) {
  try {
    const res = await fetch(`${API_BASE}/libros/${isbn}/detalle`);
    if (!res.ok) {
      console.error("No se pudo obtener el detalle");
      return;
    }
    const data = await res.json();

    // llenar el modal
    document.getElementById("modalTitulo").textContent = data.titulo;
    document.getElementById("modalAutores").textContent =
      data.autores && data.autores.length > 0 ? data.autores.join(", ") : "—";
    document.getElementById("modalEditorial").textContent = data.editorial || "—";
    document.getElementById("modalAnio").textContent = data.anio || "—";
    document.getElementById("modalIsbn").textContent = data.isbn;

    const tags = document.getElementById("modalEtiquetas");
    tags.innerHTML = "";
    if (data.categoria) {
      const tag = document.createElement("span");
      tag.className = "tag";
      tag.textContent = data.categoria;
      tags.appendChild(tag);
    }

    // mostrar modal
    document.getElementById("modal").classList.remove("hidden");
  } catch (error) {
    console.error("Error al mostrar detalle:", error);
  }
}

// cerrar modal con la X
document.getElementById("cerrarModal").addEventListener("click", () => {
  document.getElementById("modal").classList.add("hidden");
});

// cerrar haciendo clic fuera del contenido
document.getElementById("modal").addEventListener("click", (e) => {
  if (e.target.id === "modal") {
    document.getElementById("modal").classList.add("hidden");
  }
});
