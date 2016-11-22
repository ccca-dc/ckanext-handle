import logging
import pprint
import pylons
from ckan.lib.cli import CkanCommand
from ckanext.datastore.db import _get_engine
from ckan.plugins import toolkit
from ckan import logic

log = logging.getLogger()

class HANDLECommand(CkanCommand):
    """

    Paster function to add handle PID to existing resources.
    The funcion updates all existing resources, therefore the validator creates the Handle PIDs.

    Commands:
        paster handle create-pid -c /etc/ckan/default/development.ini

    """
    summary = __doc__.split('\n')[0]
    usage = __doc__


    def command(self):

        if not self.args or self.args[0] in ['--help', '-h', 'help']:
            print self.__doc__
            return

        self._load_config()

        # Set up context
        user = toolkit.get_action('get_site_user')({'ignore_auth': True}, {})
        self.context = {'user': user['name']}

        cmd = self.args[0]

        if cmd == 'create-pid':
            self.create_pid()
        else:
            print 'Command %s not recognized' % cmd

    def create_pid(self):
        try:
            pkg_list = toolkit.get_action('package_list')(self.context, {})
            pprint.pprint(pkg_list)
            for name in pkg_list:
                pkg_dict = toolkit.get_action('package_show')(self.context, {'id':name})
                pprint.pprint(pkg_dict)
                toolkit.get_action('package_update')(self.context, pkg_dict)
        except logic.NotFound:
            print "Error"
            # toolkit.get_action('organization_create')(self.context, {'id': organization_id, 'name': organization_id})
