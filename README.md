
ckanext-handle
============

The ckan plugin ckanext-handle adds the possibility to interact with a handle
service (https://www.handle.net/). It enables sysadmins to create, register,
update and delete handle records via the ckan API. The plugin automatically
creates a handle record for every dataset and all resources but only if the
resource is active and public.

Additionally the plugin provides a view-plugin citation_view which adds a
citation page for a resource.

There is the possibility to run ckanext-handle in a development mode without
connecting to the handle server. When a handle pid has to be registered, there
are debug logs instead the handle server interaction.

Requirements
----------------

This extension was tested with ckan 2.5.2 

This plugin is build on the b2handle library:
https://github.com/EUDAT-B2SAFE/B2HANDLE

Additionally it is usefull to use the HandleReverseLookupServlet:
https://github.com/EUDAT-B2SAFE/B2HANDLE-HRLS

Installation
----------------

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
----------------

These are the config settings for ckanext-handle:

    Required:
    ckanext.handle.handle_server_url = https://hdl.ccca.ac.at:8000
    ckanext.handle.private_key = path_to_privkey.pem
    ckanext.handle.certificate_only = path_to_certificate_only.pem
    ckanext.handle.prefix = 20.500.XXXXX
    ckanext.handle.proxy = https://hdl.handle.net
    ckanext.handle.resource_field = uri
    ckanext.handle.package_field = uri

    Optional: 
    If development is true no server interaction takes place, all
    events are logged to debug. 
    ckanext.handle.development = True

Development Installation
----------------

To install ckanext-handle for development, activate your CKAN virtualenv
and do:

    git clone https://github.com/ccca-dc/ckanext-handle.git
    cd ckanext-handle
    python setup.py develop
    pip install -r dev-requirements.txt
