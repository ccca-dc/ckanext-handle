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
    :rtype: dict
    '''

    tk.check_access('package_update', context, {'id': data_dict.get('id', None)})
    orig_data_dict = tk.get_action('package_show')(context, data_dict)

    # Is this active and public? If so we need to make sure we have an active PID
    if orig_data_dict.get('state', None) == 'active' and not orig_data_dict.get('private', False):
        hdl = HandleService()

        # If there is a pid available in the package metadata, check if it is registered 
        # within the handle service. If the pid is not registered do it now

        # When there is no pid available in package metadata, create one within the handle service and add
        # it to the package metadata
        pkg_pid = data_dict.get(hdl.package_field, None)

        # If we don't have a registered handle, register res_pid
        if not hdl.development:
            # There is no pkg_pid -> Create new pkg_pid
            if not pkg_pid:
                pkg_pid = hdl.create_hdl_url(data_dict['id'][:8])

            if not hdl.hdl_exists_from_url(pkg_pid):
                pkg_link = h.url_for_static_or_external(controller='package',
                                                        action='read',
                                                        id=orig_data_dict.get('id'),
                                                        qualified = True)
                hdl.register_hdl_url(pkg_pid, pkg_link)
                orig_data_dict[hdl.package_field] = pkg_pid
                # package_update in after_update, but only once no endless loop
                tk.get_action('package_update')(context, orig_data_dict)
        elif hdl.development and not pkg_pid:
            # There is no pkg_pid -> Create new pkg_pid
            pkg_pid = hdl.create_hdl_url(data_dict['id'][:8])

            pkg_link = h.url_for_static_or_external(controller='package',
                                                    action='read',
                                                    id=orig_data_dict.get('id'),
                                                    qualified = True)

            orig_data_dict[hdl.package_field] = pkg_pid
            # Maybe this won't work because we call this api action in after_update (recursive)
            log.debug('Register:' + pkg_link)
            tk.get_action('package_update')(context, orig_data_dict)



    elif orig_data_dict.get('state', None) not in 'active' or orig_data_dict.get('private', True):
        # Not active or private Dataset
        pass


def delete_persistent_identifier(context, data_dict):
    '''Return the layers of a resource from Thredds WMS.
    Exclude lat, lon, latitude, longitude, x, y

    :param: the id of the resource
    :type id: string
    :rtype: list
    '''
    pass


@ckan.logic.side_effect_free
def search_persistent_identifier(context, data_dict):
    '''Return the layers of a resource from Thredds WMS.
    Exclude lat, lon, latitude, longitude, x, y

    :param: the id of the resource
    :type id: string
    :rtype: list
    '''
    pass
