start-wave:
	cd /wave && ./waved

watch-app:
	cd ./src && wave run app.py

watch-tests:
	ptw --runner "pytest -m watch"