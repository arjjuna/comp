from . import auth

from flask import current_app, url_for, render_template

from forms import LoginForm, ClientRegistrationForm, ProfRegistrationForm


@auth.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	return render_template('auth/login.html', form=form)

@auth.route('/choix')
def registration_choice():
	return render_template('auth/registration_choice.html')

@auth.route('/enregistrer/client', methods=['GET', 'POST'])
def registration_client():
	form = ClientRegistrationForm()
	return render_template('auth/client_registration.html', form=form)