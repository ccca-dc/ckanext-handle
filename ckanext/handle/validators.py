
import ckan.plugins.toolkit as tk
from ckanext.scheming.validation import scheming_validator
import ckan.lib.navl.dictization_functions as df

def ignore_not_empty(key, data, errors, context):
    '''Ignore the field if the it was not empty or ignore_auth in context.'''
    if errors[key]:
        return

    data_dict = df.unflatten(data)
    orig_data_dict = tk.get_action('package_show')(context, {'id': data_dict.get('id', None)})

    ignore_auth = context.get('ignore_auth')

    if ignore_auth:
        return
#    data.pop(key)
