wave-start:
	cd /wave && ./waved

wave-watch:
	wave run app.py

wave-tour:
	cd /wave && wave run --no-reload examples.tour

watch-tests:
	ptw