import constants


def get_full_path(relative_path):
    return "%s/%s" % (constants.storage_dir, relative_path)
