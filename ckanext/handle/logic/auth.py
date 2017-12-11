from ckan.plugins import toolkit as tk

@tk.auth_disallow_anonymous_access
def create_persistent_identifier(context, data_dict):
    """
    Can the user create a persistent identifier. This is only available for
    registered users.

    There is a shortcut where this will not be called for sysadmins
    """
    return {'success': True}

@tk.auth_disallow_anonymous_access
def register_persistent_identifier(context, data_dict):
    """
    Can the user register a persistent identifier. This is only available for
    system administrators.

    There is a shortcut where this will not be called for sysadmins
    """
    return {'success': False}

@tk.auth_disallow_anonymous_access
def update_persistent_identifier(context, data_dict):
    """
    Can the user update a persistent identifier. This is only available for
    system administrators.

    There is a shortcut where this will not be called for sysadmins
    """
    return {'success': False}

@tk.auth_disallow_anonymous_access
def delete_persistent_identifier(context, data_dict):
    """
    Can the user delete a persistent identifier. This is only available for
    system administrators.

    There is a shortcut where this will not be called for sysadmins
    """
    return {'success': False}
