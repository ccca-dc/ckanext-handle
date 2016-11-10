import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from logging import getLogger

from ckanext.handle.lib import HandleService

config = {}

import pprint

log = getLogger(__name__)


class ConfigError(Exception):
    pass

class HandlePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IConfigurable)
    #plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.IResourceController, inherit=True)

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'handle')

    def configure(self, main_config):
        """Implementation of IConfigurable.configure"""
        # From ckanext-ldap https://github.com/NaturalHistoryMuseum/ckanext-ldap
        # Our own config schema, defines required items, default values and transform functions
        schema = {
            'ckanext.handle.handle_server_url': {'required': True},
            'ckanext.handle.private_key': {'required': True},
            'ckanext.handle.certificate_only': {'required': True},
            'ckanext.handle.prefix': {'required': True},
            'ckanext.handle.package_field': {'required': True},
            'ckanext.handle.resource_field': {'required': True}
        }

        errors = []
        for i in schema:
            v = None
            if i in main_config:
                v = main_config[i]
            elif i.replace('ckanext.', '') in main_config:
                log.warning('HANDLE configuration options should be prefixed with \'ckanext.\'. ' +
                            'Please update {0} to {1}'.format(i.replace('ckanext.', ''), i))
                # Support handle.* options for backwards compatibility
                main_config[i] = main_config[i.replace('ckanext.', '')]
                v = main_config[i]

            if v:
                if 'parse' in schema[i]:
                    v = (schema[i]['parse'])(v)
                try:
                    if 'validate' in schema[i]:
                        (schema[i]['validate'])(v)
                    config[i] = v
                except ConfigError as e:
                    errors.append(str(e))
            elif schema[i].get('required', False):
                errors.append('Configuration parameter {} is required'.format(i))
            elif schema[i].get('required_if', False) and schema[i]['required_if'] in config:
                errors.append('Configuration parameter {} is required when {} is present'.format(i,
                    schema[i]['required_if']))
            elif 'default' in schema[i]:
                config[i] = schema[i]['default']
        if len(errors):
            raise ConfigError("\n".join(errors))


    ## IPackageController
    # def after_create(self, context, pkg_dict):
    #     """
    #     A new dataset has been created, so we need to create a new HANDLE PID
    #     NB: This is called after creation of a dataset, and before resources have been added so state = draft
    #     @param context:
    #     @param pkg_dict:
    #     @return:
    #     """
    #     data_dict = toolkit.get_action('package_show')(context, pkg_dict)
    #     log.debug(pprint.pprint(pkg_dict))


    # def after_update(self, context, pkg_dict):
    #     """
    #     Dataset has been created / updated
    #     Check status of the dataset to determine if we should publish DOI to datacite network

    #     @param pkg_dict:
    #     @return: pkg_dict
    #     """
    #     log.debug(pprint.pprint(pkg_dict))

    #     # Is this active and public? If so we need to make sure we have an active DOI
    #     if pkg_dict.get('state', 'active') == 'active' and not pkg_dict.get('private', False):
    #         package_id = pkg_dict['id']

    #         # Load the original package, so we can determine if user has changed any fields
    #         orig_pkg_dict = toolkit.get_action('package_show')(context, {'id': package_id})

    #         # If we don't have a DOI, create one
    #         # This could happen if the DOI module is enabled after a dataset has been creates
    #         package_pid = orig_pkg_dict['package_pid']

    #         if not package_pid:
    #             hdl = HandleService()
    #             orig_pkg_dict['package_pid'] = hdl.create_handle_identifier(package_id)

    #             toolkit.get_action('package_update')(context, orig_pkg_dict)
    #         # Is this an existing DOI? Update it
    #         # if doi.published:

    #         #     # Before updating, check if any of the metadata has been changed - otherwise
    #         #     # We end up sending loads of revisions to DataCite for minor edits
    #         #     # Load the current version
    #         #     orig_metadata_dict = build_metadata(orig_pkg_dict, doi)
    #         #     # Check if the two dictionaries are the same
    #         #     if cmp(orig_metadata_dict, metadata_dict) != 0:
    #         #         # Not the same, so we want to update the metadata
    #         #         update_doi(package_id, **metadata_dict)
    #         #         h.flash_success('DataCite DOI metadata updated')

    #         #     # TODO: If editing a dataset older than 5 days, create DOI revision

    #         # # New DOI - publish to datacite
    #         # else:
    #         #     h.flash_success('DataCite DOI created')
    #         #     publish_doi(package_id, **metadata_dict)

    #     return pkg_dict


    def after_create(self, context, res_dict):
        log.debug(pprint.pprint(res_dict))

        # Is this active and public? If so we need to make sure we have an active DOI
        # if res_dict.get('state', 'active') == 'active' and not res_dict.get('private', False):
        #     res_id = res_dict['id']

        #     # Load the original package, so we can determine if user has changed any fields
        #     orig_res_dict = toolkit.get_action('package_show')(context, {'id': res_id})

        #     # If we don't have a DOI, create one
        #     # This could happen if the DOI module is enabled after a dataset has been creates
        #     package_pid = res_dict['package_pid']

        #     if not package_pid:
        #         hdl = HandleService()
        #         res_dict['package_pid'] = hdl.create_handle_identifier(res_id)
