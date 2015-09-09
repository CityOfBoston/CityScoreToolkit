import json

__secrets = {
    'secret_key': 'a',
}

def getter(path):
    try:
        with open(path) as handle:
            return json.load(handle)
    except IOError:
        return __secrets

def generator():

    # Based on Django's SECRET_KEY hash generator
    # https://github.com/django/django/blob/9893fa12b735f3f47b35d4063d86dddf3145cb25/django/core/management/commands/startproject.py

    from django.utils.crypto import get_random_string
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    __secrets['secret_key'] = get_random_string(50, chars)

    return __secrets

if __name__ == '__main__':
    data = json.dumps(generator())
    print(data)
