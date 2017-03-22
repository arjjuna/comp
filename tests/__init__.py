import os
import sys
import unittest

def run():
	os.environ['FLASK_CONFIG'] = 'testing'

	tests = unittest.TestLoader().discover('.')
	ok = unittest.TextTestRunner(verbosity=2, failfast=True).run(tests).wasSuccessful()

	sys.exit(0 if ok else 1)