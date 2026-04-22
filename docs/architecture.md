# Arquitectura

- **UI (`src/ui`)**: solo presentación y eventos. El orden de unión se controla en la lista visual (Subir/Bajar) y la vista de división permite elegir entre rango, número de partes o extracción de múltiples rangos, habilitando solo los campos del modo activo.
- **Services (`src/services`)**: casos de uso de negocio (`PDFService`, `FileService`, `ViewerService`). `PDFService.merge_pdfs` respeta el orden recibido y `PDFService` concentra la lógica de división/extracción/conversión (rango, por partes, rangos múltiples, texto+imágenes y PDF->Word rápida/avanzada con motor pdf2docx y fallback estructurado).
- **Adapters (`src/adapters`)**: acceso a librerías externas, filesystem y SO (`PDFAdapter`, `FileAdapter`, `SystemAdapter`).
- **Core (`src/core`)**: configuración transversal.
