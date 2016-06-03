all: build develop

build:
	python2 setup.py build
	python3 setup.py build

clean:
	-rm -rf build/

realclean: clean
	-rm -rf reddit_service_ads_tracking.egg-info/

tests:
	nosetests
	nosetests3

develop:
	python2 setup.py develop
	python3 setup.py develop

.PHONY: clean realclean tests develop build
