# CORS(app, resources={r"/api/*": {"origins": "*"}})

# Utiliza una variable de entorno para la clave secreta en producción
app.secret_key = 'admin'

# Inicializar el gestor de inicio de sesión
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))  # Asumiendo que la clase Usuario tiene un campo de clave primaria 'id'

# Importar las vistas/APIs
from componentes.vistas_api import *

# Configuración de SQLAlchemy si estás utilizando
# from flask_sqlalchemy import SQLAlchemy
# app.config['SQLALCHEMY_DATABASE_URI'] = 'tu-uri-de-base-de-datos'
# db = SQLAlchemy(app)
# db.init_app(app)

# La siguiente parte se ejecuta solo en desarrollo, no en producción
if __name__ == '__main__':
    app.run()
