install:
	pip install --editable .

watch:
	find restcli | entr make install

test:
	pytest

deps:
	pip install -r requirements.txt
