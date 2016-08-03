all: build develop

python3: build3 develop3

build:
	python2 setup.py build

build3:
	python3 setup.py build

clean:
	-rm -rf build/

realclean: clean
	-rm -rf reddit_service_ads_tracking.egg-info/

tests:
	nosetests

test3:
	nosetests3

develop:
	python2 setup.py develop

develop3:
	python3 setup.py develop

.PHONY: clean realclean tests tests3 develop develop3 build build3
