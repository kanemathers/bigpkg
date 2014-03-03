from pyramid.config import Configurator

from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application. """

    engine = engine_from_config(settings, 'sqlalchemy.')

    DBSession.configure(bind=engine)

    Base.metadata.bind = engine

    config = Configurator(settings=settings)

    config.add_static_view('static', 'static', cache_max_age=3600)

    config.add_route('client.download', '/client.tar.gz')
    config.add_route('custom.sh', '/custom.sh')

    config.add_route('packages.list', '/packages')
    config.add_route('packages.download', '/packages/{package}.tar.gz')

    config.scan()

    return config.make_wsgi_app()
