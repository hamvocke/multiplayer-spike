from flask import Flask, render_template, redirect, url_for, abort, request, session
from flask_socketio import SocketIO, send, emit, join_room, leave_room
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecret'
app.debug = True
socketio = SocketIO(app)

all_games = {}

class Game(object):
    def __init__(self, slug: str):
        self.slug = slug
        self.players = {
            0: None,
            1: None,
            2: None,
            3: None
        }
class Player(object):
    def __init__(self, guid, session_id, name, state):
        self.guid = guid
        self.session_id = session_id
        self.name = name
        self.state = state

def generate_game_slug():
    yield "pasta-turtle"
    yield "cozy-dog"
    yield "bored-chimp"
    yield "lonely-mullet"

def serialize_players(players):
    allPlayers = {}
    for index, p in players.items():
        if p is None:
            allPlayers[index] = None
        else:
            allPlayers[index] = {"guid": p.guid, "name": p.name, "state": p.state}
    return allPlayers

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
    game = Game(slug)
    all_games[slug] = game
    print(f"created new game: {slug}")
    return redirect(url_for('game_view', game_slug=game.slug))


@app.route('/game/<game_slug>', methods=["GET"])
def game_view(game_slug):
    g = all_games.get(game_slug, None)

    if g is None:
        abort(404)

    return render_template('waiting_room.html', game_slug=g.slug)


@socketio.on('connect')
def on_connect():
    print("a new connection")


@socketio.on('join')
def on_join(data):
    print("join")

    payload = json.loads(data)
    player = Player(payload["player"]["guid"], request.sid, payload["player"]["name"], "online")
    game_slug = payload["game_slug"]

    join_room(game_slug)
    print(f"{player.name} joined {game_slug}")

    g = all_games.get(game_slug, None)

    if g is None:
        print("error")
        emit("error", f"game {game_slug} does not exist")
        return

    found = False

    for (i, p) in g.players.items():
        if p is not None and p.guid == player.guid:
            print("found existing player for this guid. updating")
            g.players[i] = p
            found = True
            break

    if not found:
        for index, p in g.players.items():
            if p is None:
                print("new player is unknown, adding as new player")
                g.players[index] = player
                break

    broadcast_data = json.dumps(serialize_players(g.players))
    print(f"player joined. broadcasting {broadcast_data}")
    emit("joined", broadcast_data, room=game_slug)


@socketio.on('click')
def on_click(data):
    print("someone clicked")
    payload = json.loads(data)
    player = payload["player"]

    emit("clicked", f"{player['name']} clicked", room=payload["game_slug"])


@socketio.on('disconnect')
def on_disconnect():
    print("a player left")

    for g in all_games.values():
        for p in g.players.values():
            if p is not None and p.session_id == request.sid:
                p.state = "offline"
                broadcast_data = json.dumps(serialize_players(g.players))
                print(f"broadcasting {broadcast_data} after leaving")
                emit("left", broadcast_data, room=g.slug)


if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 8000), app, handler_class=WebSocketHandler)
    server.serve_forever()