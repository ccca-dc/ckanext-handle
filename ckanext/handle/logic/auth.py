from ckan.plugins import toolkit as tk


@tk.auth_allow_anonymous_access
def delete_persistent_identifier(context, data_dict):
    """
    Can the user delete a persistent identifier. This is only available to
    system administrators.

    There is a shortcut where this will not be called for sysadmins
    """
    return {'success': False}

@tk.auth_allow_anonymous_access
def update_persistent_identifier(context, data_dict):
    """
    Can the user update a persistent identifier. This is only available to
    system administrators.

    There is a shortcut where this will not be called for sysadmins
    """
    return {'success': False}
