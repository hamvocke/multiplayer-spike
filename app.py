from flask import Flask, render_template
from flask_sockets import Sockets
import json

app = Flask(__name__)
sockets = Sockets(app)

game = None

@app.route('/')
def hello():
    return render_template('socket.html')

@sockets.route('/join')
def join_socket(ws):
    while not ws.closed:
        message = ws.receive()
        payload = json.loads(message)

        if payload["type"] == "game":
            print("received a game message")
            game = payload["game"]
        
        ws.send(json.dumps(game))


if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 8000), app, handler_class=WebSocketHandler)
    server.serve_forever()