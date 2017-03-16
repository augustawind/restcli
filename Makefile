.PHONY: install
install:
	pip install -U pip setuptools
	pip install -e .
	pip install -r requirements.txt

.PHONY: watch
watch:
	find restcli | entr make install

.PHONY: isort
isort:
	isort -rc -w 120 restcli
	isort -rc -w 120 tests

.PHONY: lint
lint:
	python setup.py check -rms
	flake8 restcli/ tests/

.PHONY: test
test:
	pytest --cov=restcli && coverage combine

.PHONY: .test-build-cov
.test-build-cov:
	pytest --cov=restcli && (echo "building coverage html"; coverage combine; coverage html)

.PHONY: all
all: .test-build-cov lint

.PHONY: clean
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
