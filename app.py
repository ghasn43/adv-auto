#!/usr/bin/env python3
"""
Main entry point for the Social Media Agent with Authentication
"""

import streamlit as st
from auth import main_with_auth

if __name__ == "__main__":
    st.set_page_config(
        page_title="Social Media Agent",
        layout="wide",
        page_icon="📢",
        initial_sidebar_state="expanded"
    )
    
    # Run the authenticated app
    main_with_auth()