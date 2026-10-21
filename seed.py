from app import create_app
from models import db, User, Event
from werkzeug.security import generate_password_hash
from datetime import datetime

app = create_app()

with app.app_context():

    db.drop_all()
    db.create_all()

    print("Creando usuarios de prueba...")

    password_organizador = generate_password_hash('organizador123', method='scrypt')
    password_asistente = generate_password_hash('asistente123', method='scrypt')

    organizador = User(
        username='juan_organiza',
        email='organizador@correo.com',
        password_hash=password_organizador,
        role='organizer',
        bio='Organizador profesional de eventos tecnológicos.'
    )

    asistente = User(
        username='pedro_asiste',
        email='asistente@correo.com',
        password_hash=password_asistente,
        role='attendee',
        bio='Estudiante interesado en aprender programación.'
    )

    db.session.add(organizador)
    db.session.add(asistente)
    db.session.commit()

    print("Creando eventos de prueba...")

    evento1 = Event(
        title='Taller de Flask Básico',
        description='Aprende a estructurar tus aplicaciones web con Python y Flask.',
        date=datetime(2026, 6, 15, 14, 0),
        capacity=20,
        category='Tecnología',
        organizer_id=organizador.id
    )

    evento2 = Event(
        title='Conferencia de Bases de Datos',
        description='Modelado relacional y optimización de consultas SQL.',
        date=datetime(2026, 7, 20, 10, 30),
        capacity=50,
        category='Educación',
        organizer_id=organizador.id
    )

    evento3 = Event(
        title='Charla de Desarrollo Profesional',
        description='Cómo prepararse para entrevistas técnicas en la industria de software.',
        date=datetime(2026, 8, 5, 16, 0),
        capacity=2,
        category='Carrera',
        organizer_id=organizador.id
    )

    db.session.add_all([evento1, evento2, evento3])
    db.session.commit()

    print("¡Base de datos inicializada con éxito con datos de prueba!")