install:
	pip install --editable .

watch:
	find apicli | entr make install
