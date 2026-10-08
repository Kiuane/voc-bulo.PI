"""
BANCO DE PALAVRAS (local, sem API, sem custo)

Cada tema tem:
- "dica":     frase da dica geral mostrada ao jogador;
- "palavras": palavras escritas COM acento (o jogo normaliza sozinho).

Para adicionar palavras, basta incluir novos itens nas listas.
O tamanho de cada palavra é calculado automaticamente em game_logic.py
(depois de remover acentos), então você não precisa contar letras.
Use apenas UMA palavra por item (sem espaços e sem hífen).
"""

THEMES = {
    "animal": {
        "dica": "Sua palavra é um animal.",
        "palavras": [
            "lobo", "gato", "pato", "urso", "foca", "puma", "alce", "leão", "sapo", "rato",
            "zebra", "tigre", "cobra", "ovelha", "girafa", "cavalo", "coelho", "macaco", "baleia",
            "raposa", "abelha", "jacaré", "camelo", "pinguim", "gaivota", "tubarão", "morcego",
            "formiga", "leopardo", "elefante", "papagaio", "camaleão", "avestruz", "tamanduá",
            "cachorro", "libélula", "crocodilo", "chimpanzé", "borboleta", "centopeia", "escorpião",
            "gafanhoto", "tartaruga", "hipopótamo", "pernilongo", "salamandra", "passarinho",
            "caranguejo", "rinoceronte", "orangotango", "ornitorrinco",
        ],
    },
    "pais": {
        "dica": "Sua palavra é um país.",
        "palavras": [
            "Cuba", "Peru", "Irã", "Mali", "Togo", "Laos", "Omã", "Chile", "Japão", "Egito",
            "Brasil", "Canadá", "Panamá", "Angola", "França", "Itália", "Rússia", "Quênia", "Líbano",
            "México", "Bolívia", "Espanha", "Turquia", "Dinamarca", "Argentina", "Venezuela",
            "Paquistão", "Indonésia", "Singapura", "Mauritânia", "Madagascar", "Moçambique",
            "Bangladesh", "Luxemburgo", "Azerbaijão", "Montenegro", "Afeganistão", "Cazaquistão",
            "Uzbequistão", "Quirguistão", "Tadjiquistão", "Turcomenistão", "Liechtenstein",
        ],
    },
    "cidade": {
        "dica": "Sua palavra é uma cidade.",
        "palavras": [
            "Roma", "Lima", "Faro", "Oslo", "Pisa", "Nice", "Doha", "Baku", "Paris", "Dubai",
            "Berlim", "Madrid", "Lisboa", "Recife", "Cuiabá", "Manaus", "Tóquio", "Goiânia",
            "Londres", "Sevilha", "Curitiba", "Uberlândia", "Fortaleza", "Salvador", "Barcelona",
            "Florianópolis", "Johannesburgo", "Pindamonhangaba",
        ],
    },
    "corpo": {
        "dica": "Sua palavra é uma parte do corpo.",
        "palavras": [
            "mão", "olho", "boca", "dedo", "unha", "pele", "coxa", "nuca", "veia", "osso",
            "nariz", "lábio", "ombro", "cabeça", "joelho", "costas", "tronco", "pescoço", "barriga",
            "garganta", "cotovelo", "tornozelo", "antebraço", "calcanhar", "cartilagem",
            "sobrancelha", "articulação", "panturrilha", "musculatura", "esternocleidomastoideo",
        ],
    },
    "orgao": {
        "dica": "Sua palavra é um órgão do corpo.",
        "palavras": [
            "baço", "rins", "pulmão", "fígado", "bexiga", "coração", "cérebro", "esôfago",
            "estômago", "vesícula", "pâncreas", "traqueia", "tireoide", "hipófise", "diafragma",
            "intestino", "hipotálamo",
        ],
    },
    "objeto": {
        "dica": "Sua palavra é um objeto.",
        "palavras": [
            "mesa", "bola", "copo", "cama", "vaso", "lupa", "mala", "faca", "roda", "sino",
            "porta", "pente", "livro", "chave", "bolsa", "garfo", "caneta", "tapete", "colher",
            "panela", "pincel", "cadeira", "tesoura", "martelo", "relógio", "lâmpada", "espelho",
            "caderno", "cortina", "geladeira", "aspirador", "televisão", "apontador", "computador",
            "microondas", "ventilador", "impressora", "telescópio", "termômetro", "carregador",
            "espremedor", "calculadora", "descascador", "refrigerador", "estetoscópio",
            "fotocopiadora", "liquidificador", "multiprocessador",
        ],
    },
    "cor": {
        "dica": "Sua palavra é uma cor.",
        "palavras": [
            "azul", "rosa", "roxo", "bege", "cinza", "prata", "verde", "preto", "marrom", "branco",
            "laranja", "dourado", "violeta", "amarelo", "magenta", "vermelho", "turquesa",
        ],
    },
    "idioma": {
        "dica": "Sua palavra é um idioma.",
        "palavras": [
            "russo", "árabe", "hindi", "inglês", "francês", "alemão", "chinês", "japonês", "coreano",
            "italiano", "espanhol", "hebraico", "holandês", "mandarim", "português",
        ],
    },
    "estado": {
        "dica": "Sua palavra é um estado do Brasil.",
        "palavras": [
            "Acre", "Pará", "Bahia", "Goiás", "Piauí", "Ceará", "Amapá", "Paraná", "Sergipe",
            "Alagoas", "Roraima", "Paraíba", "Amazonas", "Maranhão", "Rondônia", "Tocantins",
            "Pernambuco",
        ],
    },
    "continente": {
        "dica": "Sua palavra é um continente.",
        "palavras": ["Ásia", "Europa", "África", "América", "Oceania", "Antártida"],
    },
    "fruta": {
        "dica": "Sua palavra é uma fruta.",
        "palavras": [
            "pera", "figo", "kiwi", "lima", "manga", "limão", "banana", "laranja", "abacaxi",
            "melancia", "morango", "goiaba", "mamão", "maçã", "uva", "caju", "acerola", "framboesa",
            "tangerina", "maracujá", "jabuticaba",
        ],
    },
    "profissao": {
        "dica": "Sua palavra é uma profissão.",
        "palavras": [
            "médico", "pintor", "padeiro", "dentista", "professor", "motorista", "arquiteto",
            "cozinheiro", "enfermeiro", "bombeiro", "marceneiro", "encanador", "agricultor",
            "engenheiro", "jornalista", "eletricista", "programador", "veterinário", "arqueólogo",
            "oncologista", "urologista", "nefrologista", "farmacêutico", "cabeleireiro",
            "bibliotecário", "cardiologista", "ginecologista", "fonoaudiólogo", "oftalmologista",
            "dermatologista", "neurocirurgião", "fisioterapeuta", "meteorologista",
            "reumatologista", "pneumologista", "radioterapeuta", "traumatologista",
            "endocrinologista", "anestesiologista", "gastroenterologista", "otorrinolaringologista",
        ],
    },
    "ciencia": {
        "dica": "Sua palavra tem relação com ciência.",
        "palavras": [
            "átomo", "célula", "energia", "gravidade", "oxigênio", "fotossíntese", "microscópio",
            "paleontologia", "termodinâmica", "biodiversidade", "radioatividade", "paralelepípedo",
            "eletromagnetismo", "telecomunicações",
        ],
    },
    "adverbio": {
        "dica": "Sua palavra é um advérbio terminado em -mente.",
        "palavras": [
            "lentamente", "felizmente", "totalmente", "facilmente", "geralmente", "atualmente",
            "rapidamente", "diretamente", "naturalmente", "completamente", "especialmente",
            "imediatamente", "principalmente", "exclusivamente", "individualmente",
            "definitivamente", "simultaneamente", "inevitavelmente", "inesperadamente",
            "consequentemente", "tradicionalmente", "intelectualmente", "psicologicamente",
            "tecnologicamente", "profissionalmente", "indiscutivelmente", "irreversivelmente",
            "internacionalmente", "irresponsavelmente", "institucionalmente",
            "extraordinariamente", "constitucionalmente", "desproporcionalmente",
            "incompreensivelmente", "inconstitucionalmente",
        ],
    },
}