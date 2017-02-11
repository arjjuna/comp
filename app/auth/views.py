from . import auth

from .. import db

from flask import request, current_app, url_for, render_template, redirect, flash

from flask_login import login_user, logout_user, login_required, current_user

from forms import LoginForm, ClientRegistrationForm, ProfRegistrationForm
from ..models import User, Client, Prof
from ..emails import send_email


@auth.route('/connexion', methods=['GET', 'POST'])
def login():
	if not current_user.is_anonymous:
		return redirect(url_for('auth.unconfirmed'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user, form.remember_me.data)
			return redirect(request.args.get('next') or url_for('main.index') )
		flash("Nom d'utilisateur ou mot de passe incorrecte")
	return render_template('auth/login.html', form=form)

@auth.route('/deconnexion')
@login_required
def logout():
	logout_user()
	flash(u'Vous vous \xeates d\xe9connect\xe9')
	return redirect(url_for('main.index'))

@auth.route('/choix')
def registration_choice():
	return render_template('auth/registration_choice.html')

@auth.route('/enregistrer/client', methods=['GET', 'POST'])
def register_client():
	form = ClientRegistrationForm()

	if form.validate_on_submit():
		client = Client()
		user   = User(email=form.email.data, password=form.password.data, username=form.username.data,
					 first_name=form.first_name.data, last_name=form.last_name.data, client=client)
		db.session.add(client)
		db.session.add(user)
		db.session.commit()

		token = user.generate_confirmation_token()
		send_email(user.email, ' Confirmez votre inscritpion',
					'auth/emails/confirm_client', user=user, token=token)
		
		flash(u'Un email de confirmation vous a \xeates envoy\xe9')
		return redirect(url_for('auth.login'))

	return render_template('auth/client_registration.html', form=form)

@auth.route('/enregistrer/prof', methods=['GET', 'POST'])
def register_prof():
	form = ProfRegistrationForm()

	if form.validate_on_submit():
		prof = Prof()
		user   = User(email=form.email.data, password=form.password.data, username=form.username.data,
					 first_name=form.first_name.data, last_name=form.last_name.data, prof=prof)
		db.session.add(prof)
		db.session.add(user)
		db.session.commit()

		token = user.generate_confirmation_token()
		send_email(user.email, ' Confirmez votre inscritpion',
					'auth/emails/confirm_prof', user=user, token=token)
		
		flash(u'Un email de confirmation vous a \xeates envoy\xe9')
		return redirect(url_for('auth.login'))

	return render_template('auth/prof_registration.html', form=form)





@auth.route('/confirm/<token>')
@login_required
def confirm(token):
	if current_user.confirmed:
		return redirect(url_for('main.index'))
	if current_user.confirm(token):
		flash(u'Confirmation r\xe9ussie')
	else:
		flash(u'Ce lien de confirmation est invalide ou expir\xe9')
	return redirect(url_for('main.index'))
	
@auth.before_app_request
def before_request():
	if current_user.is_authenticated and not current_user.confirmed \
				 and (request.endpoint != None) and (request.endpoint[:5] not in ['auth.', 'main.']):
		return redirect(url_for('auth.unconfirmed'))
		
@auth.route('/non_confirme')
def unconfirmed():
	if current_user.is_anonymous or current_user.confirmed:
		return redirect(url_for('main.index'))
	return "unconfirmed. visit this link %s " % url_for('auth.resend_confirmation')


@auth.route('/confirm')
@login_required
def resend_confirmation():
	token = current_user.generate_confirmation_token()
	if current_user.is_client():
		send_email(current_user.email, 'Confirmez votre inscription', 'auth/emails/confirm_client',  user=current_user, token=token)
	elif current_user.is_prof():
		send_email(current_user.email, 'Confirmez votre inscription', 'auth/emails/confirm_prof',  user=current_user, token=token)
	
	flash(u'Un nouvel email vous a \xe9t\xe9 envoy\xe9.')
	return redirect(url_for('main.index'))