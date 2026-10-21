from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User

# Creamos el Blueprint para la autenticación
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Si el usuario ya está autenticado, lo mandamos a la página principal
    if current_user.is_authenticated:
        return redirect(url_for('events.list_events'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role') # 'organizer' o 'attendee'
        bio = request.form.get('bio', '')

        # Validaciones básicas en el servidor
        if not username or not email or not password or not role:
            flash('Todos los campos obligatorios deben ser completados.', 'danger')
            return redirect(url_for('auth.register'))

        # Verificar si el usuario o correo ya existen
        user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
        if user_exists:
            flash('El nombre de usuario o el correo electrónico ya están registrados.', 'danger')
            return redirect(url_for('auth.register'))

        # Crear el nuevo usuario con la contraseña encriptada (hash)
        hashed_password = generate_password_hash(password, method='scrypt')
        new_user = User(
            username=username, 
            email=email, 
            password_hash=hashed_password, 
            role=role,
            bio=bio
        )

        db.session.add(new_user)
        db.session.commit()

        flash('¡Registro exitoso! Ya puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # 1. Si ya está autenticado, se va al catálogo
    if current_user.is_authenticated:
        return redirect(url_for('events.list_events'))

    # 2. Si el usuario llenó el formulario y le dio al botón "Ingresar"
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(email=email).first()

        # Verificar si el usuario existe y la contraseña coincide
        if not user or not check_password_hash(user.password_hash, password):
            flash('Por favor, verifica tus credenciales e intenta de nuevo.', 'danger')
            return redirect(url_for('auth.login'))

        # Iniciar sesión con Flask-Login
        login_user(user, remember=remember)

        # Redirección dinámica según el rol
        flash(f'¡Bienvenido de nuevo, {user.username}!', 'success')
        if user.role == 'organizer':
            return redirect(url_for('events.dashboard_organizer'))
        else:
            return redirect(url_for('events.list_events'))

    # 3. SI EL MÉTODO ES 'GET' (Solo visita la página), se ejecuta esto al final sin bloquear nada:
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('auth.login'))