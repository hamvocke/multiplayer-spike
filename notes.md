Notes
=====

* when using `flask`, we get two options:
    1. Flask-Sockets - bare websocket implementation, not a lot of convenience, slim, not a lot of documentation
    2. Flask-SocketIO - socket.io, lot of convenience, fallbacks, opinionated protocols, but bloated and maybe not even needed in 2020
* `Django` seems to bring something more opinionated out of the box, using ASGI support: Channels
* the current backend is super primitive - this _might_ still be the right time to switch to `Django` if the Channels implementation is much better than Flask-Socket or Flask-SocketIO
* socket.io comes with a natural way of handling "rooms" - websocket messages only get broadcasted within a specific room. this is something we'd have to implement with pure Websockets ourselves (e.g. by providing particular routes per "room"). Channels seems to support this, Flask not so much

## To spike
* connect via WS to a 'channel' / endpoint
* create two of these channels
* connect multiple clients to each
* send message over a channel
* broadcast
* make sure only clients connected to that channel receive the message

## Design

* a "room" that people can join and exchange messages (join, leave, play card, make announcement) in. should probably be called `table` to stick to Doppelkopf lingo
* `connect` means joining
* `disconnect` means leaving
* `play a card`, `make announcement`, `start game`  are custom events
* the `table` component will show a `waiting room` component until the game is started
* if 4 players are on a table, a game can be started
* once a game is started, the `table` component shows the `game` instead of the `waiting room`
* if 4 players are on a table, no further player can join
* first player who joins becomes the owner
* when connecting, we generate a player id and store it in a cookie so we can reconnect the right players
* how to deal with disconnects? quit game? let players join again? allow other players to take over?
* how do things scale? with stateful connections, horizontal scaling becomes far less trivial and requires coordination between servers

## Events 

### Table-specific
_All messages are sent for a specific table_

| event name | description | payload |
| ---------- | ----------- | --- |
| `join table` | a player joins a table | player info (name, id) |
| `joined table` | broadcast, a player joined a table | table owner's game state |
| `leave table` | a player leaves a table | player info (id) |
| `left table` | broadcast, a player left a table | player info (id) |
| `play card` | a player plays a card | player id, card |
| `played card` | broadcast, a player played a card | player id, card |
| `make announcement` | a player makes an announcement | player id, announcement |
| `made announcement` | broadcast, a player made an announcement | player id, announcement |
| `start game` | the owner starts the game | |
| `started game` | broadcast, the owner starts the game | |
| `finish round` | the owner finished the round | |
| `finish round` | broadcast, the owner finished the round | |
| `start next round` | the owner starts the next round | |
| `started next round` | broadcast, the owner started the next round | |


### `Connect`
* if first player:
    * create player as owner
    * create table
* if 2nd to 4th player:
    * check that table exists and hasn't been started yet
    * check if there's a disconnected player we're waiting for to rejoin
    * if so, check that they sent the right name/token/id
    * attach player to table
    * broadcast to all players on table
* if 5+th player or table has already started
    * refuse connection

### `Disconnect`
* if last player:
    * close table, save timestamp
* if 2nd - 4th player:
    * remember player name (or token, id?)
    * whenever they reconnect, check that id, token, name is correct

### `start game`
* send owner's entire game state
* broadcast entire game state to _all_ players on the table

### `change name`
* verify that game hasn't been started yet
* broadcast player, new name to all players on the table
* client-side: update player name in all game instances

### `Play card`
* broadcast player, card to all players on the table

### `make announcement`
* broadcast player, announcement to all players on the table

### `finish round`
* validate that it's initiated by owner
* broadcast to all players on table
* client: display scorecard

### `next round`
* validate that it's initiated by owner
* start new round on owner's client-side
* send entire game state of owner
* broadcast game state to all players on table
* client: start next round with provided state (effectively: players and their hands need to be set)
