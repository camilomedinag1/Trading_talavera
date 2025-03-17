from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import random
import time
import threading

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuración de SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'supersecretkey'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Modelo de Usuario
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    balance = db.Column(db.Float, default=10000.0)  # Dinero del usuario
    stocks = db.Column(db.JSON, default={})  # Acciones compradas

with app.app_context():
    db.create_all()

# Datos simulados de una acción
stock_data = {"symbol": "AAPL", "price": 150.0}

# Simulación de cambios de precio
def generate_stock_prices():
    while True:
        stock_data["price"] += random.uniform(-1, 1)
        socketio.emit("stock_price", stock_data)
        time.sleep(1)

threading.Thread(target=generate_stock_prices, daemon=True).start()

# Endpoint para obtener información de la acción
@app.route("/api/stock/info", methods=["GET"])
def get_stock_info():
    return jsonify(stock_data)

# Endpoint para comprar acciones
@app.route("/api/stock/buy", methods=["POST"])
@jwt_required()from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import random
import time
import threading
import json

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuración de SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'supersecretkey'  # Cambia esto en producción

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Modelo de Usuario
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    balance = db.Column(db.Float, default=10000.0)  # Saldo inicial
    stocks = db.Column(db.String, default=json.dumps({}))  # Acciones en formato JSON

# Crear la base de datos y usuario admin si no existen
with app.app_context():
    db.create_all()
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        hashed_password = bcrypt.generate_password_hash("123456").decode("utf-8")
        admin = User(username="admin", password=hashed_password, balance=10000.0, stocks=json.dumps({}))
        db.session.add(admin)
        db.session.commit()
        print("✅ Usuario 'admin' creado con contraseña '123456' y saldo $10,000")

# Datos simulados de una acción
stock_data = {"symbol": "AAPL", "price": 150.0}

# Simulación de cambios de precio
def generate_stock_prices():
    while True:
        stock_data["price"] += random.uniform(-1, 1)
        socketio.emit("stock_price", stock_data)
        time.sleep(1)

threading.Thread(target=generate_stock_prices, daemon=True).start()

# Endpoint para obtener información de la acción
@app.route("/api/stock/info", methods=["GET"])
def get_stock_info():
    return jsonify(stock_data)

# Endpoint para comprar acciones
@app.route("/api/stock/buy", methods=["POST"])
@jwt_required()
def buy_stock():
    data = request.json
    username = get_jwt_identity()
    quantity = int(data.get("quantity", 1))

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"message": "Usuario no encontrado"}), 404

    total_cost = stock_data["price"] * quantity
    if user.balance < total_cost:
        return jsonify({"message": "Saldo insuficiente"}), 400

    # Convertir stocks de string JSON a diccionario
    user_stocks = json.loads(user.stocks)

    # Actualizar las acciones compradas
    user_stocks[stock_data["symbol"]] = user_stocks.get(stock_data["symbol"], 0) + quantity
    user.balance -= total_cost

    # Guardar cambios
    user.stocks = json.dumps(user_stocks)
    db.session.commit()

    return jsonify({"message": "Compra exitosa", "balance": user.balance, "stocks": user_stocks})

# Endpoint para vender acciones
@app.route("/api/stock/sell", methods=["POST"])
@jwt_required()
def sell_stock():
    data = request.json
    username = get_jwt_identity()
    quantity = int(data.get("quantity", 1))

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"message": "Usuario no encontrado"}), 404

    # Convertir stocks de string JSON a diccionario
    user_stocks = json.loads(user.stocks)

    if stock_data["symbol"] not in user_stocks or user_stocks[stock_data["symbol"]] < quantity:
        return jsonify({"message": "No tienes suficientes acciones para vender"}), 400

    user_stocks[stock_data["symbol"]] -= quantity
    user.balance += stock_data["price"] * quantity

    # Guardar cambios
    user.stocks = json.dumps(user_stocks)
    db.session.commit()

    return jsonify({"message": "Venta exitosa", "balance": user.balance, "stocks": user_stocks})

# Endpoint para iniciar sesión
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"message": "Credenciales incorrectas"}), 401

    access_token = create_access_token(identity=username)
    return jsonify({"access_token": access_token}), 200

# Ruta protegida para probar autenticación
@app.route("/api/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify({"message": f"Bienvenido {current_user}"}), 200

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
