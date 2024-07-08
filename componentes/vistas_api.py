from flask import jsonify, request
from app import app
from componentes.modelos import Profesional, Sede, Usuario, Turno
from flask_login import login_user, login_required, logout_user, current_user
import bcrypt

@app.route('/', methods=['GET'])
def listar_rutas():
    """
    Lista todas las rutas disponibles en la API.

    Retorna:
        Un diccionario JSON con las rutas y sus descripciones.
    """
    # URL base de la aplicación (ajustar según tu configuración)
    url_base = "http://localhost:5000"

    rutas = [
        {
            "ruta": "/",
            "descripcion": "Ruta principal de la API.",
            "url": f"{url_base}/",
            "metodos": ["GET"],
        },
        {
            "ruta": "/api/profesionales",
            "descripcion": "Obtiene una lista de profesionales.",
            "url": f"{url_base}/api/profesionales",
            "metodos": ["GET"],
        },
        {
            "ruta": "/api/sedes",
            "descripcion": "Obtiene una lista de sedes.",
            "url": f"{url_base}/api/sedes",
            "metodos": ["GET"],
        },
        {
            "ruta": "/api/registro",
            "descripcion": "Registra un nuevo usuario.",
            "url": f"{url_base}/api/registro",
            "metodos": ["POST"],
        },
        {
            "ruta": "/api/login",
            "descripcion": "Inicia sesión en un usuario existente.",
            "url": f"{url_base}/api/login",
            "metodos": ["POST"],
        },
        {
            "ruta": "/api/eliminar_usuario/<int:id>",
            "descripcion": "Elimina un usuario por su ID.",
            "url": f"{url_base}/api/eliminar_usuario/1",  # Ejemplo de ID
            "metodos": ["POST"],
        },
        {
            "ruta": "/api/listar_usuarios",
            "descripcion": "Obtiene una lista de todos los usuarios.",
            "url": f"{url_base}/api/listar_usuarios",
            "metodos": ["GET"],
        },
        {
            "ruta": "/api/perfil",
            "descripcion": "Obtiene el perfil del usuario actual.",
            "url": f"{url_base}/api/perfil",
            "metodos": ["GET"],
        },
        {
            "ruta": "/api/logout",
            "descripcion": "Cierra la sesión del usuario actual.",
            "url": f"{url_base}/api/logout",
            "metodos": ["POST"],
        },
        {
            "ruta": "/api/especialidades",
            "descripcion": "Obtiene una lista de todas las especialidades disponibles.",
            "url": f"{url_base}/api/especialidades",
            "metodos": ["GET"],
        },
        {
            "ruta": "/api/profesionales/<especialidad>",
            "descripcion": "Obtiene una lista de profesionales por especialidad.",
            "url": f"{url_base}/api/profesionales/1",  # Ejemplo de especialidad
            "metodos": ["GET"],
        },
        {
            "ruta": "/api/horarios/<especialidad>",
            "descripcion": "Obtiene los horarios disponibles por especialidad.",
            "url": f"{url_base}/api/horarios/1",  # Ejemplo de especialidad
            "metodos": ["GET"],
        },
        {
            "ruta": "/api/guardar_turno",
            "descripcion": "Guarda un nuevo turno.",
            "url": f"{url_base}/api/guardar_turno",
            "metodos": ["POST"],
        },
    ]

    # Crear una respuesta HTML con enlaces clicables
    html_response = '<ul>'
    for ruta in rutas:
        html_response += f'<li><a href="{ruta["url"]}">{ruta["url"]}</a> - {ruta["descripcion"]} (Métodos: {", ".join(ruta["metodos"])})</li>'
    html_response += '</ul>'

    return html_response

@app.route('/api/profesionales', methods=['GET'])
def mostrar_profesionales():
    profesionales = Profesional.obtener()
    dicc_profesionales = [profesional.__dict__ for profesional in profesionales]
    return jsonify(dicc_profesionales)
    
@app.route('/api/sedes', methods=['GET'])
def mostrar_sedes():
    sedes = Sede.obtener()
    dicc_sedes = [sede.__dict__ for sede in sedes]
    return jsonify(dicc_sedes)

@app.route('/api/registro', methods=['POST'])
def registro():
    datos = request.json  # Obtener los datos del cuerpo de la solicitud JSON

    # Validar los datos recibidos
    if not all(key in datos for key in ['username', 'password', 'nombre', 'email']):
        print("Datos incompletos")
        return jsonify({'error': 'Datos incompletos'}), 400

    # Encriptar la contraseña antes de crear el nuevo usuario
    password_encriptada = bcrypt.hashpw(datos['password'].encode('utf-8'), bcrypt.gensalt())

    # Crear un nuevo usuario en la base de datos
    nuevo_usuario = Usuario(
        username=datos['username'],
        password=password_encriptada.decode('utf-8'),
        nombre=datos['nombre'],
        email=datos['email']
    )

    print(f"Contraseña encriptada: {nuevo_usuario.password}")

    # Guardar el usuario en la base de datos
    resultado = nuevo_usuario.guardar_db()
    print(resultado)

    if resultado == 'Creación exitosa.':
        return jsonify({'mensaje': 'Usuario registrado exitosamente'}), 201
    else:
        return jsonify({'error': 'Error al registrar usuario'}), 500

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    print("Usuario proporcionado:", username)
    print("Contraseña proporcionada:", password)

    if not username or not password:
        return jsonify({'mensaje': 'Falta nombre de usuario o contraseña'}), 400

    usuario = Usuario.obtener_para_login(username)
    print(usuario)

    if usuario:
        print(f"Contraseña almacenada en la base de datos: {usuario.password}")

        # Verificar la contraseña usando bcrypt
        es_valida = bcrypt.checkpw(password.encode('utf-8'), usuario.password.encode('utf-8'))

        if es_valida:
            login_user(usuario)
            return jsonify({'mensaje': 'Inicio de sesión exitoso'}), 200
        else:
            return jsonify({'mensaje': 'Credenciales inválidas'}), 401
    else:
        return jsonify({'mensaje': 'Credenciales inválidas'}), 401

@app.route('/api/eliminar_usuario/<int:id>', methods=['POST'])
def eliminar_usuario(id):
    resultado = Usuario.eliminar(id)
    if resultado == 'Eliminación exitosa.':
        return jsonify({'mensaje': 'Usuario eliminado exitosamente'}), 200
    else:
        return jsonify({'error': 'No se pudo eliminar el usuario'}), 500

@app.route('/api/listar_usuarios', methods=['GET'])
def listar_usuarios():
    usuarios = Usuario.obtener_todos()  # Método hipotético para obtener todos los usuarios

    # Convertir los objetos de usuarios a una lista de diccionarios
    usuarios_serializados = [usuario.to_dict() for usuario in usuarios]

    return jsonify(usuarios_serializados)

@app.route('/api/perfil', methods=['GET'])
@login_required
def perfil():
    usuario = current_user
    turnos = Turno.obtener_por_usuario(usuario.id)
    return jsonify({
        'id': usuario.id,
        'username': usuario.username,
        'nombre': usuario.nombre,
        'email': usuario.email,
        'turnos': turnos
    })

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'mensaje': 'Sesión cerrada'})

@app.route('/api/especialidades', methods=['GET'])
def api_especialidades():
    profesionales = Profesional.obtener()
    if not profesionales:
        return jsonify([])  # Devolver una lista vacía si no hay profesionales
    especialidades = set()  # Usamos un set para garantizar especialidades únicas
    for profesional in profesionales:
        especialidades.add(profesional.especialidad)

    return jsonify(list(especialidades))

@app.route('/api/profesionales/<especialidad>', methods=['GET'])
def api_profesionales_por_especialidad(especialidad):
    # Obtener todos los profesionales
    profesionales = Profesional.obtener()

    # Filtrar por especialidad si se proporciona una
    if especialidad != 'all':
        profesionales_filtrados = [profesional for profesional in profesionales if profesional.especialidad.lower() == especialidad.lower()]
    else:
        profesionales_filtrados = profesionales

    # Preparar la lista de profesionales en formato JSON
    profesionales_json = []
    for profesional in profesionales_filtrados:
        profesional_json = {
            'nombre': profesional.nombre,
            # Agrega otros campos necesarios
        }
        profesionales_json.append(profesional_json)

    # Convertir a formato JSON y devolver
    return jsonify(profesionales_json)

@app.route('/api/horarios/<especialidad>', methods=['GET'])
def api_horarios_por_profesional(especialidad):
    profesionales = Profesional.obtener()

    # Filtrar profesionales por especialidad
    profesionales_filtrados = [profesional for profesional in profesionales if profesional.especialidad.lower() == especialidad.lower()]

    horarios = []
    for profesional in profesionales_filtrados:
        profesional_horarios = Turno.obtener_horarios(profesional.id)
        for horario in profesional_horarios:
            horarios.append({
                'profesional': profesional.nombre,
                'horario': horario
            })

    return jsonify(horarios)

@app.route('/api/guardar_turno', methods=['POST'])
@login_required
def guardar_turno():
    data = request.get_json()

    # Validar los datos recibidos
    especialidad = data.get('especialidad')
    profesional_nombre = data.get('profesional')
    horario = data.get('horario')
    sede_nombre = data.get('sede')
    user_id = current_user.id

    if not (especialidad and profesional_nombre and horario and sede_nombre):
        return jsonify({'mensaje': 'Datos incompletos para guardar el turno'}), 400

    profesional = Profesional.obtener_por_nombre(profesional_nombre)
    sede = Sede.obtener_por_nombre(sede_nombre)

    if not profesional or not sede:
        return jsonify({'mensaje': 'Profesional o sede no encontrados'}), 404

    turno = Turno(
        especialidad=especialidad,
        profesional_id=profesional.id,
        horario=horario,
        sede_id=sede.id,
        user_id=user_id
    )

    resultado = turno.guardar_db()

    if resultado == 'Creación exitosa.':
        return jsonify({'mensaje': 'Turno guardado exitosamente'}), 201
    else:
        return jsonify({'error': 'Error al guardar turno'}), 500
