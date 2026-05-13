import os
from dotenv import load_dotenv
load_dotenv()
import click
import random
import time
import logging
import colorlog

from flask import Flask, render_template, send_from_directory, request, jsonify
from flask.cli import with_appcontext
from flask_migrate import Migrate
from flask_socketio import SocketIO, emit
from flask_cors import CORS

import blueprints
from blueprints.api_v1_jugadores import api_v1_jugadores_bp
from blueprints.api_v1_pistas import api_v1_pistas_bp
from database import db
from extensions import cache
from models import Jugador, Pista, Usuario 
from methodOverride import MethodOverrideMiddleware
from flasgger import Swagger

# Seeders
from models.seeders.fillJugadores import seedJugadores
from models.seeders.fillPistas import seedPistas
from models.seeders.fillUsuarios import seedUsuarios


app = Flask(__name__, static_folder="public", static_url_path="", template_folder="templates")
app.secret_key = os.environ.get("SECRET_KEY")
CORS(app)


for handler in app.logger.handlers:
    app.logger.removeHandler(handler)

handler = colorlog.StreamHandler()

formatter = colorlog.ColoredFormatter(
    "%(asctime)s - %(log_color)s%(levelname)s: %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
)

handler.setFormatter(formatter)
app.logger.addHandler(handler)

app.logger.setLevel(logging.DEBUG)

app.config['SWAGGER'] = {
    'title': 'API Mundo Tenis',
    'uiversion': 3,
    'openapi': '3.0.3'
}

app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "assets/images")
app.config["THUMB_FOLDER"] = os.path.join(app.root_path, "assets/thumbnails")
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg"}

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False 

app.config['CACHE_TYPE'] = 'simple'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300


db.init_app(app)
migrate = Migrate(app, db, directory="app/models/migrations")
swagger = Swagger(app, template_file="openapi.yaml")
app.wsgi_app = MethodOverrideMiddleware(app.wsgi_app)
cache.init_app(app)

app.register_blueprint(blueprints.auth_bp, url_prefix="/auth")
app.register_blueprint(blueprints.jugadores_bp, url_prefix="/tu_mundo/jugadores")
app.register_blueprint(blueprints.pistas_bp, url_prefix="/tu_mundo/pistas")
app.register_blueprint(blueprints.usuarios_bp, url_prefix="/tu_mundo/usuarios")
app.register_blueprint(api_v1_jugadores_bp)
app.register_blueprint(api_v1_pistas_bp)


@click.command(name='seed')
@with_appcontext
def seed():
    """Poblar la base de datos con datos iniciales."""
    app.logger.info("Iniciando seeder...")
    seedUsuarios()
    seedJugadores()
    seedPistas()
    app.logger.info("Database seeding completed!")

app.cli.add_command(seed)


# RUTAS
@app.route("/")
@cache.cached(timeout=30)
def home():
    app.logger.info("Mundo Tenis iniciado!") 
    return render_template("index.html")

@app.route("/about") 
@cache.cached(timeout=60)
def about(): 
    return render_template("about.html")

@app.route("/tu_mundo")
def tu_mundo():
    app.logger.info("Bienvenido a tu mundo")
    return render_template("tu_mundo.html")

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(os.path.join(app.root_path, 'assets/images'), filename)

@app.route('/images/<path:filename>')
def serve_image(filename):
    thumb_path = os.path.join(app.config["THUMB_FOLDER"], filename.replace("thumbnails/", ""))
    if os.path.exists(thumb_path):
        return send_from_directory(app.config["THUMB_FOLDER"], filename.replace("thumbnails/", ""))

    img_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if os.path.exists(img_path):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    pub_path = os.path.join(app.root_path, "public/images", filename)
    if os.path.exists(pub_path):
        return send_from_directory(os.path.join(app.root_path, "public/images"), filename)

    return "Imagen no encontrada", 404


# ERRORES
@app.errorhandler(404)
def error_404(error):
    if request.path.startswith('/api/'):
        return jsonify({
            "error": "Not Found",
            "message": "El recurso solicitado no existe en la API",
            "status": 404
        }), 404
    return render_template("error404.html"), 404

@app.errorhandler(500)
def error_500(error):
    if request.path.startswith('/api/'):
        return jsonify({
            "error": "Internal Server Error",
            "message": "Ha ocurrido un error inesperado en el servidor de datos",
            "status": 500
        }), 500
    return render_template("error500.html"), 500


# Ejecutar la aplicación
if __name__ == "__main__":
    app.logger.info("Servidor arrancado correctamente en http://127.0.0.1:5000")
    app.run(debug=True)
    