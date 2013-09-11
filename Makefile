upload::
	/bin/rm -RF build
	mkdir build
	cp -R dateutil www *.py *.yaml 
	grep -v default_expiration < app.yaml > build/app.yaml
	/usr/local/google_appengine/appcfg.py update build
