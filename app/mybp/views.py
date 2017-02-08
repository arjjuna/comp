from . import mybp

from flask import current_app, url_for, render_template

import urllib

@mybp.route('/urls')
def urls():
	urls = '<ul>'
	for rule in current_app.url_map.iter_rules():
		options = {}

		url = ''
		for arg in rule.arguments:
			options[arg] = '[{0}]'.format(str(arg))

		options['_external'] = True
		url = urllib.unquote(url_for(rule.endpoint, **options))

		urls += '<li>' + str(rule.endpoint) + " <a href='{0}'>".format(url) + url + '</a></li>'

	urls += '</ul>'
	return urls

@mybp.route('/dashboard')
def dashboard():
	return render_template('dashboard/base.html')

@mybp.route('/dashboard/extended')
def dashboard_extended():
	return render_template('dashboard/test_base.html')

@mybp.route('/login')
def auth():
	return render_template('auth/login.html')

