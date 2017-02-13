----------------
ckanext-handle
----------------

The ckan plugin ckanext-handle adds the possibility to interact with a handle
service. Creation, deletion and search of handle records. The plugin creates a
handle record for every resource only if the resource is active and public. It
deletes the handle record if the resources status is set to private.

The plugin offers a ckan validator and a scheming preset for the creation of a
handle record when the resource is created within ckan.

Additionally the plugin provides a view-plugin citation_view which adds a
citation page for a resource.

Requirements
============

This extension was tested with ckan 2.5.2 

This plugin is build on the b2handle library:
https://github.com/EUDAT-B2SAFE/B2HANDLE

Additionally it is usefull to use the HandleReverseLookupServlet:
https://github.com/EUDAT-B2SAFE/B2HANDLE-HRLS

Installation
============

To install ckanext-handle:

1.  Activate your CKAN virtual environment, for example:

        . /usr/lib/ckan/default/bin/activate

2.  Install the ckanext-handle Python package into your virtual
    environment:
    
        pip install -r requirements.txt
        cd ckanext-handle
        python setup.py install

3.  Add `handle` to the `ckan.plugins` setting in your CKAN config file
    (by default the config file is located at
    `/etc/ckan/default/production.ini`).
    If you want to use the citation-view add `citation_view` to `ckan.views`.
4.  Restart CKAN. For example if you've deployed CKAN with Apache on
    Ubuntu:

        sudo service apache2 reload

Config Settings
===============

These are the config settings for ckanext-handle:

    # The minimum number of hours to wait before re-checking a resource
    # (optional, default: 24).
    Required:
    ckanext.handle.handle_server_url = https://hdl.ccca.ac.at:8000
    ckanext.handle.private_key = path_to_privkey.pem
    ckanext.handle.certificate_only = path_to_certificate_only.pem
    ckanext.handle.prefix = 20.500.XXXXX
    ckanext.handle.proxy = https://hdl.handle.net
    ckanext.handle.resource_field = pid_resource
    ckanext.handle.package_field =  pid_dataset

    Optional: 
    If development is true no server interaction takes place, all
    events are logged to debug. 
    ckanext.handle.development = True

Development Installation
========================

To install ckanext-handle for development, activate your CKAN virtualenv
and do:

    git clone https://github.com/sureL89/ckanext-handle.git
    cd ckanext-handle
    python setup.py develop
    pip install -r dev-requirements.txt

Running the Tests
=================

To run the tests, do:

    nosetests --nologcapture --with-pylons=test.ini

To run the tests and produce a coverage report, first make sure you have
coverage installed in your virtualenv (`pip install coverage`) then run:

    nosetests --nologcapture --with-pylons=test.ini --with-coverage --cover-package=ckanext.handle --cover-inclusive --cover-erase --cover-tests

---------------------------------Registering ckanext-handle on PyPI
---------------------------------

ckanext-handle should be availabe on PyPI as
<https://pypi.python.org/pypi/ckanext-handle>. If that link doesn't
work, then you can register the project on PyPI for the first time by
following these steps:

1.  Create a source distribution of the project:

        python setup.py sdist

2.  Register the project:

        python setup.py register

3.  Upload the source distribution to PyPI:

        python setup.py sdist upload

4.  Tag the first release of the project on GitHub with the version
    number from the `setup.py` file. For example if the version number
    in `setup.py` is 0.0.1 then do:

        git tag 0.0.1
        git push --tags

----------------------------------------Releasing a New Version of
ckanext-handle ----------------------------------------

ckanext-handle is availabe on PyPI as
<https://pypi.python.org/pypi/ckanext-handle>. To publish a new version
to PyPI follow these steps:

1.  Update the version number in the `setup.py` file. See [PEP
    440](http://legacy.python.org/dev/peps/pep-0440/#public-version-identifiers)
    for how to choose version numbers.
2.  Create a source distribution of the new version:

        python setup.py sdist

3.  Upload the source distribution to PyPI:

        python setup.py sdist upload

4.  Tag the new release of the project on GitHub with the version number
    from the `setup.py` file. For example if the version number in
    `setup.py` is 0.0.2 then do:

        git tag 0.0.2
        git push --tags


