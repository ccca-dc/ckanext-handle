# -*- coding: utf-8 -*-

import os
import json
import copy

import ckan
import ckan.plugins.toolkit as tk
import ckan.logic as logic
import ckan.lib.helpers as h

from ckanext.handle.lib import HandleService

from logging import getLogger
log = getLogger(__name__)

NotAuthorized = logic.NotAuthorized
NotFound = logic.NotFound
ValidationError = logic.ValidationError


@ckan.logic.side_effect_free
def auto_create_persistent_identifier(context, data_dict):
    """Check status of the dataset to determine, if it is necessary to
       create persistent handle identifiers (including resource) and add
       it to dataset metadata.

    :param id: The id of the package
    :type id: string
    :returns:
    """
    tk.check_access('package_update', context, {'id': data_dict.get('id', None)})
    orig_data_dict = tk.get_action('package_show')(context, {'id': data_dict.get('id', None)})

    # Is this active and public? If so we need to make sure we have an active PID
    if orig_data_dict.get('state', None) == 'active' and not orig_data_dict.get('private', False):
        # Deepcopy dict
        pid_data_dict = copy.deepcopy(orig_data_dict)

        # Lists and dicts are mutable objects
        _package_persistent_identifier(pid_data_dict)
        _resource_persistent_identifier(pid_data_dict)

        # Some pids changed -> Update package
        if orig_data_dict != pid_data_dict:
            # package_update in after_update
            tk.get_action('package_update')(context, pid_data_dict)

    elif orig_data_dict.get('state', None) not in 'active' or orig_data_dict.get('private', True):
        # Not active or private Dataset
        pass


def _package_persistent_identifier(data_dict):
    """If it is necessary, create a persistent handle identifier
       and add it to package metadata.

    :param data_dict: The full package dictionary
    :type id: string
    :rtype: list of dicts
    """
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
                                                id=data_dict.get('id'),
                                                qualified=True)
        # Register package link
        hdl.register_hdl_url(pkg_pid, pkg_link)
        data_dict[hdl.package_field] = pkg_pid


def _resource_persistent_identifier(data_dict):
    """If it is necessary, create a persistent handle identifier
       and add it to resource metadata.

    :param data_dict: The full package dictionary
    :type id: string
    :rtype: list of dicts
    """
    hdl = HandleService()

    for res in data_dict.get('resources', None):
        res_pid = res.get(hdl.resource_field, None)

        if not hdl.hdl_exists_from_url(res_pid):
            # If there is no res_pid -> Create new res_pid
            if not res_pid:
                res_pid = hdl.create_unique_hdl_url()

            # Create Link for package
            res_link = h.url_for_static_or_external(controller='package',
                                                    action='resource_read',
                                                    id=res.get('package_id'),
                                                    resource_id=res.get('id'),
                                                    qualified = True)
            # Register package link
            hdl.register_hdl_url(res_pid, res_link)
            res[hdl.resource_field] = res_pid


@ckan.logic.side_effect_free
def create_persistent_identifier(context, data_dict):
    """Creates a unique persistent identifier without registering it

    :param location: The new URL for this hdl pid
    :type location: string
    :returns:
    :raises: KeyError
    """
    tk.check_access('create_persistent_identifier', context)
    hdl = HandleService()
    try:
        return hdl.create_unique_hdl_url()
    except:
        raise ValidationError('Something went wrong. Inspect your handle service')


@ckan.logic.side_effect_free
def register_persistent_identifier(context, data_dict):
    """Registers a persistent identifier

    :param hdl_url: A handle url e.g.: https://hdl.handle.net/20.500.11756/15aa58d5
    :type hdl_url: string
    :param location: The new URL for this hdl pid
    :type location: string
    :returns: bool -- the success code
    """
    tk.check_access('register_persistent_identifier', context)
    hdl = HandleService()
    try:
        return hdl.register_hdl_url(data_dict['hdl_url'], data_dict['location'])
    except KeyError:
        raise ValidationError('Specifiy hdl_url and location in data_dict')
    except:
        raise ValidationError('Could not register the persistent identifier')


@ckan.logic.side_effect_free
def update_persistent_identifier(context, data_dict):
    """Update the persistent identifier (only package latest version)

    :param hdl_url:
    :type hdl_url: string (A handle url e.g.: https://hdl.handle.net/20.500.11756/15aa58d5)
    :param location: The new URL for this hdl pid
    :type location: string
    """
    tk.check_access('update_persistent_identifier', context)
    hdl = HandleService()
    try:
        return hdl.update_hdl_url(data_dict['hdl_url'], data_dict['location'])
    except KeyError:
        raise ValidationError('Specifiy hdl_url and location in data_dict')
    except:
        raise ValidationError('Something went wrong. Inspect your handle service')


@ckan.logic.side_effect_free
def delete_persistent_identifier(context, data_dict):
    """Deletes the persistent identifier (only sysadmins)

    :param hdl_url: A handle url e.g.: https://hdl.handle.net/20.500.11756/15aa58d5
    :type hdl_url: string
    :returns:
    :raises: KeyError
    """
    tk.check_access('delete_persistent_identifier', context)
    hdl = HandleService()
    try:
        return hdl.delete_hdl_url(data_dict['hdl_url'])
    except KeyError:
        raise ValidationError('Specifiy hdl_url in data_dict')
    except:
        raise ValidationError('Something went wrong. Inspect your handle service')
