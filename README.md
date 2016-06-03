# reddit_service_ads_tracking

[![Build Status](https://travis-ci.org/reddit/reddit-service-ads-tracking.svg?branch=master)](https://travis-ci.org/reddit/reddit-service-ads-tracking)

This service provides endpoints for tracking ad clicks, impressions, and conversions.

## prereqs

- vagrant (https://www.vagrantup.com/downloads.html)
- virtualbox (https://www.virtualbox.org/wiki/Downloads)

## installation

    vagrant up

## run the service

    vagrant ssh
    cd src
    baseplate-serve2 example.ini --bind 0.0.0.0:9090 --reload --debug

Check to see that everything is working by hitting the health check.

    curl localhost:9090/health

Vagrant is setup to forward 9090 on both guest and host so it should work from either place.

## run the tests

    vagrant ssh -c "cd src; nosetests"

## development

Please install the git hooks for development:

    chmod +x hooks/*
    cp hooks/* .git/hooks
