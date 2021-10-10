PYLINT = flake8

FORCE:

tests: FORCE
	$(PYLINT) *.py
	nosetests --exe --with-coverage --verbose --cover-package=SETemplate

prod: tests
	git commit -a
	git push origin main

dev_env: FORCE
	pip3 install -r requirements-dev.txt

%.py: FORCE
	nosetests tests.test_$* --nocapture
