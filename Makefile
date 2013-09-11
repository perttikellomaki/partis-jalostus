upload::
	/bin/rm -Rf build
	mkdir build
	cp -R dateutil www *.py *.yaml build
	grep -v default_expiration < app.yaml > build/app.yaml
	/usr/local/google_appengine/appcfg.py update build
