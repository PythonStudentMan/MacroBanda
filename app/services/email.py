from flask_mail import Message
from flask import url_for, render_template
from app.extensions import mail

def enviar_invitacion(email, token):

    link = url_for(
        'auth.aceptar_invitacion',
        token=token,
        _external=True
    )

    msg = Message(
        subject='Invitación a la plataforma',
        recipients=[email]
    )

    msg.body = f"""
Has sido invitaado a la plataforma.

Accede aquí:
{link}

Este enlace caduca en 48 horas.
"""
    msg.html = render_template('email/invitacion.html', link=link)

    mail.send(msg)
