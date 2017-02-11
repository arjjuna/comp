from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms import ValidationError
from wtforms.validators import Required, Length, Email, Regexp, EqualTo

from ..models import User


class LoginForm(FlaskForm):
	email       = StringField('Email', validators=[])
	password    = PasswordField('Mot de passe', validators=[])
	remember_me = BooleanField(u'Rester connect\xe9')
	
	submit      = SubmitField('Se connecter')

class ProfRegistrationForm(FlaskForm):
	email      = StringField('Email', validators=[Required(), Length(1,64), Email() ] )
	username   = StringField("Nom d'utilisateur", validators=[Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
																								"Ne peut contenir que des lettres, des nombre, '.' et '_' ")])
	password   = PasswordField("Mot de passe", validators=[Required(), EqualTo('password_confirmation', message=u"Veuillez resaisir le m\xeame mot de passe" )] )
	password_confirmation = PasswordField('Confirmer le mot de passe', validators=[Required()])
	first_name = StringField(u'Pr\xe9nom', validators=[Required()])
	last_name  = StringField(u'Nom', validators=[Required()])
	
	submit     = SubmitField("S'enregistrer")
	
	def validate_email(self, field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError(u'Cet email est d\xe9j\xe0 enregistr\xe9.')
			
	def validate_username(self, field):
		if User.query.filter_by(username=field.data).first():
			raise ValidationError(u"Ce nom d'utilisateur est d\xe9j\xe0 enregistr\xe9.")	
			
class ClientRegistrationForm(FlaskForm):
	email      = StringField('Email', validators=[Required(), Length(1,64), Email() ] )
	username   = StringField("Nom d'utilisateur", validators=[Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
																							"Ne peut contenir que des lettres, des nombre, '.' et '_' ")])
	password   = PasswordField("Mot de passe", validators=[Required(), EqualTo('password_confirmation', message=u"Veuillez resaisir le m\xeame mot de passe" )] )
	password_confirmation = PasswordField('Confirmer le mot de passe', validators=[Required()])
	first_name = StringField(u'Pr\xe9nom', validators=[Required()])
	last_name  = StringField(u'Nom', validators=[Required()])
	submit     = SubmitField("S'enregistrer")
	
	def validate_email(self, field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError(u'Cet email est d\xe9j\xe0 enregistr\xe9.')
			
	def validate_username(self, field):
		if User.query.filter_by(username=field.data).first():
			raise ValidationError(u"Ce nom d'utilisateur est d\xe9j\xe0 enregistr\xe9.")
