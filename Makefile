start-wave:
	cd /wave && ./waved

watch-app:
	wave run app.py

watch-tests:
	ptw --runner "pytest -s" --poll