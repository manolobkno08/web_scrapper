import yaml

# Cachear config
__config = None


def config():
    """ Reads a yaml file and return a dictionary """
    global __config
    if not __config:
        with open('config.yaml', mode='r') as f:
            __config = yaml.safe_load(f)

    return __config
