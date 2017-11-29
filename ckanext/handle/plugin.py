import ckan.plugins as plugins
import ckan.plugins.toolkit as tk
import ckan.lib.helpers as h

from logging import getLogger

import ckanext.handle.logic.action as action
from ckanext.handle.lib import HandleService
import ckanext.handle.commands.handle as handle_action
import datetime

config = {}

import pprint

log = getLogger(__name__)


class ConfigError(Exception):
    pass

class HandlePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IConfigurable)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IResourceView, inherit=True)
    plugins.implements(plugins.IPackageController, inherit=True)

    ## IConfigurer
    def update_config(self, config_):
        tk.add_template_directory(config_, 'templates')
        tk.add_public_directory(config_, 'public')
        tk.add_resource('fanstatic', 'handle')


    ## IConfigurable
    def configure(self, main_config):
        """Implementation of IConfigurable.configure"""
        # Our own config schema, defines required items, default values and transform functions
        schema = {
            'ckanext.handle.handle_server_url': {'required': True},
            'ckanext.handle.private_key': {'required': True},
            'ckanext.handle.certificate_only': {'required': True},
            'ckanext.handle.prefix': {'required': True},
            'ckanext.handle.package_field': {'required': True},
            'ckanext.handle.resource_field': {'required': True},
            'ckanext.handle.development': {'default': False, 'parse': tk.asbool}
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

    # IActions
    def get_actions(self):
        actions = {'package_add_persistent_identifier': action.package_add_persistent_identifier}
        return actions

    ## IResourceView
    def info(self):
        return {'name': 'citation_view',
                'title': tk._('Citation'),
                'icon': 'pencil',
                'iframed': False,
                'requires_datastore': False,
                'default_title': tk._('Citation')
                }

    def can_view(self, data_dict):
        # Returning True says a that any resource can use this view type.
        # It will appear in every resource view dropdown.
        return True

    def view_template(self, context, data_dict):
        return 'citation_view.html'

    def setup_template_variables(self, context, data_dict):
        """Setup variables available to templates"""
        #log.debug(pprint.pprint(data_dict))
        hdl = HandleService()

        # Author name
        author_name = data_dict['package'].get('citation_info', '')
        if not author_name:
            author_name = 'Author name'

        # Publication year
        publication_year = data_dict['package'].get('iso_pubDate', '')
        if not publication_year:
            publication_year = "Publication year"
        else:
            publication_year = h.date_str_to_datetime(publication_year).year

        res_name = data_dict['resource'].get('name', '')
        res_id = tk.get_or_bust(data_dict['resource'],'id')
        ver_number = tk.get_action('resource_version_number')(context, {'id':res_id})
        res_pid = data_dict['resource'].get(hdl.resource_field, '')
        access_date =  datetime.datetime.now()

        tpl_variables = {
            'author_name': author_name,
            'publication_year': publication_year,
            'res_name': res_name,
            'ver_number': ver_number,
            'res_pid': res_pid,
            'access_date': access_date
        }

        return tpl_variables


    ## IPackageController
    def after_update(self, context, data_dict):
        """
        Dataset has been created / updated
        Check status of the dataset to determine if we should publish HANDLE
        PIDS to datacite network
        @param pkg_dict:
        @return: pkg_dict
        """
        tk.get_action('package_add_persistent_identifier')(context, data_dict)
