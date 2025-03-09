"""
Interface module for the Message Terminal
"""
import streamlit as st
import time

class Interface:
    def __init__(self, db_manager, config):
        self.db_manager = db_manager
        self.config = config
        self._init_session_state()
    
    def _init_session_state(self):
        """Initialize session state variables"""
        if 'session_id' not in st.session_state:
            st.session_state['session_id'] = str(int(time.time()))
        if 'messages_cache' not in st.session_state:
            st.session_state['messages_cache'] = []
        if 'input_key' not in st.session_state:
            st.session_state['input_key'] = 0
        if 'container_key' not in st.session_state:
            st.session_state['container_key'] = 0
    
    def setup_page(self):
        """Setup the page configuration"""
        st.set_page_config(
            page_title=self.config['app']['title'],
            page_icon=self.config['app']['icon'],
            layout="wide",
            initial_sidebar_state="collapsed",
            menu_items={
                'Get Help': None,
                'Report a bug': None,
                'About': 'Message Terminal System v1.0'
            }
        )
    
    def render_header(self):
        """Render the header section"""
        st.markdown('<h1 class="title-text">_MESSAGE TERMINAL_</h1>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="status-text">[SYSTEM: ONLINE] [SESSION ID: {st.session_state["session_id"]}]</div>',
            unsafe_allow_html=True
        )
    
    def render_messages(self):
        """Render the messages area"""
        messages_container = st.empty()
        with messages_container.container():
            messages = self.db_manager.load_messages()
            if not messages:
                st.info("_Waiting for messages..._")
            else:
                with st.container():
                    for msg in messages:
                        st.markdown(f'<div class="terminal-text">{msg}</div>', unsafe_allow_html=True)
        return messages_container
    
    def render_input_area(self):
        """Render the input area"""
        col1, col2 = st.columns([4, 1])
        with col1:
            key = f"msg_input_{st.session_state['input_key']}"
            message = st.text_input("Message", value="", key=key, label_visibility="collapsed")
        
        with col2:
            sent = st.button("SEND") or (message and message != st.session_state.get('last_msg', ''))
            if sent and message.strip():
                self.db_manager.add_message(message, True)
                st.session_state['last_msg'] = message
                st.session_state['input_key'] += 1
                time.sleep(0.1)
                st.rerun()
    
    def render_clear_button(self, messages_container):
        """Render the clear button"""
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            if st.button("🗑️ Clear Messages"):
                if self.db_manager.clear_messages():
                    # Gerar novo Session ID
                    st.session_state['session_id'] = str(int(time.time()))
                    st.session_state['messages_cache'] = []
                    st.session_state['container_key'] += 1
                    st.session_state['input_key'] = 0
                    with messages_container.container():
                        st.info("_Waiting for messages..._")
                    time.sleep(0.1)
                    st.rerun()
    
    def check_updates(self):
        """Check for updates and rerun if needed"""
        time.sleep(0.5)
        current_time = time.time()
        last_update = st.session_state.get('last_update', 0)
        
        if current_time - last_update > 2:
            st.session_state['last_update'] = current_time
            st.rerun() 