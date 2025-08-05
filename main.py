#!/usr/bin/env python3
"""
Article Analysis Tool - Main Entry Point

A comprehensive web application that uses Streamlit for the frontend and crewAI 
for backend processing to find, scrape, summarize, and classify online articles.

Author: AI Assistant
Version: 2.0
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.streamlit_ui import StreamlitUI

def main():
    """
    Main entry point for the Article Analysis Tool
    """
    try:
        # Initialize and run the Streamlit UI
        ui = StreamlitUI()
        ui.run()
        
    except Exception as e:
        import streamlit as st
        st.error(f"Application failed to start: {str(e)}")
        st.error("Please check your API keys and dependencies.")

if __name__ == "__main__":
    main()
