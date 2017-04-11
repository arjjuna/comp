# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField,\
					IntegerField, DateField
from wtforms import ValidationError
from wtforms.validators import Required, Length, Email, Regexp, EqualTo



class ChangePassword(FlaskForm):
	old_password = PasswordField('Mot de passe actuel', validators=[Required()])

	new_password = PasswordField('Nouveau mot de passe', validators=[
			Required(),
			 EqualTo('password_confirmation', message=u"Veuillez resaisir le m\xeame mot de passe" )
			 ])
	password_confirmation = PasswordField('Confirmer le mot de passe', validators=[Required()])


	submit = SubmitField(u'Sauvegarder')