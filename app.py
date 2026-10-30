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
        host=os.environ.get("DB_HOST", "127.0.0.1"),
        port=int(os.environ.get("DB_PORT", 3306)),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", ""),
        database=os.environ.get("DB_NAME", "login_db"),
        cursorclass=pymysql.cursors.DictCursor,
    )


def preparar_bd():
    try:
        conexion = conectar()
        with conexion.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    usuario VARCHAR(100) UNIQUE NOT NULL,
                    clave VARCHAR(255) NOT NULL
                )
            """)
        conexion.commit()
        conexion.close()
    except Exception as e:
        print(f"Advertencia BD local: {e}")


@app.route("/")
def inicio():
    if "usuario" not in session:
        return redirect(url_for("login"))

    return render_template("inicio.html")


@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        clave = request.form.get("clave", "")

        if not usuario or not clave:
            flash("Completa todos los campos")
            return redirect(url_for("registro"))

        if len(clave) < 8:
            flash("La contraseña debe tener al menos 8 caracteres")
            return redirect(url_for("registro"))

        preparar_bd()
        try:
            conexion = conectar()
            with conexion.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO usuarios (usuario, clave) VALUES (%s, %s)",
                    (usuario, generate_password_hash(clave)),
                )
            conexion.commit()
            conexion.close()
            flash("Usuario registrado correctamente")
            return redirect(url_for("login"))

        except pymysql.err.IntegrityError:
            flash("Ese nombre de usuario ya existe")
        except Exception as e:
            flash(f"Error al conectar con la base de datos: {e}")

    return render_template("registro.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        clave = request.form.get("clave", "")

        preparar_bd()
        resultado = None
        try:
            conexion = conectar()
            with conexion.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM usuarios WHERE usuario = %s",
                    (usuario,),
                )
                resultado = cursor.fetchone()
            conexion.close()
        except Exception as e:
            print(f"Error en login BD: {e}")

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
    puerto = int(os.environ.get("PORT", 8080))
    print(f"\n Servidor corriendo localmente en: http://127.0.0.1:{puerto}\n")
    app.run(
        host="127.0.0.1",
        port=puerto,
        debug=True,
    )