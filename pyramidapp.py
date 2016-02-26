from pyramid.config import Configurator
from pyramid.response import Response

def Saluton(request):
    return Response(
        'Saluton from Pyramid!\n',
        content_type='text/plain',
    )

config = Configurator()
config.add_route('Saluton', '/Saluton')
config.add_view(Saluton, route_name='Saluton')
app = config.make_wsgi_app()