from wtforms import Form
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FloatField, RadioField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

#Create a class which inherits from FlaskForm.
#Each form field are imported classes
#Add another requirements, called validators, as arguments. DataRequired means can't be empty
class Form(Form):
    location = StringField('Locație', validators=[Length(min=2, max=20)])

    action = StringField('Activitate', validators=[Length(min=2, max=20)])


    templow_on = RadioField('Low temp', choices=[(True,'on'),(False, 'off')])
    templow_value = FloatField('Value')

    humidhigh_on = RadioField('High humidity', choices=[(True,'on'),(False, 'off')])
    humidhigh_value = FloatField('Value')

    submit = SubmitField('更新')


    #warning = SelectField('Select Notification', choices=[('none', 'None'), ('hightemp', 'High Temp'), ('lowtemp', 'Low Temp'), ('lowlight', 'Low light')])