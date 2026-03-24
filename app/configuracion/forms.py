from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, DecimalField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

class TipoSocioForm(FlaskForm):

    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=50)])
    tiene_cuota = BooleanField('¿Tiene cuota?')

    # Campos de cuota
    importe = DecimalField('Importe (€)', validators=[NumberRange(min=0)], places=2, default=0)
    frecuencia = SelectField(
        'Frecuencia',
        choices=[
            ('unico', 'Pago Único'),
            ('mensual', 'Mensual'),
            ('bimensual', 'Bimensual'),
            ('trimestral', 'Trimestral'),
            ('cuatrimestral', 'Cuatrimestral'),
            ('anual', 'Anual'),
            ('semanal', 'Semanal'),
            ('quincenal', 'Quincenal')
        ]
    )

    submit = SubmitField('Guardar')