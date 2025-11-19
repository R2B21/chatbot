
# chatbot_ccs.py
# Protótipo de chatbot FAQ para o Setor de Gestão de Pessoas (CCS/UFPB)
# Execução: python chatbot_ccs.py
# Requisitos: apenas Python 3 (sem bibliotecas externas)

import sys
import re
import unicodedata
from difflib import SequenceMatcher

BANNER = '''
====================================================
  Chatbot - Atendimento CCS/UFPB (Protótipo CLI)
  Pergunte sobre: férias, plano de trabalho, afastamentos,
  atendimento, horário, documentos, contatos...

  Comandos úteis: "menu", "opções", "listar", "sair"
====================================================
'''

def normalize(text: str) -> str:
    """Normaliza texto para comparação: minúsculas, sem acentos,
    remove pontuação simples e espaços extras."""
    if not text:
        return ""
    text = text.lower().strip()
    # remove acentos
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    # remove pontuação simples
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    # colapsa espaços
    text = re.sub(r"\s+", " ", text).strip()
    return text

# Base de conhecimento inicial (mock) — substituir/expandir conforme documentos da PRG/UFPB
KB = [
    {
        "id": "ferias_basico",
        "tags": ["ferias", "férias", "marcar ferias", "periodo aquisitivo"],
        "patterns": [
            "como marcar ferias",
            "quando posso tirar ferias",
            "ferias servidor ccs",
            "calendario de ferias",
            "prazo ferias",
        ],
        "answer": (
            "FÉRIAS — Informações básicas:\\n"
            "- O agendamento segue o calendário institucional.\\n"
            "- A solicitação deve ser registrada no sistema SEI conforme orientações da PROGEP.\\n"
            "- Recomenda-se antecedência mínima conforme a norma interna.\\n"
            "Consulte o manual/portais oficiais da PROGEP/UFPB para detalhes e prazos."
        ),
    },
    {
        "id": "plano_trabalho",
        "tags": ["plano de trabalho", "plano", "pt", "atividades", "registro"],
        "patterns": [
            "como enviar plano de trabalho",
            "onde registrar plano de trabalho",
            "prazo do plano de trabalho",
            "modelo de plano de trabalho",
        ],
        "answer": (
            "PLANO DE TRABALHO — Diretrizes:\\n"
            "- O envio é feito via SEI usando o modelo oficial.\\n"
            "- Verifique o manual da PROGEP/UFPB para campos obrigatórios e periodicidade.\\n"
            "- Guarde o comprovante de protocolo.\\n"
            "Para links e modelos, consulte o site da PROGEP."
        ),
    },
    {
        "id": "afastamentos",
        "tags": ["afastamento", "licenca", "licença", "saude", "capacitação"],
        "patterns": [
            "como solicitar afastamento",
            "afastamento para capacitacao",
            "licenca medica",
            "documentos para afastamento",
        ],
        "answer": (
            "AFASTAMENTOS — Passos gerais:\\n"
            "- Verifique o tipo (capacitação, saúde, interesse, etc.).\\n"
            "- Anexe a documentação exigida conforme o tipo de afastamento.\\n"
            "- Protocole no SEI e acompanhe os prazos.\\n"
            "As regras completas constam no portal da PROGEP/UFPB."
        ),
    },
    {
        "id": "horario_contato",
        "tags": ["horario", "horário", "contato", "email", "e-mail", "atendimento"],
        "patterns": [
            "qual horario de atendimento",
            "como entrar em contato",
            "email do setor",
            "telefone do setor",
        ],
        "answer": (
            "ATENDIMENTO — Contatos e horários (protótipo):\\n"
            "- Horário padrão: dias úteis, conforme expediente do CCS.\\n"
            "- Priorize o atendimento institucional (e-mail setorial).\\n"
            "Para demandas complexas, descreva o caso e anexe documentos no SEI."
        ),
    },
    {
        "id": "documentos_publicos",
        "tags": ["documento", "documentos", "base de dados", "norma", "manual", "faq"],
        "patterns": [
            "onde estao os documentos",
            "documentos publicos",
            "manual da prg",
            "base de conhecimento",
        ],
        "answer": (
            "DOCUMENTOS — Acesso público:\\n"
            "- Os documentos/FAQs estão disponíveis no portal da Pró-Reitoria de Gestão de Pessoas (PROGEP/UFPB).\\n"
            "- Utilize as buscas por tema (férias, plano de trabalho, afastamentos) e verifique as versões atualizadas."
        ),
    },
    {
        "id": "fallback",
        "tags": [],
        "patterns": [],
        "answer": (
            "Não encontrei uma resposta direta para sua pergunta.\\n"
            "Você pode tentar:\\n"
            "1) digitar 'menu' para ver opções; ou\\n"
            "2) reescrever com mais detalhes; ou\\n"
            "3) encaminhar ao atendimento humano via e-mail institucional."
        ),
    },
]

MENU = [
    ("Férias", "Pergunte sobre períodos, prazos e agendamento."),
    ("Plano de trabalho", "Envio via SEI, modelos e prazos."),
    ("Afastamentos", "Tipos, documentos e protocolo."),
    ("Atendimento/Contato", "Horário e canais institucionais."),
    ("Documentos públicos", "Onde localizar manuais e normas (PROGEP/UFPB)."),
]

def similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

def find_best_answer(user_input: str) -> str:
    q = normalize(user_input)
    if not q:
        return "Digite sua dúvida ou 'menu' para ver opções."

    # 1) correspondência por TAG (palavra-chave direta)
    for item in KB:
        for tag in item["tags"]:
            if normalize(tag) in q:
                return item["answer"]

    # 2) similaridade com padrões
    best_score = 0.0
    best_item = None
    for item in KB:
        for patt in item["patterns"]:
            score = similar(q, normalize(patt))
            if score > best_score:
                best_score = score
                best_item = item

    if best_item and best_score >= 0.60:
        return best_item["answer"]

    # 3) fallback
    return next(x for x in KB if x["id"] == "fallback")["answer"]

def show_menu():
    print("\\n=== MENU DE TÓPICOS ===")
    for i, (titulo, desc) in enumerate(MENU, 1):
        print(f"{i}. {titulo} — {desc}")
    print("=======================\\n")

def main():
    print(BANNER)
    show_menu()
    while True:
        try:
            user = input("Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\\nBot: Até logo!")
            break

        if not user:
            print("Bot: Pode repetir por favor?")
            continue

        cmd = normalize(user)
        if cmd in {"sair", "exit", "tchau"}:
            print("Bot: Até logo!")
            break

        if cmd in {"menu", "opcoes", "opções", "listar"}:
            show_menu()
            continue

        answer = find_best_answer(user)
        print("Bot:", answer)
        # dica de follow-up
        if "Não encontrei" in answer:
            print("Bot: Exemplos: 'como marcar férias', 'plano de trabalho', 'afastamento para capacitação'.")

if __name__ == "__main__":
    main()
