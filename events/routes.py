from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime
from models import db, User, Event, Registration

events_bp = Blueprint('events', __name__, url_prefix='/events')

# ==========================================
# DECORADOR PERSONALIZADO PARA CONTROL DE ROLES
# ==========================================
def role_required(role_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Si el usuario no tiene el rol requerido, lanzamos error 403 (Prohibido)
            if current_user.role != role_name:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ==========================================
# RUTAS COMPARTIDAS / CATÁLOGO
# ==========================================

@events_bp.route('/')
@login_required
def list_events():
    # Listar todos los eventos disponibles para el catálogo general
    events = Event.query.all()
    return render_template('events/catalog.html', events=events)


# ==========================================
# RUTAS EXCLUSIVAS DEL ORGANIZADOR
# ==========================================

@events_bp.route('/dashboard')
@login_required
@role_required('organizer')
def dashboard_organizer():
    # El organizador solo ve los eventos creados por él mismo
    my_events = Event.query.filter_by(organizer_id=current_user.id).all()
    return render_template('events/dashboard.html', events=my_events)


@events_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required('organizer')
def create_event():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        date_str = request.form.get('date')
        capacity = request.form.get('capacity')
        category = request.form.get('category')

        if not title or not description or not date_str or not capacity or not category:
            flash('Todos los campos son obligatorios.', 'danger')
            return redirect(url_for('events.create_event'))

        # Conversión de la fecha string a objeto datetime de Python
        event_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')

        new_event = Event(
            title=title,
            description=description,
            date=event_date,
            capacity=int(capacity),
            category=category,
            organizer_id=current_user.id
        )
        db.session.add(new_event)
        db.session.commit()

        flash('¡Evento creado con éxito!', 'success')
        return redirect(url_for('events.dashboard_organizer'))

    return render_template('events/create.html')


@events_bp.route('/edit/<int:event_id>', methods=['GET', 'POST'])
@login_required
@role_required('organizer')
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Validación de autoría: Solo el creador puede editarlo
    if event.organizer_id != current_user.id:
        abort(403)

    if request.method == 'POST':
        event.title = request.form.get('title')
        event.description = request.form.get('description')
        event.capacity = int(request.form.get('capacity'))
        event.category = request.form.get('category')
        
        date_str = request.form.get('date')
        if date_str:
            event.date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')

        db.session.commit()
        flash('Evento actualizado correctamente.', 'success')
        return redirect(url_for('events.dashboard_organizer'))

    return render_template('events/edit.html', event=event)


@events_bp.route('/delete/<int:event_id>', methods=['POST'])
@login_required
@role_required('organizer')
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Validación de autoría: Solo el creador puede eliminarlo
    if event.organizer_id != current_user.id:
        abort(403)

    # Eliminar inscripciones asociadas primero en cascada manual sencilla
    Registration.query.filter_by(event_id=event.id).delete()
    
    db.session.delete(event)
    db.session.commit()
    
    flash('Evento eliminado de forma definitiva.', 'info')
    return redirect(url_for('events.dashboard_organizer'))


@events_bp.route('/event/<int:event_id>/attendees')
@login_required
@role_required('organizer')
def view_attendees(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Solo el organizador dueño puede ver la lista de inscritos
    if event.organizer_id != current_user.id:
        abort(403)
        
    return render_template('events/attendees.html', event=event)


# ==========================================
# RUTAS EXCLUSIVAS DEL ASISTENTE (INSCIPCIONES)
# ==========================================

@events_bp.route('/register_to_event/<int:event_id>', methods=['POST'])
@login_required
@role_required('attendee')
def register_to_event(event_id):
    event = Event.query.get_or_404(event_id)

    # 1. Verificar si ya está inscrito
    already_registered = Registration.query.filter_by(user_id=current_user.id, event_id=event.id).first()
    if already_registered:
        flash('Ya estás inscrito en este evento.', 'warning')
        return redirect(url_for('events.list_events'))

    # 2. Control estricto de cupo: Contar cuántos inscritos hay actualmente
    current_registrations = Registration.query.filter_by(event_id=event.id).count()
    if current_registrations >= event.capacity:
        flash('Lo sentimos, no hay cupos disponibles para este evento.', 'danger')
        return redirect(url_for('events.list_events'))

    # 3. Proceder con la inscripción
    new_registration = Registration(user_id=current_user.id, event_id=event.id)
    db.session.add(new_registration)
    db.session.commit()

    flash(f'Te has inscrito exitosamente en: {event.title}', 'success')
    return redirect(url_for('events.list_events'))


@events_bp.route('/cancel_registration/<int:event_id>', methods=['POST'])
@login_required
@role_required('attendee')
def cancel_registration(event_id):
    registration = Registration.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    
    if not registration:
        flash('No estás inscrito en este evento.', 'danger')
        return redirect(url_for('events.list_events'))

    db.session.delete(registration)
    db.session.commit()

    flash('Inscripción cancelada con éxito.', 'info')
    return redirect(url_for('events.list_events'))