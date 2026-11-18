import httpx
import streamlit as st

# Frontend für die Regesta Chat-Anwendung mit Streamlit.
# Dieses Skript stellt die Benutzeroberfläche bereit, über die Benutzer Fragen stellen und Antworten vom Backend-Server erhalten können.

# Titel der Anwendung
st.title("Regesta Chat")

# Initialisierung des Chatverlaufs im Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Anzeige des Chatverlaufs
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Eingabefeld für neue Nachrichten
prompt = st.chat_input("Frage stellen")

# Wenn der Benutzer eine Nachricht eingibt, wird sie an den Backend-Server gesendet und die Antwort wird gestreamt
if prompt:

    # Neue Nachricht des Benutzers zum Chatverlauf hinzufügen
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
    })

    # Anzeige der Benutzeranfrage im Chat
    with st.chat_message("user"):
        st.markdown(prompt)

    # Platzhalter für die Antwort des Assistenten (notwendig, um die Antwort während des Streamings zu aktualisieren)
    placeholder = st.empty()
    answer = ""

    # Streaming der Antwort vom Backend-Server
    with st.chat_message("assistant"):
        # Streaming der Antwort vom Backend-Server (Endpunkt: /chat)
        with httpx.stream(
            "POST",
            "http://127.0.0.1:8000/chat",
            json={"message": prompt},
            timeout=120,
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line.startswith("data:"):
                    chunk = line.removeprefix("data:")
                    answer += chunk
                    placeholder.markdown(answer)

    # Nach dem Streaming wird die vollständige Antwort des Assistenten zum Chatverlauf hinzugefügt
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
    })