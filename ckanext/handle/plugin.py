import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.lib.helpers as h

from logging import getLogger

from ckanext.handle.lib import HandleService
from ckanext.handle.validation import handle_pid_validator
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
    plugins.implements(plugins.IValidators, inherit=True)
    plugins.implements(plugins.IResourceView, inherit=True)
    plugins.implements(plugins.IResourceController, inherit=True)
    plugins.implements(plugins.IPackageController, inherit=True)

    ## IConfigurer -----------------------------------------------------------------------
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'handle')


    ## IConfigurable ---------------------------------------------------------------------
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
            'ckanext.handle.development': {'default': False, 'parse': plugins.toolkit.asbool}
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


    ## IValidators
    def get_validators(self):
       return {'valid_handle_pid': handle_pid_validator}

    ## IResourceView
    def info(self):
        return {'name': 'citation_view',
                'title': plugins.toolkit._('Citation'),
                'icon': 'pencil',
                'iframed': False,
                'requires_datastore': False,
                'default_title': plugins.toolkit._('Citation')
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
        res_id = toolkit.get_or_bust(data_dict['resource'],'id')
        ver_number = toolkit.get_action('resource_version_number')(context, {'id':res_id})
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

    ## IResourceController ---------------------------------------------------------------
    def after_create(self, context, data_dict):
        # pkg_id = data_dict.get('package_id') pkg_dict =
        # toolkit.get_action('package_show')(context, {'id': pkg_id})
        # toolkit.get_action('package_update')(context, pkg_dict)
        # Unfortunatelly necessary for handle creation, because Resource ID is
        # not present during the creation process
        if 'type' not in data_dict:
            toolkit.get_action('resource_update')(context, data_dict)


    ## IPackageController ----------------------------------------------------------------
    def after_update(self, context, data_dict):
        """
        Dataset has been created / updated
        Check status of the dataset to determine if we should publish HANDLE
        PIDS to datacite network
        @param pkg_dict:
        @return: pkg_dict
        """
        if 'type' in data_dict and data_dict.get('type', None) == 'dataset':
            pkg_id = data_dict['id']
            # Load the original package, so we can determine if user has changed any fields
            orig_data_dict = toolkit.get_action('package_show')(context, {'id': pkg_id})
            resources = orig_data_dict['resources']
            hdl = HandleService()

            # Is this active and public? If so we need to make sure we have an active DOI
            if orig_data_dict.get('state', 'active') == 'active' and not orig_data_dict.get('private', False):
                for res in resources:
                    #res = toolkit.get_action('resource_update')(context, res)
                    res_pid = res.get(hdl.resource_field, '')

                    # Is there no res_pid -> Create new res_pid
                    # Needed, because validator does not have Resource UUID at first run
                    if not res_pid:
                        res_pid = hdl.create_hdl_url(res['id'][:8])
                        #toolkit.get_action('resource_update')(context,orig_res)

                    # If we don't have a registered handle, register res_pid
                    if not hdl.development:
                        if not hdl.hdl_exists_from_url(res_pid):
                            res_link = h.url_for_static_or_external(controller='package',
                                                                    action='resource_read',
                                                                    id=pkg_id,
                                                                    resource_id=res['id'],
                                                                    qualified = True)
                            hdl.register_hdl_url(res_pid, res_link)
                    else:
                        res_link = h.url_for_static_or_external(controller='package',
                                                                action='resource_read',
                                                                id=pkg_id,
                                                                resource_id=res['id'],
                                                                qualified = True)
                        log.debug('Register:' + res_link)

            elif orig_data_dict.get('state', 'active') == 'active' and orig_data_dict.get('private', False):
                # Not active or private Dataset (delete the handle PID) if it
                # exists
                for res in resources:
                    res_pid = res.get(hdl.resource_field, '')

                    # Is there no res_pid -> Create new res_pid
                    # Needed, because validator does not have Resource UUID at first run
                    if not res_pid:
	                    res_pid = hdl.create_hdl_url(res['id'][:8])
                    #log.debug('Delete:' + res[hdl.resource_field])
                    if not hdl.development:
                        if hdl.hdl_exists_from_url(res_pid):
                            hdl.delete_hdl_url(res_pid)
                    else:
                        log.debug('Delete:' + res.get(hdl.resource_field,''))
