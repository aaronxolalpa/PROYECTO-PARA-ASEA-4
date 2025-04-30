# PROYECTO-PARA-ASEA-4
Este realizado en mi servicio social en ASEA proyecto en Python proporciona una herramienta completa de escritorio, desarrollada con Tkinter, para gestionar archivos PDF escaneados de oficios. Permite visualizar, renombrar, recortar, generar copias de seguridad y organizar documentos según un formato institucional definido.
Funcionalidades principales
Interfaz gráfica completa para procesar archivos PDF de manera visual y estructurada.

Carga automática de archivos desde la carpeta escaneados.

Renombrado automático según dirección general, número de folio y año.

Extracción y recorte de páginas específicas dentro de un PDF.

Copia de seguridad automática antes de cada modificación (carpeta backups).

Restauración de archivos a su estado anterior gracias a los backups generados.

Control de errores y validación de rango de páginas antes del recorte.

Visualización de PDFs con el visor por defecto del sistema.

Registro y advertencia después de cada 10 archivos procesados.

Separación de archivos renombrados en la carpeta renombrados.

Gestión de archivos no PDF y limpieza de carpetas temporales.

Carpetas utilizadas
escaneados: Contiene los archivos PDF originales a procesar.

renombrados: Almacena los archivos con nombre ya estandarizado.

backups: Guarda copias de respaldo automáticas antes de modificaciones.

copia de seguridad: Contiene una copia de todos los archivos de entrada antes de iniciar el procesamiento.
Consideraciones
Los archivos PDF deben estar cerrados antes de ser procesados.

Se pueden recortar rangos de páginas específicos de cada PDF.

El sistema alerta cuando un nombre está duplicado o se intenta sobrescribir un archivo existente.

Se recomienda cerrar pestañas del navegador después de cada 10 archivos procesados para mejorar el rendimiento.
