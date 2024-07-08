from flask import Flask, jsonify
from flask_cors import CORS
from flask_login import LoginManager
from componentes.modelos import Usuario 

app = Flask(__name__)
app.json.ensure_ascii = False

# Configuración CORS para todas las rutas de la aplicación
CORS(app, resources={r"/api/*": {"origins": "http://127.0.0.1:5500"}})

# Utiliza una variable de entorno para la clave secreta en producción
app.secret_key = 'admin'

# Inicializar el gestor de inicio de sesión
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id)) 

# Ejemplo de una ruta API para 'especialidades'
@app.route('/api/especialidades', methods=['GET'])
def get_especialidades():
    # Aquí iría tu lógica para obtener las especialidades
    especialidades = ["Cardiología", "Dermatología", "Pediatría"]
    return jsonify(especialidades)

# Importar las vistas/APIs
from componentes.vistas_api import *

# La siguiente parte se ejecuta solo en desarrollo, no en producción
if __name__ == '__main__':
    app.run(debug=True)
