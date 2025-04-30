from tkinter import *
from tkinter import ttk
import tkinter as tk
import os
from datetime import datetime
import webbrowser
import PyPDF2
from PyPDF2 import PdfReader, PdfWriter
import shutil
import subprocess
from tkinter import messagebox


# Rutas de carpeta
ruta_actual = os.getcwd()

entregados = r'escaneados'
copiados = r'renombrados'
backups = r'backups'  
copia_seguridad = r'copia de seguridad'

# Listas
Archivo = []
Renombrado = []

# Variables
Actual = 0
content = ""
ini_pdf = ""
year = 0
totalPages = 0
ultima_operacion = None  # Para guardar información sobre la última operación
ultimo_backup = None  # Para almacenar la ruta del último backup creado
archivos_procesados = 0  # Contador para archivos procesados
#funcion crear copia de seguridad 
def crear_copia_seguridad():
    try:
        # crea carpeta copia de seguridad si no existe 
        if not os.path.exists(copia_seguridad):
            os.makedirs(copia_seguridad)
        
        # checa si escaneados tiene archivos
        if not os.path.exists(entregados):
            messagebox.showinfo("Información", "La carpeta de escaneados no existe.")
            return
        
    
        for filename in os.listdir(copia_seguridad):
            file_path = os.path.join(copia_seguridad, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Error al eliminar archivo anterior: {str(e)}")
        
        # copia archivos en copia de seguridad
        files_copied = 0
        for filename in os.listdir(entregados):
            source_file = os.path.join(entregados, filename)
            dest_file = os.path.join(copia_seguridad, filename)
            
            if os.path.isfile(source_file):
                shutil.copy2(source_file, dest_file)
                files_copied += 1
        
      
        if files_copied > 0:
            messagebox.showinfo("Copia de Seguridad", 
                               f"Se han copiado {files_copied} archivos a Copia de Seguridad")
        else:
            messagebox.showinfo("Copia de Seguridad", 
                               "No hay archivos para copiar en la carpeta de escaneados")
    
    except Exception as e:
        messagebox.showerror("Error", f"Error al crear copia de seguridad: {str(e)}")


# Función para limpiar carpetas
def limpiar_carpetas():
    carpetas = [entregados, copiados, backups,copia_seguridad]
    archivos_encontrados = False
    
    # Verificar si hay archivos en las carpetas
    for carpeta in carpetas:
        if os.path.exists(carpeta) and os.listdir(carpeta):
            archivos_encontrados = True
            break
    
    # Si hay archivos, preguntar al usuario
    if archivos_encontrados:
        respuesta = messagebox.askyesno("Limpiar carpetas", 
                                       "Se han encontrado archivos en las carpetas. ¿Desea limpiarlas?")
        
        if respuesta:
            # Limpiar cada carpeta
            carpetas_limpiadas = []
            carpetas_con_error = []
            
            for carpeta in carpetas:
                if os.path.exists(carpeta):
                    try:
                        for filename in os.listdir(carpeta):
                            file_path = os.path.join(carpeta, filename)
                            if os.path.isfile(file_path) or os.path.islink(file_path):
                                os.unlink(file_path)
                            elif os.path.isdir(file_path):
                                shutil.rmtree(file_path)
                        carpetas_limpiadas.append(carpeta)
                    except Exception as e:
                        carpetas_con_error.append((carpeta, str(e)))
            
            # Mostrar mensaje de confirmación
            if carpetas_limpiadas:
                
                messagebox.showinfo("Limpieza completada", "Limpieza de las carpetas completada")
            
            # Mostrar errores si los hay
            if carpetas_con_error:
                mensaje_errores = "Errores al limpiar:\n" + "\n".join([f"{carpeta}: {error}" for carpeta, error in carpetas_con_error])
                messagebox.showerror("Errores de limpieza", mensaje_errores)

# Extraer los nombres de los archivos
def escaneados():
    
    result_generator = os.walk(entregados)
    files_result = [x for x in result_generator]


    for folder, dir_list, file_list in files_result:
        # Obtener los nombres de cada archivo
        Archivo.extend([os.path.join(file) for file in file_list])

    global Actual
    Actual = 1

# Funcion para el valor seleccionado en el combobox
def on_select(event):
    global ini_pdf
    dg = selected_value.get()
    if dg == 'DGGC':
        ini_pdf = "ASEA_UGSIVC_DGGC_"

    elif dg == 'DGGOI':
        ini_pdf = "ASEA_UGI_DGGOI_"

    elif dg == 'DGGPI':
        ini_pdf = "ASEA_UGI_DGGPI_"

    elif dg == 'DGGEERC':
        ini_pdf = "ASEA_UGI_DGGEERC_"

    elif dg == 'DGGEERNCM':
        ini_pdf = "ASEA_UGI_DDGGEERNCM_"
    
    elif dg == 'DGGEERNCT':
        ini_pdf = "ASEA_UGI_DGGEERNCT_"

    elif dg == 'UGI':
        ini_pdf = "ASEA_UGI_"

    Inicio.set(ini_pdf)

def oficio_capturado(var):
    global content
    content= var.get()
    Inicio.set(ini_pdf + content + "_" + str(year) + ".pdf")

def ano_ingresado(ano_1):
    global year
    captura= ano_1.get()
    year = captura
    Inicio.set(ini_pdf + str(content) + "_" + str(captura) + ".pdf")

def renombrar():
    global Actual, archivos_procesados
    rep = 0

    # Extraer los nombres de los archivos renombrados
    result_generator = os.walk(copiados)
    files_result = [x for x in result_generator]

    for folder, dir_list, file_list in files_result:
        # Obtener los nombres de cada archivo
        Renombrado.extend([os.path.join(file) for file in file_list])


        leyenda = str(len(Archivo)) + " de " + str(len(Archivo))
        Conteo.config(text=leyenda)
        # llamar al pdf actual
        n = Actual
        anterior = os.path.join(entregados, Archivo[n-1])

        n_nombre = Nuevo_Nombre.get()
        nuevo_1 = os.path.join(copiados, n_nombre)

        # verificar si el nuevo nombre contiene .pdf
        if nuevo_1.find(".pdf") == -1:
            nuevo = nuevo_1 + ".pdf"
        else:
            nuevo = nuevo_1
        
        # verificar que no se repita el nombre
        for x in Renombrado:
            if os.path.join(copiados, x) == nuevo:
                rep = rep + 1

        if rep < 1 and var.get() != "Repetido":
            # copiar el archivo con un nuevo nombre a la carpeta de renombrados
            shutil.copyfile(anterior, nuevo)

            # Incrementar contador de archivos procesados
            archivos_procesados += 1
            
            # Verificar si se han procesado 10 archivos
            if archivos_procesados % 10 == 0:
                messagebox.showwarning("Muchas pestañas abiertas", 
                                    "Has procesado 10 archivos. Se recomienda cerrar las pestañas del navegador para mejorar el rendimiento.")

            # moverse al siguiente pdf en la lista Archivo
            Actual = n + 1

            # llamar rutinas
            cuenta()
            abrir_pdf()

            # repetir inicio del folio
            folio_uno = var.get()
            var.set(folio_uno[0:len(folio_uno)-1])
            #var.set("")
            

        else:
            var.set("Repetido")

# Función para eliminar backups anteriores del mismo archivo
def eliminar_backup_anterior(nombre_base):
    if not os.path.exists(backups):
        return
        
    # Buscar backups anteriores con el mismo nombre base
    for filename in os.listdir(backups):
        if filename.startswith(nombre_base + "_") and filename.endswith(".pdf"):
            try:
                os.remove(os.path.join(backups, filename))
            except Exception as e:
                print(f"Error al eliminar backup anterior: {str(e)}")

# Función para crear un backup del archivo original antes de modificarlo
def crear_backup(archivo_origen):
    global ultimo_backup
    
    # Asegurarse de que la carpeta de backups existe
    if not os.path.exists(backups):
        os.makedirs(backups)
    
    # Obtener el nombre base del archivo (sin extensión)
    nombre_archivo = os.path.basename(archivo_origen)
    nombre_base = os.path.splitext(nombre_archivo)[0]
    
    # Eliminar backups anteriores del mismo archivo
    eliminar_backup_anterior(nombre_base)
    
    # Crear nombre para el nuevo backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_nombre = f"{nombre_base}_{timestamp}.pdf"
    backup_ruta = os.path.join(backups, backup_nombre)
    
    # Copiar el archivo original al backup
    shutil.copy2(archivo_origen, backup_ruta)
    
    # Guardar la referencia al último backup creado
    ultimo_backup = backup_ruta
    
    return backup_ruta

# función para recortar el PDF según el rango de páginas seleccionado
def recortar_pdf():
    try:
        global Actual, ultima_operacion, totalPages, archivos_procesados
        
        # Verificar que haya archivos para procesar
        if len(Archivo) == 0 or Actual > len(Archivo):
            messagebox.showerror("Error", "No hay archivos para recortar")
            return
        
        # Obtener el PDF actual
        n = Actual
        archivo_original = os.path.join(entregados, Archivo[n-1])
        
        # Verificar si el archivo está abierto
        try:
            # Intentar abrir el archivo en modo exclusivo
            with open(archivo_original, 'rb+') as file:
                pass
        except PermissionError:
            # Si no se puede abrir, significa que está en uso
            messagebox.showerror("Error", "El archivo PDF está abierto. Por favor, ciérrelo antes de recortar.")
            return
        
        # Obtener el nombre del nuevo archivo
        nuevo_nombre = Nuevo_Nombre.get()
        if not nuevo_nombre:
            messagebox.showerror("Error", "Debe generar un nombre para el archivo")
            return
            
        # Verificar si el nombre contiene .pdf
        if nuevo_nombre.find(".pdf") == -1:
            nuevo_nombre = nuevo_nombre + ".pdf"
            
        nuevo_archivo = os.path.join(copiados, nuevo_nombre)
        
        # Verificar que no exista un archivo con ese nombre
        if os.path.exists(nuevo_archivo):
            respuesta = messagebox.askyesno("Archivo existente", 
                                           f"El archivo {nuevo_nombre} ya existe. ¿Desea reemplazarlo?")
            if not respuesta:
                return
        
        # Obtener las páginas a extraer
        try:
            pagina_inicio_val = int(pagina_inicio.get())
            pagina_fin_val = int(pagina_fin.get())
        except ValueError:
            messagebox.showerror("Error", "Los números de página deben ser valores numéricos")
            return
            
        # Validar el rango de páginas
        if pagina_inicio_val < 1 or pagina_fin_val > totalPages or pagina_inicio_val > pagina_fin_val:
            messagebox.showerror("Error", f"El rango de páginas debe estar entre 1 y {totalPages}")
            return
        
        # Crear backup del archivo original antes de modificarlo
        backup_ruta = crear_backup(archivo_original)
            
        # Abrir el PDF original
        with open(archivo_original, 'rb') as input_file:
            pdf_reader = PyPDF2.PdfReader(input_file)
            
            # Writer para el archivo recortado que contendrá solo las páginas seleccionadas
            pdf_writer_recorte = PyPDF2.PdfWriter()
            
            # Writer para el archivo original modificado que contendrá todas las páginas excepto las seleccionadas
            pdf_writer_original = PyPDF2.PdfWriter()
            
            # Procesar cada página - corregido para manejar correctamente la última página
            for i in range(len(pdf_reader.pages)):
                # Convertir a índice base-0 (las páginas en PyPDF2 comienzan en 0, pero para el usuario comienzan en 1)
                if pagina_inicio_val - 1 <= i <= pagina_fin_val - 1:
                    # Añadir las páginas seleccionadas al archivo recortado
                    pdf_writer_recorte.add_page(pdf_reader.pages[i])
                else:
                    # Añadir las páginas no seleccionadas al archivo original modificado
                    pdf_writer_original.add_page(pdf_reader.pages[i])
            
            # Verificar si se extrajeron páginas
            if pdf_writer_recorte.pages:  # Verifica que hay páginas en el archivo recortado
                # Guardar el nuevo PDF recortado
                with open(nuevo_archivo, 'wb') as output_file:
                    pdf_writer_recorte.write(output_file)
                
                # Verificar si el original debe mantenerse o modificarse
                if pdf_writer_original.pages:  # Hay páginas restantes
                    with open(archivo_original, 'wb') as output_file:
                        pdf_writer_original.write(output_file)
                else:
                    # Si se seleccionaron todas las páginas, mantener una copia en la carpeta original
                    shutil.copy2(nuevo_archivo, archivo_original)
            else:
                messagebox.showerror("Error", "No se pudieron extraer páginas del PDF")
                return
        
            # Guardar información sobre la última operación para poder revertirla
            ultima_operacion = {
                'archivo_original': archivo_original,
                'backup': backup_ruta,
                'paginas_recortadas': (pagina_inicio_val, pagina_fin_val),
                'archivo_recortado': nuevo_archivo
            }
            
            # Mostrar botón de restaurar ya que ahora hay una operación para revertir
            btn_restaurar.config(state=tk.NORMAL)
            
            # Actualizar la lista de archivos renombrados
            if nuevo_nombre not in Renombrado:
                Renombrado.append(nuevo_nombre)
    
            # Incrementar contador de archivos procesados
            archivos_procesados += 1
            
            # Verificar si se han procesado 10 archivos
            if archivos_procesados % 10 == 0:
                messagebox.showwarning("Muchas pestañas abiertas", 
                                    "Has procesado 10 archivos. Se recomienda cerrar las pestañas del navegador para mejorar el rendimiento.")
            
            # Abrir el PDF original después de recortar
            webbrowser.open_new(archivo_original)
            
            # Actualizar la información de páginas en el archivo original
            with open(archivo_original, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                totalPages = len(pdf_reader.pages)
                paginas.config(text="págs: " + str(totalPages))
                
                # Actualizar los campos de inicio y fin de página
                pagina_inicio.delete(0, tk.END)
                pagina_inicio.insert(0, "1")
                
                pagina_fin.delete(0, tk.END)
                pagina_fin.insert(0, str(totalPages))
                 # Verificar si se recortó hasta la página final
            if pagina_fin_val == totalPages:
                messagebox.showinfo("Proceso completado", "Has finalizado se recortó hasta la página final.")
            else:
                messagebox.showinfo("Éxito", f"PDF recortado y guardado como {nuevo_nombre}. El archivo original ha sido actualizado.")
        
    except Exception as e:
        messagebox.showerror("Error", f"Error al recortar el PDF: {str(e)}")

# Función para restaurar el PDF original desde el backup
def restaurar_pdf():
    global ultima_operacion, totalPages
    
    if not ultima_operacion:
        messagebox.showinfo("Información", "No hay operación anterior para restaurar")
        return
    
    try:
        archivo_original = ultima_operacion['archivo_original']
        
        # Verificar si el archivo está abierto
        try:
            # Intentar abrir el archivo en modo exclusivo
            with open(archivo_original, 'rb+') as file:
                pass
        except PermissionError:
            # Si no se puede abrir, significa que está en uso
            messagebox.showerror("Error", "El archivo PDF está abierto. Por favor, ciérrelo antes de restaurar.")
            return
        
        # Verificar si el backup existe
        if not os.path.exists(ultima_operacion['backup']):
            messagebox.showerror("Error", "El archivo de respaldo no se encuentra")
            return
        
        # Restaurar el archivo original desde el backup
        shutil.copy2(ultima_operacion['backup'], archivo_original)
        
        messagebox.showinfo("Éxito", "Se ha restaurado el PDF una version antes")
        
        # Actualizar la información de páginas
        with open(archivo_original, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            totalPages = len(pdf_reader.pages)
            paginas.config(text="págs: " + str(totalPages))
            
            # Actualizar los campos de inicio y fin de página
            pagina_inicio.delete(0, tk.END)
            pagina_inicio.insert(0, "1")
            
            pagina_fin.delete(0, tk.END)
            pagina_fin.insert(0, str(totalPages))
        
        # Abrir el archivo restaurado
        webbrowser.open_new(archivo_original)
        
        # Deshabilitar el botón después de restaurar
        btn_restaurar.config(state=tk.DISABLED)
        
        # Limpiar la información de la última operación
        ultima_operacion = None
        
    except Exception as e:
        messagebox.showerror("Error", f"Error al restaurar el PDF: {str(e)}")


# Hipervinculo    
def callback(url):
    webbrowser.open_new(url)

# abrir carpeta escaneados
def carpeta_escaneados():

    os.startfile(entregados)

# abrir carpeta renombrados
def carpeta_renombrados():

    os.startfile(copiados)

# abrir archivo copia de seguridad
def carpeta_backups():
    global Actual, Archivo
    
    # Verificar si hay archivos en la carpeta de copia de seguridad
    if not os.path.exists(copia_seguridad):
        messagebox.showinfo("Información", "La carpeta de copia de seguridad no existe")
        return
    
    backup_files = os.listdir(copia_seguridad)
    
    if len(backup_files) == 0:
        messagebox.showinfo("Información", "No hay archivos en la carpeta de copia de seguridad")
        return
    
    # Verificar si hay un archivo actual en la lista de Archivo
    if len(Archivo) == 0 or Actual > len(Archivo):
        # Si no hay archivo actual, abrir el primer archivo de la carpeta de copia de seguridad
        backup_file_path = os.path.join(copia_seguridad, backup_files[0])
    else:
        # Obtener el nombre del archivo actual
        n = Actual
        archivo_actual = Archivo[n-1]
        
        # Buscar un archivo de backup correspondiente
        matching_backups = [f for f in backup_files if archivo_actual in f]
        
        if matching_backups:
            # Usar el primer archivo de backup que coincida
            backup_file_path = os.path.join(copia_seguridad, matching_backups[0])
        else:
            # Si no se encuentra un backup específico, usar el primer archivo de la carpeta
            backup_file_path = os.path.join(copia_seguridad, backup_files[0])
    
    # Mostrar un mensaje de advertencia
    messagebox.showwarning("Recomendación", 
                          "Se recomienda cerrar todas las pestañas para evitar confusiones",
                          icon="warning")
    
    # Verificar si el archivo existe
    if os.path.exists(backup_file_path):
        # Abrir el archivo PDF en el navegador predeterminado
        webbrowser.open_new(backup_file_path)
    else:
        messagebox.showinfo("Información", "El archivo de backup no se encuentra disponible")

def ano_texto(value):
    ano.delete(0, tk.END)  # limpia si existe uno
    ano.insert(0, value)   # inserta nuevo valor
    global year
    year = value

def cuenta():
    leyenda = str(Actual) + " de " + str(len(Archivo))
    Conteo.config(text=leyenda)
    
def abrir_pdf():
    global totalPages
    n = Actual

    #contenido de la carpeta
    contents = os.listdir(entregados)

    if len(contents) == 0:
        Archivo_actual.config(text="Sin archivos a renombrar")


    # verificar si se alcanzo el total de archivos
    elif Actual > len(Archivo):
        Archivo_actual.config(text="Acabamos")
        leyenda = str(len(Archivo)) + " de " + str(len(Archivo))
        Conteo.config(text=leyenda)

    elif n-1 < len(Archivo):
        archivo_abrir = os.path.join(entregados, Archivo[n-1])

        # Contar las paginas
        file = open(archivo_abrir, 'rb')
        pdfReader = PyPDF2.PdfReader(file)
        totalPages = len(pdfReader.pages)

        leyenda = str(Archivo[n-1])
        Archivo_actual.config(text=leyenda)
        
        paginas.config(text="págs: " + str(totalPages))
        
        # Establecer página inicial y final por defecto
        pagina_inicio.delete(0, tk.END)
        pagina_inicio.insert(0, "1")
        
        pagina_fin.delete(0, tk.END)
        pagina_fin.insert(0, str(totalPages))
        
     
        # Abrir el PDF
        webbrowser.open_new(archivo_abrir)
        
        # Deshabilitar el botón de restaurar al abrir un nuevo PDF
        btn_restaurar.config(state=tk.DISABLED)
        global ultima_operacion
        ultima_operacion = None

def actualizar():
    # Limpiar la lista de archivos
    global Archivo
    Archivo = []

    # Ejecutar escaneados para obtener la lista de archivos
    escaneados()
    cuenta()
    abrir_pdf()

    # Crear copia de seguridad del archivo actual
    if len(Archivo) > 0 and Actual <= len(Archivo):
        try:
            # Obtener la ruta del archivo actual
            n = Actual
            archivo_actual = os.path.join(entregados, Archivo[n-1])
            
            # Crear la carpeta de copia de seguridad si no existe
            if not os.path.exists(copia_seguridad):
                os.makedirs(copia_seguridad)
            
            # Copiar el archivo a la carpeta de copia de seguridad
            nombre_archivo = os.path.basename(archivo_actual)
            ruta_destino = os.path.join(copia_seguridad, nombre_archivo)
            
            # Copiar el archivo, reemplazando si ya existe
            shutil.copy2(archivo_actual, ruta_destino)
            
            messagebox.showinfo("Copia de Seguridad", f"Se ha creado una copia de seguridad de {nombre_archivo}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear la copia de seguridad: {str(e)}")

    # Ejecutar formulario
    ano_texto(datetime.now().year)

# Parametros del formulario ----------------------------------------------------
root = tk.Tk()
root.geometry('750x450')  # Increased height to accommodate new buttons
root.title('Renombrar Oficios Escaneados')

frm = ttk.Frame(root, padding=10)
frm.grid()

# Varible para almacenar la captura del usuario
Inicio = tk.StringVar()
ano_1 = StringVar()
ano_1.trace_add("write", lambda name, index,mode, var=ano_1: ano_ingresado(var))

var = StringVar()
var.trace_add("write", lambda name, index,mode, var=var: oficio_capturado(var))


# Conteo
Conteo = ttk.Label(frm, width=30, font=('Helvetica', 12))
Conteo.grid(column=0, row=0, sticky = tk.W)
# Separador
ttk.Label(frm, text="                                        ", font=('Helvetica', 12)).grid(column=1, row=1, sticky=tk.W)


# Archivo actual
ttk.Label(frm, text="Archivo actual:", font=('Helvetica', 10, 'underline')).grid(column=0, row=2, sticky=tk.W)

paginas = ttk.Label(frm, width=30, font=('Helvetica', 12))
paginas.grid(column=1, row=2, sticky=tk.W)
paginas.config(foreground ='red')

Archivo_actual = ttk.Label(frm, width=50, font=('Helvetica', 12))
Archivo_actual.grid(column=0, row=3, sticky = tk.W+tk.E, columnspan=3)
Archivo_actual.config(foreground ='green')
 


# Número de página inicio y fin
ttk.Label(frm, text="Número página inicio", font=('Helvetica', 12)).grid(column=0, row=5, sticky=tk.W)
pagina_inicio = ttk.Entry(frm, width=10, font=('Helvetica', 12, "bold"))
pagina_inicio.grid(column=0, row=5, sticky=tk.E)

ttk.Label(frm, text="Número página fin", font=('Helvetica', 12)).grid(column=1, row=5, sticky=tk.W)
pagina_fin = ttk.Entry(frm, width=10, font=('Helvetica', 12, "bold"))
pagina_fin.grid(column=1, row=5, sticky=tk.E)

# Frame para botones de recortar y restaurar
recorte_frame = ttk.Frame(frm)
recorte_frame.grid(column=2, row=5, sticky=tk.W+tk.E)

# Botón Recortar PDF
ttk.Button(recorte_frame, text="Recortar PDF", command=recortar_pdf).pack(side=tk.LEFT, padx=2)

# Botón Restaurar PDF (inicialmente deshabilitado)
btn_restaurar = ttk.Button(recorte_frame, text="Restaurar PDF", command=restaurar_pdf, state=tk.DISABLED)
btn_restaurar.pack(side=tk.RIGHT, padx=2)


# Separador
ttk.Label(frm, text="                                        ", font=('Helvetica', 12)).grid(column=0, row=6, sticky=tk.W)

ttk.Label(frm, text="Generar nombre a partir de DG, Folio y Año", font=('Helvetica', 10, 'underline')).grid(column=0, row=7, sticky = tk.W+tk.E, columnspan=3)


# Inicio del oficio
ttk.Label(frm, text="Seleccione la DG", font=('Helvetica', 12)).grid(column=0, row=8)

selected_value = tk.StringVar()
combobox = ttk.Combobox(frm, textvariable=selected_value, width=15, font=('Helvetica', 12))
combobox.grid(column=0, row=9)
combobox['values'] = ('DGGC', 'DGGOI', 'DGGPI', 'DGGEERC', 'DGGEERNCM', 'DGGEERNCT', 'UGI')
combobox['state'] = 'readonly'
combobox.bind('<<ComboboxSelected>>', on_select)


# Numero de folio
ttk.Label(frm, text="Escriba el folio", font=('Helvetica', 12)).grid(column=1, row=8)
folio = ttk.Entry(frm, width=15, font=('Helvetica', 12, "bold"),textvariable=var).grid(column=1, row=9)


# Ano
ttk.Label(frm, text="Año", width=8, font=('Helvetica', 12)).grid(column=2, row=8)
ano = ttk.Entry(frm, width=8, font=('Helvetica', 12, "bold"),textvariable = ano_1)
ano.grid(column=2, row=9)
# Separador
ttk.Label(frm, text="                                        ", font=('Helvetica', 12)).grid(column=0, row=10, sticky=tk.W)
ttk.Label(frm, text="                                        ", font=('Helvetica', 12)).grid(column=0, row=11, sticky=tk.W)


# Nuevo nombre
ttk.Label(frm, text="Nuevo nombre:", font=('Helvetica', 10, 'underline')).grid(column=0, row=12, sticky=tk.W)
Nuevo_Nombre = ttk.Entry(frm, font=('Helvetica', 12), textvariable = Inicio)
Nuevo_Nombre.grid(column=0, row=13, sticky = tk.W+tk.E, columnspan=3)
# Separador
ttk.Label(frm, text="                                        ", font=('Helvetica', 12)).grid(column=0, row=14, sticky=tk.W)


# Botones -------------------------------------------------------

# Primera fila de botones
button_frame1 = ttk.Frame(frm)
button_frame1.grid(column=0, row=0, columnspan=3, sticky=tk.W+tk.E)

# Escaneados
ttk.Button(button_frame1, text="Escaneados", command=carpeta_escaneados).pack(side=tk.LEFT, padx=5)

# Actualizar
ttk.Button(button_frame1, text="Actualizar", command=actualizar).pack(side=tk.LEFT, padx=5)

# Renombrados
ttk.Button(button_frame1, text="Renombrados", command=carpeta_renombrados).pack(side=tk.LEFT, padx=5)

# Backups
ttk.Button(button_frame1, text="Copia de seguridad", command=carpeta_backups).pack(side=tk.LEFT, padx=5)

# Salir
ttk.Button(frm, text="Salir", command=root.destroy).grid(column=2, row=15)

# Credito
ttk.Label(frm, text="                                        ", font=('Helvetica', 12)).grid(column=0, row=16, sticky=tk.W)
ttk.Label(frm, text="                                        ", font=('Helvetica', 12)).grid(column=0, row=17, sticky=tk.W)
credito = ttk.Label(frm, text="Por Aaron Xolalpa Benitez para la ASEA", font=('Helvetica', 10, 'underline'))
credito.config(foreground ='blue')
credito.grid(column=0, row=18, sticky = tk.W+tk.E, columnspan=3)
credito.bind("<Button-1>", lambda e: callback("https://www.linkedin.com/in/aaron-xolalpa-benitez-744791315"))


# Crear carpetas si no existen
if not os.path.exists(entregados):
    os.makedirs(entregados)
    
if not os.path.exists(copiados):
    os.makedirs(copiados)

if not os.path.exists(backups):
    os.makedirs(backups)


# Llamar a la función de limpiar carpetas antes de iniciar el procesamiento
limpiar_carpetas()
crear_copia_seguridad()
escaneados()
cuenta()
abrir_pdf()

# Ejecutar formulario
ano_texto(datetime.now().year)


root.mainloop()