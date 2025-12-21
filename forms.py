from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from flask_wtf.recaptcha import RecaptchaField

class ImageRotateForm(FlaskForm):
    image = FileField('Изображение', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Только изображения!')
    ])
    angle = IntegerField('Угол поворота (градусы)', validators=[
        DataRequired(),
        NumberRange(-360, 360)
    ])
    recaptcha = RecaptchaField()
    submit = SubmitField('Повернуть')