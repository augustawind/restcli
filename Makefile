install:
	pip install --editable .

watch:
	find apicli | entr make install

test:
	pytest

deps:
	pip install -r requirements.txt
