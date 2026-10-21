from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, User, Event, Registration

users_bp = Blueprint('users', __name__, url_prefix='/users')

@users_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Obtener los datos del formulario de edición
        username = request.form.get('username')
        bio = request.form.get('bio')

        # Validar que el nombre de usuario no esté vacío
        if not username:
            flash('El nombre de usuario no puede estar vacío.', 'danger')
            return redirect(url_for('users.profile'))

        # Verificar si el nuevo nombre de usuario ya está tomado por OTRO usuario
        existing_user = User.query.filter(User.username == username, User.id != current_user.id).first()
        if existing_user:
            flash('Ese nombre de usuario ya está en uso.', 'danger')
            return redirect(url_for('users.profile'))

        # Actualizar los datos del usuario actual
        current_user.username = username
        current_user.bio = bio
        
        db.session.commit()
        flash('Perfil actualizado correctamente.', 'success')
        return redirect(url_for('users.profile'))

    # --- LÓGICA DEL HISTORIAL SEGÚN EL ROL ---
    history = []
    if current_user.role == 'organizer':
        # El organizador ve los eventos creados por él mismo
        history = Event.query.filter_by(organizer_id=current_user.id).all()
    elif current_user.role == 'attendee':
        # El asistente ve las inscripciones vinculadas a su cuenta
        # Traemos los registros y a través de la relación M:N obtenemos el evento
        registrations = Registration.query.filter_by(user_id=current_user.id).all()
        history = [reg.event for reg in registrations]

    return render_template('users/profile.html', history=history)