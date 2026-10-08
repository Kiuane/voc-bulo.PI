"""
SERVIDOR FLASK
Liga o navegador à lógica do jogo (game_logic.py).

Rotas:
  GET  /               -> página do jogo
  GET  /api/state      -> estado atual da partida (cria uma se não existir)
  POST /api/new-game   -> começa uma nova partida
  POST /api/guess      -> envia uma tentativa  {"guess": "palavra"}
  POST /api/hint       -> usa a dica extra (nível 3+, uma vez por nível)
  POST /api/next       -> avança para a próxima palavra/nível
"""

import os
from collections import OrderedDict

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, session

from game_logic import Game, GameError

load_dotenv()  # lê o arquivo .env (se existir)

app = Flask(__name__)
# Chave usada para assinar o cookie de sessão (que guarda só o ID da partida).
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

# As partidas (com as respostas) ficam na memória do servidor, nunca no navegador.
GAMES = OrderedDict()
MAX_GAMES = 1000


def save_game(game):
    GAMES[game.id] = game
    while len(GAMES) > MAX_GAMES:      # evita crescer sem limite
        GAMES.popitem(last=False)
    session["gid"] = game.id


def current_game():
    game = GAMES.get(session.get("gid"))
    if game is None:
        game = Game()
        save_game(game)
    return game


@app.errorhandler(GameError)
def handle_game_error(error):
    return jsonify({"error": str(error)}), 400


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/state")
def api_state():
    return jsonify({"state": current_game().state()})


@app.post("/api/new-game")
def api_new_game():
    old = GAMES.get(session.get("gid"))
    used = old.used if old else set()          # evita repetir palavras da partida anterior
    game = Game(used)
    save_game(game)
    return jsonify({"state": game.state()})


@app.post("/api/guess")
def api_guess():
    game = current_game()
    data = request.get_json(silent=True) or {}
    game.guess(data.get("guess", ""))
    return jsonify({"state": game.state()})


@app.post("/api/hint")
def api_hint():
    game = current_game()
    game.use_hint()
    return jsonify({"state": game.state()})


@app.post("/api/next")
def api_next():
    game = current_game()
    transition = game.advance()                # "word", "level" ou "game"
    return jsonify({"state": game.state(), "transition": transition})


if __name__ == "__main__":
    app.run(debug=True, port=5000)