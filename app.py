from flask import Flask, render_template, redirect, url_for, abort
from flask_sockets import Sockets
import json

app = Flask(__name__)
app.debug = True
sockets = Sockets(app)

all_games = {}

def generate_game_slug():
    yield "pasta-turtle"
    yield "cozy-dog"
    yield "bored-chimp"
    yield "lonely-mullet"


slug_generator = generate_game_slug()


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/socket')
def socket():
    return render_template('socket.html')


@app.route('/game/new', methods=["POST"])
def new_game():
    slug = next(slug_generator)
    all_games[slug] = { "slug": slug, "players": []}
    print(f"created new game: {slug}")
    return redirect(url_for('game', game_slug=slug))


@app.route('/game/<game_slug>', methods=["GET"])
def game(game_slug):
    g = all_games.get(game_slug, None)

    if g is None:
        abort(404)
    
    return render_template('waiting_room.html', game_slug=g["slug"], players=g["players"])


@sockets.route('/game/socket')
def game_socket(ws):
    while not ws.closed:
        message = ws.receive()

        payload = json.loads(message)
        print("received message " + message)


        if payload["type"] == "join":
            player = payload["name"]
            game_slug = payload["game_slug"]
            print(f"{player} joined {game_slug}")

            g = all_games.get(game_slug, None)

            if g is None:
                ws.send(json.dumps({"status": "error", "message": f"game {game_slug} does not exist"}))
            else:
                for client in ws.handler.server.clients.values():
                    client.ws.send(json.dumps({"status": "success", "message": g}))


if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 8000), app, handler_class=WebSocketHandler)
    server.serve_forever()