from . import mybp

from flask import current_app, url_for

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

