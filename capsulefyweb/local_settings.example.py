DEBUG=True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'capsulefy',
        'USER': 'user',
        'PASSWORD': 'password'
        'HOST': 'localhost',
        'PORT': '5432',
    }
}