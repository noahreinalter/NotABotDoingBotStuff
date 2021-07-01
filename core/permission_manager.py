permissions_dict = {}


def add_permissions(permissions):
    for permission in permissions:
        if permission in permissions_dict:
            permissions_dict[permission] = permissions_dict[permission] + 1
        else:
            permissions_dict[permission] = 1


def remove_permissions(permissions):
    for permission in permissions:
        if permission in permissions_dict:
            if permissions_dict[permission] <= 1:
                del permissions_dict[permission]
            else:
                permissions_dict[permission] = permissions_dict[permission] - 1


def get_permissions():
    permissions_arg = {}
    for permission in permissions_dict:
        permissions_arg[permission] = True
    return permissions_arg
