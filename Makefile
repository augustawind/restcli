.PHONY: install watch isort lint test .test-build-cov all clean

dev:
	pip install -e .

install:
	pip install -U pip setuptools
	pip install -e .
	pip install -r requirements.txt

watch:
	find restcli | entr make install

lint:
	python setup.py check -rms
	flake8 restcli/ tests/

test:
	pytest --cov=restcli && coverage combine

.test-build-cov:
	pytest --cov=restcli && (echo "building coverage html"; coverage combine; coverage html)

all: .test-build-cov lint

clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -rf .cache
	rm -rf htmlcov
	rm -rf *.egg-info
	rm -f .coverage
	rm -f .coverage.*
	rm -rf build
	python setup.py clean
