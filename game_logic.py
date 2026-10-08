"""
LÓGICA DO JOGO
Este arquivo não depende do Flask: ele só sabe jogar.
O app.py apenas "conecta" a internet a este arquivo.
"""

import random
import unicodedata
import uuid
from collections import Counter

from words import THEMES

# ---------------------------------------------------------------------------
# Regras gerais
# ---------------------------------------------------------------------------
TOTAL_LEVELS = 10        # número de níveis
WORDS_PER_LEVEL = 2      # palavras por nível
HINT_FROM_LEVEL = 3      # a dica extra só existe a partir deste nível


def letters_for_level(level):
    """Nível 1 -> 4 letras, nível 2 -> 6, ..., nível 10 -> 22."""
    return 2 + 2 * level


def attempts_for_level(level):
    """Tentativas = quantidade de letras da palavra."""
    return letters_for_level(level)


class GameError(Exception):
    """Erro "esperado" (ex.: palavra com tamanho errado). A mensagem vai para o jogador."""


# ---------------------------------------------------------------------------
# Normalização
# ---------------------------------------------------------------------------
def normalize(text):
    """
    Deixa o texto em um formato único para comparação:
      1. NFD separa cada letra do seu acento ("ç" vira "c" + cedilha, "ã" vira "a" + til);
      2. removemos os acentos soltos (categoria Unicode "Mn");
      3. passamos para MAIÚSCULAS.
    Resultado: "Coração", "CORACAO" e "coracao" ficam todos como "CORACAO".
    """
    text = unicodedata.normalize("NFD", str(text))
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return text.strip().upper()


def is_only_letters(text):
    """True se o texto tem somente letras de A a Z (já normalizado)."""
    return text.isascii() and text.isalpha()


# ---------------------------------------------------------------------------
# Índice de palavras: {quantidade_de_letras: [palavras]}
# ---------------------------------------------------------------------------
def build_index():
    index = {}
    seen = set()
    for theme_key, info in THEMES.items():
        for word in info["palavras"]:
            answer = normalize(word)
            if not is_only_letters(answer) or answer in seen:
                continue  # ignora itens com espaço, hífen, repetidos...
            seen.add(answer)
            index.setdefault(len(answer), []).append(
                {
                    "display": word.upper(),   # versão COM acento, mostrada no fim da palavra
                    "answer": answer,          # versão normalizada, usada na comparação
                    "theme": theme_key,
                    "theme_hint": info["dica"],
                }
            )
    return index


WORD_INDEX = build_index()

# Garante, ao iniciar, que existem palavras suficientes para todos os níveis.
for _level in range(1, TOTAL_LEVELS + 1):
    if len(WORD_INDEX.get(letters_for_level(_level), [])) < WORDS_PER_LEVEL:
        raise RuntimeError(
            f"Faltam palavras de {letters_for_level(_level)} letras em words.py "
            f"(precisa de pelo menos {WORDS_PER_LEVEL})."
        )


def pick_words(level, used):
    """
    Sorteia 2 palavras com EXATAMENTE o tamanho do nível.
    - Evita palavras já usadas em partidas anteriores (conjunto `used`);
    - se acabarem as palavras novas daquele tamanho, permite repetir;
    - tenta usar temas diferentes nas duas palavras.
    """
    pool = WORD_INDEX[letters_for_level(level)]
    fresh = [w for w in pool if w["answer"] not in used]
    chosen = []
    while len(chosen) < WORDS_PER_LEVEL:
        candidates = [w for w in fresh if w not in chosen]
        if not candidates:
            candidates = [w for w in pool if w not in chosen]
        if chosen:
            other_theme = [w for w in candidates if w["theme"] != chosen[0]["theme"]]
            candidates = other_theme or candidates
        chosen.append(random.choice(candidates))
    return chosen


def make_extra_hint(answer):
    """Escolhe automaticamente uma dica extra que NÃO revela a palavra inteira."""
    vowels = sum(1 for ch in answer if ch in "AEIOU")
    middle = random.randint(1, len(answer) - 2)
    options = [
        f"A palavra começa com a letra {answer[0]}.",
        f"A palavra termina com a letra {answer[-1]}.",
        f"A palavra tem {vowels} vogais (contando repetidas).",
        f"A {middle + 1}ª letra da palavra é {answer[middle]}.",
    ]
    return random.choice(options)


# ---------------------------------------------------------------------------
# Comparação da tentativa com a resposta
# ---------------------------------------------------------------------------
def evaluate(guess, answer):
    """
    Devolve uma lista com "correct", "present" ou "absent" para cada posição.
    Funciona com letras repetidas (como no Termo):
      1ª passada: marca as letras corretas na posição certa;
      2ª passada: marca como "present" só enquanto ainda sobrar a letra na resposta.
    """
    size = len(answer)
    result = ["absent"] * size
    remaining = Counter()

    for i in range(size):
        if guess[i] == answer[i]:
            result[i] = "correct"
        else:
            remaining[answer[i]] += 1

    for i in range(size):
        if result[i] == "correct":
            continue
        if remaining[guess[i]] > 0:
            result[i] = "present"
            remaining[guess[i]] -= 1

    return result


# ---------------------------------------------------------------------------
# Uma partida completa
# ---------------------------------------------------------------------------
class Game:
    def __init__(self, used=None):
        self.id = uuid.uuid4().hex
        self.used = set(used or [])        # palavras já usadas (inclui partidas anteriores)

        # Sorteia as 20 palavras da partida. Ficam SÓ no servidor.
        self.levels = []
        for level in range(1, TOTAL_LEVELS + 1):
            words = []
            for w in pick_words(level, self.used):
                self.used.add(w["answer"])
                words.append(dict(w, extra_hint=make_extra_hint(w["answer"])))
            self.levels.append(words)

        self.level = 1
        self.word_index = 0                # 0 = primeira palavra do nível, 1 = segunda
        self.guesses = []                  # tentativas da palavra atual
        self.word_status = "playing"       # playing | won | lost
        self.hint_used_level = False       # a dica já foi usada neste nível?
        self.hint_text = None              # texto da dica usada na palavra atual
        self.score = 0                     # palavras acertadas
        self.finished = False

    # -- atalhos ------------------------------------------------------------
    @property
    def current(self):
        return self.levels[self.level - 1][self.word_index]

    @property
    def letters(self):
        return letters_for_level(self.level)

    @property
    def max_attempts(self):
        return attempts_for_level(self.level)

    # -- estado enviado ao navegador (NUNCA inclui a resposta enquanto joga) --
    def state(self):
        over = self.word_status != "playing"
        return {
            "level": self.level,
            "total_levels": TOTAL_LEVELS,
            "word_number": self.word_index + 1,
            "words_per_level": WORDS_PER_LEVEL,
            "letters": self.letters,
            "max_attempts": self.max_attempts,
            "attempts_used": len(self.guesses),
            "theme_hint": self.current["theme_hint"],
            "hint_available": self.level >= HINT_FROM_LEVEL,
            "hint_used": self.hint_used_level,
            "hint_text": self.hint_text,
            "guesses": self.guesses,
            "word_status": self.word_status,
            "answer": self.current["display"] if over else None,
            "finished": self.finished,
            "score": self.score,
            "total_words": TOTAL_LEVELS * WORDS_PER_LEVEL,
        }

    # -- ações ----------------------------------------------------------------
    def guess(self, raw):
        if self.finished:
            raise GameError("O jogo já terminou. Comece uma nova partida.")
        if self.word_status != "playing":
            raise GameError("Esta palavra já foi encerrada. Clique em continuar.")

        guess = normalize(raw or "")
        if not guess:
            raise GameError("Digite uma palavra antes de enviar.")
        if not is_only_letters(guess):
            raise GameError("Use apenas letras (sem números, espaços ou símbolos).")
        if len(guess) != self.letters:
            raise GameError(f"A palavra precisa ter exatamente {self.letters} letras.")

        answer = self.current["answer"]
        status = evaluate(guess, answer)
        self.guesses.append({"letters": guess, "status": status})

        if guess == answer:
            self.word_status = "won"
            self.score += 1
        elif len(self.guesses) >= self.max_attempts:
            self.word_status = "lost"

    def use_hint(self):
        if self.finished:
            raise GameError("O jogo já terminou.")
        if self.level < HINT_FROM_LEVEL:
            raise GameError(f"A dica extra só fica disponível a partir do nível {HINT_FROM_LEVEL}.")
        if self.word_status != "playing":
            raise GameError("Esta palavra já foi encerrada.")
        if self.hint_used_level:
            raise GameError("Você já usou a dica deste nível.")
        self.hint_used_level = True
        self.hint_text = self.current["extra_hint"]

    def advance(self):
        """Vai para a próxima palavra/nível. Devolve 'word', 'level' ou 'game'."""
        if self.finished:
            raise GameError("O jogo já terminou.")
        if self.word_status == "playing":
            raise GameError("Termine a palavra atual antes de continuar.")

        self.guesses = []
        self.word_status = "playing"
        self.hint_text = None

        if self.word_index < WORDS_PER_LEVEL - 1:
            self.word_index += 1
            return "word"
        if self.level == TOTAL_LEVELS:
            self.finished = True
            return "game"
        self.level += 1
        self.word_index = 0
        self.hint_used_level = False       # a dica volta a ficar disponível
        return "level"