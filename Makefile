upload::
	/bin/rm -Rf build
	mkdir build
	cp -R dateutil www *.py *.yaml build
	grep -v default_expiration < app.yaml > build/app.yaml
	/usr/local/google_appengine/appcfg.py update build

build::
	/bin/rm -Rf build
	mkdir build
	cp -R *.py *.yaml favicon.ico dateutil www build
	grep -v DELETE_IN_PRODUCTION www/app/index.html > build/www/app/index.html
