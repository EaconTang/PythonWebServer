from wsgiref.simple_server import make_server, demo_app
from simple_app import simple_app
from WebApp2 import MyApp

server = make_server('', 8888, MyApp)
sockname = server.socket.getsockname()
print "Serving!" + sockname.__str__()
server.serve_forever()