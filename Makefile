upload::
	make build
	/usr/local/google_appengine/appcfg.py update build

build::
	/bin/rm -Rf build
	mkdir build
	cp -R *.py *.yaml favicon.ico dateutil simpleauth oauth2 httplib2 www build
	grep -v default_expiration < app.yaml > build/app.yaml
	grep -v DELETE_IN_PRODUCTION www/app/index.html > build/www/app/index.html
