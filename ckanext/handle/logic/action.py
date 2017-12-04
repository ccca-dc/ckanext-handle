# -*- coding: utf-8 -*-

import os
import json

import ckan
import ckan.plugins.toolkit as tk
import ckan.logic as logic
import ckan.lib.helpers as h

from ckanext.handle.lib import HandleService

from logging import getLogger
log = getLogger(__name__)

check_access = logic.check_access

_get_or_bust = logic.get_or_bust

NotAuthorized = logic.NotAuthorized
NotFound = logic.NotFound
ValidationError = logic.ValidationError


@ckan.logic.side_effect_free
def package_add_persistent_identifier(context, data_dict):
    '''Check status of the dataset to determine, if it is necessary to
       create a persistent handle identifier and add it to dataset metadata.
    :param: the id of the dataset
    :type id: string
    '''

    tk.check_access('package_update', context, {'id': data_dict.get('id', None)})
    orig_data_dict = tk.get_action('package_show')(context, data_dict)

    # Is this active and public? If so we need to make sure we have an active PID
    if orig_data_dict.get('state', None) == 'active' and not orig_data_dict.get('private', False):
        hdl = HandleService()

        # Get pkg pid, None if there is no pid
        pkg_pid = data_dict.get(hdl.package_field, None)

        if not hdl.hdl_exists_from_url(pkg_pid):
            # If there is no pkg_pid -> Create new pkg_pid
            if not pkg_pid:
                pkg_pid = hdl.create_unique_hdl_url()

            # Create Link for package
            pkg_link = h.url_for_static_or_external(controller='package',
                                                    action='read',
                                                    id=orig_data_dict.get('id'),
                                                    qualified=True)
            # Register package link
            hdl.register_hdl_url(pkg_pid, pkg_link)
            orig_data_dict[hdl.package_field] = pkg_pid

            # package_update in after_update
            tk.get_action('package_update')(context, orig_data_dict)

    elif orig_data_dict.get('state', None) not in 'active' or orig_data_dict.get('private', True):
        # Not active or private Dataset
        pass


@ckan.logic.side_effect_free
def delete_persistent_identifier(context, data_dict):
    '''Delete the persistent identifier (only sysadmins)
    :param: hdl_url
    :type id: string
    :type hdl_url: string (A handle url e.g.: https://hdl.handle.net/20.500.11756/15aa58d5)
    '''
    tk.check_access('delete_persistent_identifier')
    hdl = HandleService()
    try:
        hdl.delete_hdl_url(data_dict['hdl_url'])
    except KeyError:
        ValidationError('Specifiy hdl_url in data_dict')


@ckan.logic.side_effect_free
def update_persistent_identifier(context, data_dict):
    '''Update the persistent identifier (only package latest version)
    :param: hdl_url, location
    :type hdl_url: string (A handle url e.g.: https://hdl.handle.net/20.500.11756/15aa58d5)
    :type location: string
    '''
    # tk.check_access('update_persistent_identifier')
    hdl = HandleService()
    try:
        hdl.update_hdl_url(data_dict['hdl_url'], data_dict['location'])
    except KeyError:
        ValidationError('Specifiy hdl_url in data_dict')
