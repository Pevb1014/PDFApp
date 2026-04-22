# PDF Processor Desktop (Python)

Aplicación de escritorio para procesar PDFs con arquitectura limpia, modular y escalable.

## Stack
- Python 3.11+
- UI: Tkinter (incluido en Python, facilita empaquetado `.exe`)
- Manipulación PDF: `pypdf`

## Estructura
Se implementa una estructura principal escalable en `src/` (recomendada para crecimiento) y se incluyen rutas espejo compatibles con la estructura solicitada `project/`.

```text
src/
  core/        -> configuración y reglas base
  services/    -> casos de uso (merge, split, extract)
  adapters/    -> integración con filesystem y pypdf
  ui/          -> interfaz Tkinter
  utils/       -> helpers reutilizables
main.py        -> punto de entrada

project/       -> wrappers de compatibilidad con estructura pedida
ui/services/core/utils -> wrappers ligeros de compatibilidad

tests/         -> pruebas
config/        -> ejemplos de configuración
scripts/       -> automatización
docs/          -> documentación adicional
data/          -> datos de trabajo
assets/        -> recursos estáticos
```

## Instalación
```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecución
```bash
python main.py
```

## Empaquetado a `.exe` con PyInstaller
1. Instala PyInstaller:
```bash
pip install pyinstaller
```
2. Genera ejecutable standalone:
```bash
pyinstaller --noconfirm --clean --onefile --windowed --name PDFProcessor main.py
```
3. El ejecutable quedará en:
- `dist/PDFProcessor.exe`

### Notas para evitar errores comunes de rutas
- Usa rutas absolutas derivadas del runtime cuando agregues assets/binarios (ejemplo: íconos, OCR).
- Mantén el acceso a recursos centralizado en `src/core/config.py`.
- Si agregas dependencias nativas (OCR/firmas), declara `--add-data` y/o `--hidden-import` en PyInstaller.
- Para extracción de imágenes, incluye Pillow en el build (ya está en `requirements.txt`).

## MVP implementado
- **Interfaz Moderna**: UI renovada con estilos personalizados, iconos y disposición mejorada.
- **Procesamiento por Lotes**: Extraer contenido o convertir a Word múltiples PDFs simultáneamente.
- **Conversión Inversa**: Convertir uno o varios archivos Word (.docx) a PDF.
- **Edición de PDF**: Reemplazar texto existente, agregar contenido y añadir firma visible (texto e imagen opcional).
- Cargar uno o múltiples PDFs.
- Listado de PDFs cargados.
- Reordenar manualmente la lista (Subir/Bajar) para decidir un orden exacto de unión.
- Visualizar un PDF seleccionado en el visor por defecto del sistema.
- Unir PDFs en un solo archivo respetando el orden manual de la lista.
- Dividir PDF por rango, por número de partes o por extracción de múltiples rangos.
- Extraer contenido: solo texto, texto + imágenes, o convertir a Word (.docx).
- Guardar resultados en ubicación elegida.

## Escalabilidad (sin romper arquitectura)
- **OCR**: crear `src/adapters/ocr_adapter.py` + caso de uso en `src/services/ocr_service.py`; UI solo invoca servicio.
- **Compresión**: agregar `compress_pdf` en `PDFService` y aislar detalles técnicos en adapter.
- **Conversión a Word/imágenes**: nuevos adapters por tecnología externa, servicios orquestan flujo.
- **Firma digital / password**: nuevos métodos en `PDFService` o servicios específicos; mantener UI desacoplada.

## Testing
```bash
python -m pytest -q
```


## Uso rápido para unión con orden personalizado
1. Carga varios PDFs con **Cargar PDFs**.
2. Selecciona un archivo y usa **Subir ↑ / Bajar ↓** para acomodar el orden exacto que quieras.
3. Pulsa **Unir**; el resultado conserva exactamente ese orden.


## División de PDF: rango o número de partes
1. Selecciona un PDF cargado.
2. Pulsa **Dividir**.
3. Elige una opción:
   - **Dividir por rango**: inicio/fin (opcional, por defecto 1 y última).
   - **Dividir por número de partes**: valor entre `1` y el total de páginas.
4. Selecciona carpeta de salida.

Regla de distribución por partes:
- Se reparten las páginas de forma equitativa.
- Si sobran páginas, se añaden de una en una empezando por las primeras partes.
- Ejemplo: 9 páginas en 2 partes => 5 y 4 páginas.


## Extracción de múltiples rangos
Desde el botón **Dividir** ahora tienes la modalidad **Extraer rangos**.

Formato de entrada:
- Ejemplo: `2-14, 16-18, 20-29`
- Cada rango crea un PDF independiente.

Reglas y validaciones:
- Los rangos deben estar dentro del total de páginas del documento.
- No se permite inicio mayor que fin.
- No se permiten rangos solapados ni repetidos en la misma operación.
- Se toleran espacios en la entrada (ejemplo: `2-14, 16-18`).


## Usabilidad en diálogo de división
- El selector de modo es exclusivo (radio buttons).
- Solo los campos del modo activo quedan habilitados.
- Los campos de modos inactivos se deshabilitan y se limpian automáticamente para evitar conflictos.


## Extraer contenido / Convertir PDF
La acción de extracción ahora ofrece 3 modos exclusivos:
1. **Extraer solo texto** → genera `.txt`.
2. **Extraer texto + imágenes** → crea carpeta organizada con texto y subcarpeta `images/`.
3. **Conversión rápida** → método simple (texto/imagenes básicas).
4. **Conversión avanzada (recomendada)** → usa `pdf2docx` como motor principal para mejor layout.

Notas:
- Si el PDF no contiene texto extraíble (ej. escaneado sin OCR), el resultado de texto puede quedar vacío y en Word se añade una nota informativa.
- En todos los modos, el usuario elige la ubicación de salida.


### Pillow (dependencia para imágenes)
- La extracción de imágenes requiere **Pillow**.
- Si falta, la app muestra un mensaje amigable en UI y evita caída.
- Instalar manualmente (si aplica): `pip install pillow`


### Conversión Word estructurada
La modalidad estructurada prioriza legibilidad y estructura:
- Usa **PyMuPDF (fitz)** para extraer bloques con posición.
- Usa **pdfplumber** para detección de tablas cuando es posible.
- Construye el `.docx` con **python-docx** (texto, tablas, imágenes y links).
- Si el PDF es complejo o falta alguna librería, aplica fallback a `pdf2docx` y luego a conversión rápida.

Limitación: no todos los PDFs pueden replicarse al 100%; se prioriza estructura útil sobre diseño exacto.


### Estrategia profesional de conversión Word
- La modalidad avanzada usa como **motor principal `pdf2docx`**.
- Si falla (PDF complejo/corrupto), aplica fallback automático a conversión estructurada con PyMuPDF + python-docx.
- Si aún falla, se usa la conversión rápida para no bloquear al usuario.
- En PDFs escaneados (sin capa de texto) se muestra aviso de que puede requerir OCR para resultados óptimos.


### Post-procesado de imágenes en Word
Después de convertir con `pdf2docx`, la app aplica limpieza de layout:
- Fuerza flujo vertical legible (separación visual antes/después de imágenes).
- Evita superposición texto/imagen moviendo imágenes a párrafos dedicados cuando es necesario.
- Ajusta automáticamente imágenes grandes al ancho máximo aproximado de página (~6 in), manteniendo proporción.


## Edición y firma de PDF
La app incluye un editor de escritorio avanzado (PyQt6 + PyMuPDF) accesible desde **"✍️ Editar / Firmar PDF"**:

1. `replace`: reemplaza un texto por otro en todo el documento.
2. `add`: agrega texto directamente donde haces click en la vista del PDF.
3. `edit_click`: reemplaza la palabra ubicada en la posición clicada.
4. `image`: inserta una imagen en la posición clicada.
5. `sign`: añade firma visible (texto + imagen opcional) justo en la posición clicada.

Características principales del editor:
- Renderizado visual de página PDF en lienzo desplazable.
- Modos visibles en UI: **Agregar texto nuevo**, **Insertar imagen**, **Firmar documento**.
- `Agregar texto nuevo`: inserta texto como superposición y luego puedes moverlo visualmente.
- `Insertar imagen`: añade imágenes al PDF como overlay, con arrastre y redimensión.
- `Firmar documento`: firma por texto, imagen PNG o dibujo a mano alzada, con reposicionamiento por arrastre.
- Las superposiciones se pueden arrastrar con click sostenido para ajustar posición.
- Doble click sobre un texto agregado para editar su contenido nuevamente.
- Doble click sobre una imagen para reemplazarla por otra.
- Redimensiona imágenes usando la rueda del mouse sobre la imagen.
- Si en la edición de doble click dejas el texto vacío y aceptas, el overlay se elimina.
- El tipo de letra, tamaño y color de la barra se aplican también al re-editar textos existentes.
- Desde el botón **Instrucciones** en la barra del editor puedes ver una guía rápida de uso.
- Sistema de capas por superposiciones (sin modificar directamente el contenido original).
- Exportación reconstruyendo PDF base + overlays.

Notas:
- La edición genera un PDF nuevo (no sobrescribe el original automáticamente).
- Para firma con imagen se aceptan formatos comunes (`.png`, `.jpg`, `.jpeg`, `.bmp`).
