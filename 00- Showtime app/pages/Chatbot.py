import streamlit as st
import branding
import random
import sys 
from pathlib import Path

st.subheader("Discutes avec Confussio 🐼")

st.markdown(
    """
    Réalises le rêve de tant de femmes et glisse dans les dms de ce bon vieux **Confussio** 😉"""
)

st.divider()

branding.render_sidebar()


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BOT_AVATAR = PROJECT_ROOT / "visuals/Icon confussio.png"

# Initialize chat history
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# Display messages
for message in st.session_state.chat_messages:
    if message["role"] == "assistant":
        with st.chat_message("assistant", avatar=str(BOT_AVATAR)):
            st.markdown(message["content"])
    else:
        with st.chat_message("user", avatar="👤"):
            st.markdown(message["content"])

# List of random responses
responses = [
    "Fuck you Loïs 🖕",
    "Envoies fesses 🍑",
    "Tu crois qu'on est pote ptdrrrrr 😂 arraches là bas stp",
    "Bodycount ?",
    "Envoies pieds stp",
    "Parles aps ici c'est les cités de wenZOO #lamuerteleurvasibien",
    "Ntm Loïs 🖕"
]

# User input
prompt = st.chat_input("Écris un message")

if prompt:
    st.session_state.chat_messages.append({
        "role": "user",
        "content": prompt
    })

    # Pick random response
    reply = random.choice(responses)

    st.session_state.chat_messages.append({
        "role": "assistant",
        "content": reply
    })

    st.rerun()