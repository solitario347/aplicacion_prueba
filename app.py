
import os

import pymysql
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
)
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clave-solo-para-pruebas")


def conectar():
    return pymysql.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ.get("DB_PORT", 3306)),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
        cursorclass=pymysql.cursors.DictCursor,
    )


def preparar_bd():
    conexion = conectar()

    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    usuario VARCHAR(100) UNIQUE NOT NULL,
                    clave VARCHAR(255) NOT NULL
                )
            """)

        conexion.commit()

    finally:
        conexion.close()


@app.route("/")
def inicio():
    if "usuario" not in session:
        return redirect(url_for("login"))

    return render_template("inicio.html")


@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        usuario = request.form["usuario"].strip()
        clave = request.form["clave"]

        if not usuario or not clave:
            flash("Completa todos los campos")
            return redirect(url_for("registro"))

        if len(clave) < 8:
            flash("La contraseña debe tener al menos 8 caracteres")
            return redirect(url_for("registro"))

        preparar_bd()
        conexion = conectar()

        try:
            with conexion.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO usuarios (usuario, clave) VALUES (%s, %s)",
                    (usuario, generate_password_hash(clave)),
                )

            conexion.commit()
            flash("Usuario registrado correctamente")
            return redirect(url_for("login"))

        except pymysql.err.IntegrityError:
            flash("Ese nombre de usuario ya existe")

        finally:
            conexion.close()

    return render_template("registro.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"].strip()
        clave = request.form["clave"]

        preparar_bd()
        conexion = conectar()

        try:
            with conexion.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM usuarios WHERE usuario = %s",
                    (usuario,),
                )
                resultado = cursor.fetchone()

        finally:
            conexion.close()

        if resultado and check_password_hash(resultado["clave"], clave):
            session.clear()
            session["usuario"] = resultado["usuario"]

            return redirect(url_for("inicio"))

        flash("Usuario o contraseña incorrectos")

    return render_template("login.html")


@app.route("/salir")
def salir():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False,
    )
