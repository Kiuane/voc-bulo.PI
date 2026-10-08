/*
  FRONTEND DO JOGO
  Este arquivo só cuida da tela: desenhar a grade, capturar o teclado e animar.
  Toda a lógica importante (respostas, níveis, tentativas, dicas) fica no Python.
*/
(() => {
  "use strict";

  const KEY_ROWS = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"];

  let S = null;           // estado atual vindo do servidor
  let current = "";       // letras digitadas na linha atual
  let busy = false;       // true enquanto espera o servidor / animações
  let overlayOpen = false;
  let rowDivs = [];       // elementos de cada linha da grade
  let tileEls = [];       // tileEls[linha][coluna]

  const $ = (id) => document.getElementById(id);
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  // ---------------------------------------------------------------- utilidades
  async function api(path, method = "GET", body) {
    const res = await fetch(path, {
      method,
      headers: { "Content-Type": "application/json" },
      body: body ? JSON.stringify(body) : undefined,
    });
    let data = {};
    try { data = await res.json(); } catch (_) { /* resposta sem JSON */ }
    if (!res.ok) throw new Error(data.error || "Algo deu errado. Tente novamente.");
    return data;
  }

  function el(tag, cls, text) {
    const e = document.createElement(tag);
    e.className = cls || "";
    if (text !== undefined) e.textContent = text;
    return e;
  }

  // Reinicia uma animação CSS (remove, força o navegador a "perceber", e adiciona).
  function play(element, cls) {
    if (!element) return;
    element.classList.remove(cls);
    void element.offsetWidth;
    element.classList.add(cls);
  }

  function toast(msg) {
    const t = $("toast");
    t.textContent = msg;
    t.classList.remove("hidden");
    play(t, "animate-pop");
    clearTimeout(toast.timer);
    toast.timer = setTimeout(() => t.classList.add("hidden"), 2400);
  }

  // Normaliza uma tecla do teclado físico: "ç" -> "C", "Á" -> "A"...
  function keyToLetter(key) {
    if (key.length !== 1) return "";
    const ch = key.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toUpperCase();
    return /^[A-Z]$/.test(ch) ? ch : "";
  }

  // ---------------------------------------------------------------- tamanhos
  // Palavras longas precisam de quadrados menores para caber em telas pequenas.
  function sizing(n) {
    const w = (rem) => `w-[min(100%,${(n * rem).toFixed(1)}rem)]`;
    if (n <= 6)  return { gap: "gap-1.5",    text: "text-2xl sm:text-3xl",  round: "rounded-lg", border: "border-2", width: w(3.6) };
    if (n <= 10) return { gap: "gap-1",      text: "text-xl sm:text-2xl",   round: "rounded-md", border: "border-2", width: w(3.1) };
    if (n <= 14) return { gap: "gap-[3px]",  text: "text-sm sm:text-xl",    round: "rounded",    border: "border-2", width: w(2.7) };
    if (n <= 18) return { gap: "gap-[2px]",  text: "text-[11px] sm:text-base", round: "rounded-sm", border: "border",   width: w(2.4) };
    return              { gap: "gap-[2px]",  text: "text-[9px] sm:text-sm", round: "rounded-sm", border: "border",   width: w(2.2) };
  }

  const TILE_KINDS = {
    empty:   "bg-white/50 border-brand-brown/30 text-ink",
    typed:   "bg-white/90 border-brand-brown text-ink",
    correct: "bg-brand-blue border-brand-blue text-ink",
    present: "bg-brand-pink border-brand-pink text-ink",
    absent:  "bg-brand-brown border-brand-brown text-brand-cream",
  };

  function tileClass(kind) {
    const z = sizing(S.letters);
    return `aspect-square flex items-center justify-center font-extrabold uppercase select-none transition-colors ${z.round} ${z.border} ${z.text} ${TILE_KINDS[kind]}`;
  }

  // ---------------------------------------------------------------- grade
  function buildBoard() {
    const board = $("board");
    board.replaceChildren();
    rowDivs = [];
    tileEls = [];
    const n = S.letters;
    const z = sizing(n);

    for (let r = 0; r < S.max_attempts; r++) {
      const row = el("div", `grid ${z.gap} ${z.width} grid-cols-[repeat(${n},minmax(0,1fr))]`);
      const tiles = [];
      for (let c = 0; c < n; c++) {
        const guess = S.guesses[r];
        const tile = el("div", tileClass(guess ? guess.status[c] : "empty"), guess ? guess.letters[c] : "");
        row.appendChild(tile);
        tiles.push(tile);
      }
      board.appendChild(row);
      rowDivs.push(row);
      tileEls.push(tiles);
    }
    paintCurrent(false);
  }

  // Mostra na linha atual as letras que o jogador está digitando.
  function paintCurrent(animate) {
    const r = S.guesses.length;
    if (r >= S.max_attempts) return;
    tileEls[r].forEach((tile, c) => {
      const letter = current[c] || "";
      tile.textContent = letter;
      tile.className = tileClass(letter ? "typed" : "empty");
      if (animate && c === current.length - 1) play(tile, "animate-pop");
    });
    if (rowDivs[r]) rowDivs[r].scrollIntoView({ block: "center", behavior: "smooth" });
  }

  // Animação de "virar" cada quadrado e mostrar a cor. Devolve o tempo total (ms).
  function revealRow(r, statuses) {
    const step = S.letters > 12 ? 55 : 130;
    tileEls[r].forEach((tile, i) => {
      tile.style.animationDelay = `${i * step}ms`;
      play(tile, "animate-flip");
      setTimeout(() => { tile.className = tileClass(statuses[i]) + " animate-flip"; }, i * step + 250);
    });
    return (S.letters - 1) * step + 600;
  }

  function celebrate(r) {
    tileEls[r].forEach((tile, i) => {
      tile.style.animationDelay = `${i * 40}ms`;
      play(tile, "animate-hop");
    });
  }

  // ---------------------------------------------------------------- teclado
  function buildKeyboard() {
    const kb = $("keyboard");
    kb.replaceChildren();

    KEY_ROWS.forEach((letters, idx) => {
      const row = el("div", "flex gap-1 justify-center");
      for (const ch of letters) row.appendChild(makeKey(ch, ch));
      if (idx === 2) row.appendChild(makeKey("⌫", "BACK", true));
      kb.appendChild(row);
    });

    const send = el("button",
      "h-12 w-full rounded-lg bg-brand-brown text-base font-extrabold tracking-wide text-brand-cream shadow transition hover:brightness-110 active:scale-95",
      "ENVIAR");
    send.id = "send-btn";
    send.addEventListener("click", submit);
    kb.appendChild(send);
  }

  const KEY_BASE = "h-11 flex-1 rounded-md text-sm font-bold shadow-sm transition active:scale-90 sm:h-12 sm:text-base ";
  const KEY_KINDS = {
    none:    "bg-brand-brown/15 text-ink",
    correct: "bg-brand-blue text-ink",
    present: "bg-brand-pink text-ink",
    absent:  "bg-brand-brown text-brand-cream",
  };

  function makeKey(label, value, wide) {
    const b = el("button", KEY_BASE + KEY_KINDS.none + (wide ? " flex-[1.5]" : ""), label);
    b.dataset.key = value;
    b.addEventListener("click", () => handleKey(value));
    return b;
  }

  // Cada tecla ganha a melhor cor já descoberta naquela letra.
  function updateKeys() {
    const rank = { absent: 1, present: 2, correct: 3 };
    const best = {};
    for (const g of S.guesses) {
      g.letters.split("").forEach((ch, i) => {
        const st = g.status[i];
        if (!best[ch] || rank[st] > rank[best[ch]]) best[ch] = st;
      });
    }
    document.querySelectorAll("#keyboard [data-key]").forEach((b) => {
      const key = b.dataset.key;
      if (key.length !== 1) return;
      const wide = b.className.includes("flex-[1.5]") ? " flex-[1.5]" : "";
      b.className = KEY_BASE + KEY_KINDS[best[key] || "none"] + wide;
    });
  }

  // ---------------------------------------------------------------- informações
  function refreshInfo() {
    $("info-level").textContent = `${S.level}/${S.total_levels}`;
    $("info-word").textContent = `${S.word_number}/${S.words_per_level}`;
    $("info-attempts").textContent = `${S.attempts_used}/${S.max_attempts}`;
    $("theme-hint").textContent = S.theme_hint;
    $("letters-info").textContent = `${S.letters} letras • ${S.max_attempts} tentativas`;

    const hintBtn = $("hint-btn");
    hintBtn.classList.toggle("hidden", !S.hint_available);
    hintBtn.disabled = S.hint_used || S.word_status !== "playing";
    hintBtn.textContent = S.hint_used ? "Dica deste nível já usada" : "Pedir dica extra (1 por nível)";

    const hintText = $("hint-text");
    if (S.hint_text) {
      hintText.textContent = "Dica extra: " + S.hint_text;
      hintText.classList.remove("hidden");
    } else {
      hintText.classList.add("hidden");
    }
  }

  function render() {
    current = "";
    buildBoard();
    refreshInfo();
    updateKeys();
    play($("board"), "animate-fadein");
  }

  // ---------------------------------------------------------------- ações do jogador
  function handleKey(value) {
    if (busy || overlayOpen || !S || S.finished || S.word_status !== "playing") return;
    if (value === "BACK") {
      current = current.slice(0, -1);
      paintCurrent(false);
    } else if (value === "ENTER") {
      submit();
    } else if (current.length < S.letters) {
      current += value;
      paintCurrent(true);
    }
  }

  async function submit() {
    if (busy || overlayOpen || !S || S.word_status !== "playing") return;
    const r = S.guesses.length;

    if (current.length === 0) {
      toast("Digite uma palavra antes de enviar.");
      play(rowDivs[r], "animate-shake");
      return;
    }
    if (current.length !== S.letters) {
      toast(`A palavra precisa ter ${S.letters} letras (você digitou ${current.length}).`);
      play(rowDivs[r], "animate-shake");
      return;
    }

    busy = true;
    try {
      const data = await api("/api/guess", "POST", { guess: current });
      S = data.state;
      current = "";
      await sleep(revealRow(r, S.guesses[r].status));
      refreshInfo();
      updateKeys();

      if (S.word_status === "won") {
        celebrate(r);
        await sleep(700);
      }
      if (S.word_status !== "playing") showWordResult();
    } catch (err) {
      toast(err.message);
      play(rowDivs[r], "animate-shake");
    } finally {
      busy = false;
    }
  }

  async function useHint() {
    if (busy || overlayOpen) return;
    busy = true;
    try {
      const data = await api("/api/hint", "POST");
      S = data.state;
      refreshInfo();
      play($("hint-text"), "animate-pop");
    } catch (err) {
      toast(err.message);
    } finally {
      busy = false;
    }
  }

  async function goNext() {
    closeOverlay();
    busy = true;
    try {
      const data = await api("/api/next", "POST");
      S = data.state;
      if (S.finished) {
        showFinal();
      } else {
        if (data.transition === "level") await showLevelTransition();
        render();
      }
    } catch (err) {
      toast(err.message);
    } finally {
      busy = false;
    }
  }

  async function newGame() {
    closeOverlay();
    busy = true;
    try {
      const data = await api("/api/new-game", "POST");
      S = data.state;
      render();
    } catch (err) {
      toast(err.message);
    } finally {
      busy = false;
    }
  }

  // ---------------------------------------------------------------- telas sobrepostas
  function showOverlay(build) {
    const box = $("overlay-box");
    box.replaceChildren();
    build(box);
    const ov = $("overlay");
    ov.classList.remove("hidden");
    ov.classList.add("flex");
    play(box, "animate-pop");
    overlayOpen = true;
  }

  function closeOverlay() {
    const ov = $("overlay");
    ov.classList.add("hidden");
    ov.classList.remove("flex");
    overlayOpen = false;
  }

  function button(label, cls, onClick) {
    const b = el("button", `w-full rounded-xl px-4 py-3 text-base font-extrabold shadow transition active:scale-95 hover:brightness-95 ${cls}`, label);
    b.addEventListener("click", onClick);
    return b;
  }

  function showWordResult() {
    const won = S.word_status === "won";
    const lastWord = S.word_number === S.words_per_level;
    const lastLevel = S.level === S.total_levels;

    showOverlay((box) => {
      box.appendChild(el("p", "text-5xl", won ? "🎉" : "💭"));
      box.appendChild(el("h2", "mt-2 text-2xl font-black text-brand-brown", won ? "Você acertou!" : "Não foi dessa vez"));
      if (won) {
        box.appendChild(el("p", "mt-1 text-sm", `Em ${S.attempts_used} ${S.attempts_used === 1 ? "tentativa" : "tentativas"}.`));
      } else {
        box.appendChild(el("p", "mt-1 text-sm", "Suas tentativas acabaram. A palavra era:"));
      }
      const answer = el("p", `mt-3 break-all rounded-xl px-3 py-3 text-xl font-black tracking-widest ${won ? "bg-brand-blue" : "bg-brand-pink"}`, S.answer);
      box.appendChild(answer);

      const label = !lastWord ? "Próxima palavra" : lastLevel ? "Ver resultado final" : "Concluir nível";
      const next = button(label, "mt-4 bg-brand-brown text-brand-cream", goNext);
      box.appendChild(next);
    });
  }

  async function showLevelTransition() {
    showOverlay((box) => {
      box.appendChild(el("p", "text-5xl animate-hop", "⭐"));
      box.appendChild(el("h2", "mt-2 text-2xl font-black text-brand-brown", `Nível ${S.level - 1} concluído!`));
      box.appendChild(el("p", "mt-2 text-sm", `Prepare-se: no nível ${S.level} as palavras têm ${S.letters} letras e você tem ${S.max_attempts} tentativas.`));
    });
    await sleep(2200);
    closeOverlay();
  }

  function showFinal() {
    showOverlay((box) => {
      const stars = el("div", "flex justify-center gap-2 text-4xl");
      ["#78A5CE", "#DDA4B4", "#7C5549", "#78A5CE", "#DDA4B4"].forEach((color, i) => {
        const s = el("span", "animate-hop", "★");
        s.style.color = color;
        s.style.animationDelay = `${i * 120}ms`;
        stars.appendChild(s);
      });
      box.appendChild(stars);
      box.appendChild(el("h2", "mt-3 text-2xl font-black text-brand-brown", "Parabéns! Você concluiu o jogo!"));
      box.appendChild(el("p", "mt-2 text-sm", `Você acertou ${S.score} de ${S.total_words} palavras.`));
      box.appendChild(button("Jogar novamente", "mt-4 bg-brand-brown text-brand-cream", newGame));
    });
  }

  function showHelp() {
    showOverlay((box) => {
      box.appendChild(el("h2", "text-2xl font-black text-brand-brown", "Como jogar"));
      const p = (t) => box.appendChild(el("p", "mt-2 text-sm", t));
      p("Descubra a palavra inteira. Digite uma palavra com o número de letras da grade e toque em ENVIAR. Você tem tantas tentativas quanto letras.");

      const legend = [
        ["correct", "A", "A letra está na palavra e na posição certa."],
        ["present", "B", "A letra está na palavra, mas em outra posição."],
        ["absent", "C", "A letra não está na palavra."],
      ];
      const list = el("div", "mt-3 flex flex-col gap-2 text-left");
      legend.forEach(([kind, letter, text]) => {
        const line = el("div", "flex items-center gap-3");
        const tile = el("div", `flex h-10 w-10 shrink-0 items-center justify-center rounded-md border-2 text-lg font-extrabold ${TILE_KINDS[kind]}`, letter);
        line.appendChild(tile);
        line.appendChild(el("span", "text-sm", text));
        list.appendChild(line);
      });
      box.appendChild(list);

      p("Acentos e cedilha são preenchidos automaticamente: pode digitar sem eles. A dica extra aparece a partir do nível 3 (uma vez por nível).");
      box.appendChild(button("Entendi", "mt-4 bg-brand-brown text-brand-cream", closeOverlay));
    });
  }

  function confirmRestart() {
    showOverlay((box) => {
      box.appendChild(el("h2", "text-xl font-black text-brand-brown", "Reiniciar a partida?"));
      box.appendChild(el("p", "mt-2 text-sm", "Seu progresso atual será perdido e novas palavras serão sorteadas."));
      const row = el("div", "mt-4 flex gap-2");
      row.appendChild(button("Cancelar", "bg-brand-brown/15 text-ink", closeOverlay));
      row.appendChild(button("Reiniciar", "bg-brand-brown text-brand-cream", newGame));
      box.appendChild(row);
    });
  }

  // ---------------------------------------------------------------- início
  async function init() {
    buildKeyboard();

    $("hint-btn").addEventListener("click", useHint);
    $("help-btn").addEventListener("click", () => { if (!overlayOpen) showHelp(); });
    $("restart-btn").addEventListener("click", () => { if (!overlayOpen && !busy) confirmRestart(); });

    document.addEventListener("keydown", (e) => {
      if (e.ctrlKey || e.metaKey || e.altKey) return;
      if (e.key === "Enter") { e.preventDefault(); handleKey("ENTER"); return; }
      if (e.key === "Backspace") { e.preventDefault(); handleKey("BACK"); return; }
      const letter = keyToLetter(e.key);
      if (letter) handleKey(letter);
    });

    try {
      const data = await api("/api/state");
      S = data.state;
      render();
      if (S.finished) showFinal();
    } catch (err) {
      $("theme-hint").textContent = "Não foi possível carregar o jogo. Verifique se o servidor está rodando.";
    }
  }

  init();
})();