DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'decide',
        'USER': 'decide',
        'PASSWORD': 'decide',
        'HOST': 'localhost',
        'PORT': 5432,
    }
}

STATIC_ROOT = '/home/decide/static/'
MEDIA_ROOT = '/home/decide/static/media/'
ALLOWED_HOSTS = ['*']
ALLOWED_ORIGINS = ['http://*', 'https://*', 'https://localhost:8080', 'http://localhost:8080']
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_TRUSTED_ORIGINS = ALLOWED_ORIGINS.copy()

# Modules in use, commented modules that you won't use
MODULES = [
    'authentication',
    'base',
    'booth',
    'census',
    'mixnet',
    'postproc',
    'store',
    'visualizer',
    'voting',
    'home',
    'request',
]

BASEURL = 'http://localhost:8080'
APIS = {
    'authentication': BASEURL,
    'base': BASEURL,
    'booth': BASEURL,
    'census': BASEURL,
    'mixnet': BASEURL,
    'postproc': BASEURL,
    'store': BASEURL,
    'visualizer': BASEURL,
    'voting': BASEURL,
    'home': BASEURL,
    'request': BASEURL,
}

