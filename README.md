Spike: A multiplayer-mode for Doppelkopf
========================================

I'm not good at thinking things through without having something to play around with. After hours of drawing boxes and arrows and getting nowhere, it's time to get my hands dirty to answer one of the most pressing questions of humanity: How could we build a multiplayer-mode for [doppelkopf.ham.codes](https://doppelkopf.ham.codes)?

This is a basic flask project serving a view that contains some JavaScript WebSocket code. The flask backend is using `Flask-Sockets` to handle WebSocket connections.

Starting the naked flask server (using `flask run` or `pipenv run flask run`) won't work here. Run the following to get started:

```
pipenv install
./start.sh
```

...and then go check out <http://localhost:8000> and open your browser console.