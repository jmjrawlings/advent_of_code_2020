start-wave:
	cd /wave && ./waved

tour-wave:
	cd /wave/examples && wave run --no-reload tour.py

watch-app:
	wave run app.py

watch-tests:
	ptw --runner "pytest -s" --poll
