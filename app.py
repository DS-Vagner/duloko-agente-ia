"""
Interface do Agente DuLoko (Streamlit).

Para rodar localmente:
    streamlit run app.py
"""
import sys
from pathlib import Path

import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent))

from src.config import NOME_LOJA, NOME_AGENTE, GROQ_API_KEY
from src.rag_engine import RagEngine, RagAnswer

st.set_page_config(
    page_title=f"{NOME_AGENTE} 🛍️",
    page_icon="🛍️",
    layout="centered",
)

EXEMPLOS_PERGUNTAS = [
    "Qual o prazo para solicitar devolução por arrependimento?",
    "Meu produto chegou com defeito, o que eu faço?",
    "Quanto tempo demora o reembolso e ele volta pro mesmo cartão?",
    "O frete de devolução é gratuito?",
    "Quais métodos de pagamento a DuLoko aceita?",
    "Como funciona a comissão do programa de afiliados se o pedido for devolvido?",
    "Meu pedido chegou com a caixa amassada, isso é garantia ou dano de transporte?",
]


@st.cache_resource(show_spinner="Carregando a base de conhecimento da DuLoko...")
def carregar_engine() -> RagEngine:
    return RagEngine()


def render_sidebar():
    with st.sidebar:
        st.header(f"🛍️ {NOME_LOJA}")
        st.caption("Agente inteligente (RAG) — Challenge Alura Agente")

        st.markdown("### 📚 Base de conhecimento")
        st.markdown(
            "- Política de Reembolsos e Devoluções\n"
            "- Manual de Garantia de Produtos\n"
            "- FAQ de Métodos de Pagamento\n"
            "- Guia de Prazos e Custos de Envio\n"
            "- Programa de Afiliados"
        )

        st.markdown("### 💬 Exemplos de perguntas")
        for pergunta in EXEMPLOS_PERGUNTAS:
            if st.button(pergunta, use_container_width=True, key=f"ex_{pergunta}"):
                st.session_state["pergunta_selecionada"] = pergunta

        st.divider()
        if st.button("🗑️ Limpar conversa", use_container_width=True):
            st.session_state["mensagens"] = []
            st.rerun()


def render_mensagem(role: str, content: str, sources=None):
    with st.chat_message(role):
        st.markdown(content)
        if sources:
            with st.expander("📄 Fontes consultadas"):
                for s in sources:
                    st.markdown(f"- `{s}`")


def main():
    render_sidebar()

    st.title(f"🛍️ {NOME_AGENTE}")
    st.caption(
        f"Pergunte sobre devoluções, garantia, pagamentos, envios e o programa de "
        f"afiliados da {NOME_LOJA}. Respostas baseadas apenas na documentação oficial."
    )

    if not GROQ_API_KEY:
        st.warning(
            "⚠️ A variável GROQ_API_KEY não está configurada. "
            "Crie uma chave gratuita em https://console.groq.com/keys e configure-a "
            "no arquivo `.env` (local) ou em Secrets (Streamlit Cloud) antes de perguntar.",
            icon="⚠️",
        )

    if "mensagens" not in st.session_state:
        st.session_state["mensagens"] = []

    for msg in st.session_state["mensagens"]:
        render_mensagem(msg["role"], msg["content"], msg.get("sources"))

    pergunta_input = st.chat_input("Digite sua pergunta sobre a DuLoko...")
    pergunta_botao = st.session_state.pop("pergunta_selecionada", None)
    pergunta = pergunta_input or pergunta_botao

    if pergunta:
        st.session_state["mensagens"].append({"role": "user", "content": pergunta})
        render_mensagem("user", pergunta)

        with st.chat_message("assistant"):
            with st.spinner("Consultando a base de conhecimento..."):
                try:
                    engine = carregar_engine()
                    resultado: RagAnswer = engine.ask(pergunta)
                    st.markdown(resultado.answer)
                    if resultado.sources:
                        with st.expander("📄 Fontes consultadas"):
                            for s in resultado.sources:
                                st.markdown(f"- `{s}`")
                    st.session_state["mensagens"].append(
                        {
                            "role": "assistant",
                            "content": resultado.answer,
                            "sources": resultado.sources,
                        }
                    )
                except RuntimeError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"Ocorreu um erro ao consultar o agente: {e}")


if __name__ == "__main__":
    main()
