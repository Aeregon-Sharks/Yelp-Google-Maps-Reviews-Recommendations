from flask import Flask, render_template, request, jsonify
import os
from google.cloud import storage

ALLOWED_EXTENSIONS = {".csv"}

# Configuración de Cloud Storage
credentials_path = "C:/Users/Work/Downloads/eminent-cycle-415715-3ef9bde04901.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
bucket_name = "yelp-ggmaps-data"
client = storage.Client()
bucket = client.get_bucket(bucket_name)

app = Flask(__name__)

# Añadir un indicador de inicio de sesión
logged_in = False

@app.route('/')
def index():
    return render_template('index.html', logged_in=logged_in)

@app.route('/login', methods=['POST'])
def login():
    global logged_in
    usuario = request.form['usuario']
    contrasena = request.form['contrasena']

    # Lógica para validar el usuario y contraseña
    if usuario == 'admin' and contrasena == 'admin':
        logged_in = True
        return render_template('index.html', logged_in=logged_in)
    else:
        return 'Usuario o contraseña incorrectos.'

@app.route('/logout')
def logout():
    global logged_in
    logged_in = False
    return redirect('/')

@app.route('/upload', methods=['POST'])
def upload():
    if not logged_in:
        return 'Inicia sesión para subir archivos.'
    
    archivo = request.files['archivo']
    file_name = "raw/" + request.form['carpeta'] + "/" + request.form['archivo_a_reemplazar']

    # Verificar si el archivo tiene una extensión permitida
    if not allowed_file(archivo.filename):
        return f'El formato de archivo no está permitido. Puede subir archivos con extensión: .csv'

    # Verificar si el archivo ya existe en Cloud Storage
    if is_file_uploaded(bucket_name, file_name):
        return f'El archivo {file_name} ya existe en Cloud Storage. No se puede subir.'
    else:
        # Sube el archivo a Cloud Storage
        blob = bucket.blob(file_name)
        blob.upload_from_file(archivo)
        return f'Archivo {file_name} subido exitosamente.'

@app.route('/get_folders', methods=['GET'])
def get_folders():
    folders = []

    # Obtener las carpetas dentro de la carpeta 'raw'
    blobs = bucket.list_blobs(prefix='raw/')
    for blob in blobs:
        folder_name = os.path.dirname(blob.name)
        if folder_name not in folders:
            folders.append(folder_name)

    return jsonify({'folders': folders})

@app.route('/get_files', methods=['POST'])
def get_files():
    selected_folder = request.json['folder']
    files = []

    # Obtener los archivos dentro de la carpeta seleccionada
    blobs = bucket.list_blobs(prefix=selected_folder)
    for blob in blobs:
        if blob.name != selected_folder:  # Evitar agregar la carpeta como un archivo
            files.append(blob.name)

    return jsonify({'files': files})

def allowed_file(filename):
    return any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)

if __name__ == '__main__':
    app.run(debug=True)