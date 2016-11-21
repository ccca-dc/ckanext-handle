from ckan.plugins.toolkit import missing
from ckanext.handle.lib import HandleService

from logging import getLogger
log = getLogger(__name__)
import pprint


def handle_pid_validator(key, data, errors, context):
    # if there was an error before calling our validator
    # don't bother with our validation
    value = data[key]
    resource_id = data.get(key[:-1] + ('id',))

    if (not value or value is missing) and resource_id:
        hdl = HandleService()
        data[key]=hdl.create_hdl_url(resource_id.encode('utf-8')[:8])
