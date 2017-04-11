from . import mybp

from flask import current_app, url_for, render_template

from ..models import Notification, User

from .. import db

from forms import NotifyForm

@mybp.route('/notify', methods=['POST', 'GET'])
def notify():
	form = NotifyForm()

	if form.validate_on_submit():
		n = Notification(
				text = form.text.data,
				link = form.link.data,
				
				picture_endpoint = form.picture_endpoint.data,
				picture_kwargs   = form.picture_kwargs.data,

				user = User.query.get(int(form.user_id.data))

			)

		db.session.add(n)
		db.session.commit()
	
	return render_template('test/notify.html', form=form)