# encoding: utf-8

import os
import json

import ckan.plugins.toolkit as tk
import ckan.logic as logic

from ckanext.handle.lib import HandleService

check_access = logic.check_access

_get_or_bust = logic.get_or_bust

NotAuthorized = logic.NotAuthorized
NotFound = logic.NotFound
Invalid = df.Invalid
ValidationError = logic.ValidationError


@ckan.logic.side_effect_free
def package_add_persistent_identifier(context, data_dict):
    '''If necessary, create a persistent handle identifier and add it to dataset metadata
    :param: the id of the dataset
    :type id: string
    :rtype: dict
    '''

    tk.check_access('package_update', context, data_dict)
    orig_data_dict = tk.get_action('package_show')(context, data_dict)

    # Is this active and public? If so we need to make sure we have an active PID
    if orig_data_dict.get('state', None) == 'active' and not orig_data_dict.get('private', False):
        hdl = HandleService()

        # If there is a pid available in the package metadata, check if it is registered within the handle service
        # If the pid is not registered do it now

        # When there is no pid available in package metadata, create one within the handle service and add
        # it to the package metadata
        pkg_pid = orig_data_dict.get(hdl.package_field, None)

        # Is there no pkg_pid -> Create new pkg_pid
        if not pkg_pid:
            pkg_pid = hdl.create_hdl_url(orig_data_dict['id'][:8])
            #toolkit.get_action('resource_update')(context,orig_res)

        # If we don't have a registered handle, register res_pid
        if not hdl.development:
            if not hdl.hdl_exists_from_url(pkg_pid):
                pkg_link = h.url_for_static_or_external(controller='package',
                                                        action='read',
                                                        id=pkg_id,
                                                        qualified = True)
                hdl.register_hdl_url(pkg_pid, pkg_link)
        else:
            pkg_link = h.url_for_static_or_external(controller='package',
                                                    action='read',
                                                    id=pkg_id,
                                                    qualified = True)
            log.debug('Register:' + pkg_link)

    elif orig_data_dict.get('state', None) == 'active' or orig_data_dict.get('private', True):
        # Not active or private Dataset raise NotAuthorized
        raise NotAuthorized('The dataset is not active or private. No pid was created.')


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
