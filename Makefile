start-wave:
	cd /wave && ./waved

watch-wave:
	wave run app.py

tour-wave:
	cd /wave && wave run --no-reload examples.tour

watch-tests:
	ptw