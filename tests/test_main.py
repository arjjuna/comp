from cases import ViewsTestCase
from flask import url_for


class MainViewsTest(ViewsTestCase):
	def test_mainBp(self):
		#The index
		body, status_code, headers = self.get(url_for('main.index'))
		_ = (status_code == 200)
		self.assertTrue(_)