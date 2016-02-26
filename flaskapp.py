from flask import Flask
from flask import Response

flask_app = Flask('flaskapp')

@flask_app.route('/saluton')
def saluton():
    return Response(
        'Saluton form Flask!\n',
        mimetype='text/plain',
    )

# flask_app.wsgi_app(self,environ=, start_response=,)
app = flask_app.wsgi_app

