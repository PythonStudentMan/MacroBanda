from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, TelField, SelectField, DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional

class SocioForm(FlaskForm):

    nombre = StringField('Nombre', validators=[DataRequired()])
    apellidos = StringField('Apellidos', validators=[Optional()])

    documento_identidad = StringField('NIF/NIE/CIF', validators=[Optional()])

    email = EmailField('Email', validators=[Optional()])
    telefono = TelField('Teléfono', validators=[Optional()])

    direccion = StringField('Dirección', validators=[Optional()])
    cp = StringField('C.P.', validators=[Optional()])
    poblacion = StringField('Población', validators=[Optional()])
    provincia = StringField('Provincia', validators=[Optional()])

    tipo_socio_id = SelectField('Tipo de Socio', coerce=int)

    fecha_alta = DateField('Fecha de alta', validators=[DataRequired()])

    observaciones = TextAreaField('Observaciones', validators=[Optional()])

    submit = SubmitField('Guardar')
