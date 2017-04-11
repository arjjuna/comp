from flask_wtf import FlaskForm

from wtforms import StringField, SubmitField, TextAreaField, IntegerField


class NotifyForm(FlaskForm):
	user_id     = IntegerField()
	text        = TextAreaField()
	link        = StringField()
	
	picture_endpoint = StringField()
	picture_kwargs   = StringField()

	submit      = SubmitField('send')
