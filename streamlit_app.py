import streamlit as st

st.title('Highrise Music Bot')
st.write('This bot plays music in Highrise rooms using Spotify.')

song_name = st.text_input("Enter song name to play:")

if st.button("Play Song"):
    st.write(f"Playing: {song_name} (This feature needs integration with WebSocket.)")
