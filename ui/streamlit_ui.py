import streamlit as st
from typing import List, Dict, Any
from datetime import datetime
import json
from database.db_manager import DatabaseManager
from crewai_workflow import CrewAIWorkflow

class StreamlitUI:
    """Handles all Streamlit UI components and user interactions"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.workflow = CrewAIWorkflow()
        self.setup_page_config()
        self.init_session_state()
    
    def setup_page_config(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title="Realtime Analysis Tool",
            page_icon="🔍",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def init_session_state(self):
        """Initialize Streamlit session state variables"""
        if 'results' not in st.session_state:
            st.session_state.results = []
        if 'is_processing' not in st.session_state:
            st.session_state.is_processing = False
        if 'current_topic' not in st.session_state:
            st.session_state.current_topic = ""
        if 'analysis_history' not in st.session_state:
            st.session_state.analysis_history = []
    
    def render_header(self):
        """Render the main page header"""
        st.title("Realtime Analysis Tool")
        st.markdown("Find, analyze, and classify realtime data online using AI")
        st.markdown("---")
    
    def render_sidebar(self):
        """Render the sidebar with input controls and status"""
        with st.sidebar:
            st.header("Input Parameters")
            
            # Topic input
            topic = st.text_input(
                "Enter a topic to search for:",
                placeholder="e.g., global warming myths, vaccine safety, etc.",
                help="Enter a topic you want to analyze articles about"
            )
            
            # Analysis options
            st.subheader("Analysis Options")
            use_crewai = st.checkbox("Use CrewAI Framework", value=True, 
                                   help="Use the full CrewAI workflow instead of direct processing")
            max_results = st.slider("Maximum Results", min_value=5, max_value=20, value=10,
                                  help="Maximum number of articles to analyze")
            
            # Run button
            run_button = st.button("Run Analysis 🚀", type="primary", use_container_width=True)
            
            # API status
            self.render_api_status()
            
            # Database stats
            self.render_database_stats()
            
            return topic, use_crewai, max_results, run_button
    
    def render_api_status(self):
        """Render API key status in sidebar"""
        st.subheader("API Status")
        
        import os
        serper_key = os.getenv('SERPER_API_KEY')
        google_key = os.getenv('GOOGLE_API_KEY')
        
        if serper_key:
            st.success("✅ SerperAPI Key Found")
        else:
            st.error("❌ SerperAPI Key Missing")
            
        if google_key:
            st.success("✅ Google API Key Found")
        else:
            st.error("❌ Google API Key Missing")
    
    def render_database_stats(self):
        """Render database statistics in sidebar"""
        st.subheader("📊 Database Stats")
        
        stats = self.db_manager.get_database_stats()
        if stats:
            st.metric("Total Articles", stats.get('total_articles', 0))
            st.metric("Analysis Sessions", stats.get('total_sessions', 0))
            
            # Show recent sessions
            recent_sessions = self.db_manager.get_analysis_sessions(limit=3)
            if recent_sessions:
                st.caption("Recent Sessions:")
                for session in recent_sessions:
                    st.caption(f"• {session['topic'][:30]}... ({session['articles_found']} articles)")
    
    def render_main_content(self):
        """Render the main content area"""
        # Get sidebar inputs
        topic, use_crewai, max_results, run_button = self.render_sidebar()
        
        # Handle analysis trigger
        if run_button and topic:
            self.handle_analysis_request(topic, use_crewai, max_results)
        
        # Display results
        if st.session_state.results and not st.session_state.is_processing:
            self.render_results()
        elif st.session_state.is_processing:
            st.info("🔄 Analysis in progress... Please wait.")
    
    def handle_analysis_request(self, topic: str, use_crewai: bool, max_results: int):
        """Handle the analysis request from user"""
        import os
        
        # Check API keys
        if not os.getenv('SERPER_API_KEY') or not os.getenv('GOOGLE_API_KEY'):
            st.error("Please set both SERPER_API_KEY and GOOGLE_API_KEY environment variables")
            return
        
        st.session_state.is_processing = True
        st.session_state.current_topic = topic
        
        try:
            # Run analysis
            if use_crewai:
                results = self.workflow.run_crewai_workflow(topic)
            else:
                results = self.workflow.run_analysis(topic)
            
            if results:
                # Save to database
                saved_count = self.db_manager.save_articles_batch(results)
                session_id = self.db_manager.save_analysis_session(topic, results)
                
                # Update session state
                st.session_state.results = results
                st.session_state.is_processing = False
                
                # Add to history
                st.session_state.analysis_history.append({
                    'topic': topic,
                    'timestamp': datetime.now().isoformat(),
                    'articles_count': len(results),
                    'session_id': session_id
                })
                
                st.success(f"✅ Analysis complete! Found {len(results)} articles. Saved {saved_count} to database.")
            else:
                st.warning("No articles found or analysis failed.")
                st.session_state.is_processing = False
                
        except Exception as e:
            st.error(f"An error occurred during analysis: {str(e)}")
            st.session_state.is_processing = False
    
    def render_results(self):
        """Render the analysis results"""
        st.header("📊 Analysis Results")
        
        # Summary statistics
        self.render_summary_stats()
        
        # Results tabs
        tab1, tab2, tab3 = st.tabs(["📄 Articles", "📈 Charts", "💾 Export"])
        
        with tab1:
            self.render_articles_list()
        
        with tab2:
            self.render_charts()
        
        with tab3:
            self.render_export_options()
    
    def render_summary_stats(self):
        """Render summary statistics"""
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Articles", len(st.session_state.results))
        
        with col2:
            fact_count = sum(1 for r in st.session_state.results if r.get('fact_myth_status') == 'Fact')
            st.metric("Facts", fact_count)
        
        with col3:
            myth_count = sum(1 for r in st.session_state.results if r.get('fact_myth_status') == 'Myth')
            st.metric("Myths", myth_count)
        
        with col4:
            unclear_count = sum(1 for r in st.session_state.results if r.get('fact_myth_status') == 'Unclear')
            st.metric("Unclear", unclear_count)
        
        with col5:
            successful_count = sum(1 for r in st.session_state.results 
                                 if r.get('summary') != 'Analysis failed - unable to process content')
            st.metric("Successful", successful_count)
    
    def render_articles_list(self):
        """Render the list of analyzed articles"""
        for i, article in enumerate(st.session_state.results):
            with st.expander(f"📄 Article {i+1}: {article.get('title', 'Untitled')}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**URL:** {article['url']}")
                    st.markdown(f"**Summary:** {article.get('summary', 'No summary available')}")
                    
                    # Show key claims if available
                    if article.get('key_claims'):
                        st.markdown("**Key Claims:**")
                        for claim in article.get('key_claims', []):
                            st.markdown(f"• {claim}")
                
                with col2:
                    # Classification badge
                    self.render_classification_badge(article.get('classification', 'Other'))
                    
                    # Fact/Myth status
                    self.render_fact_myth_status(article.get('fact_myth_status', 'Unclear'))
                    
                    # Confidence level
                    confidence = article.get('confidence', 'medium')
                    if confidence == 'high':
                        st.success("🔵 High Confidence")
                    elif confidence == 'medium':
                        st.info("🟡 Medium Confidence")
                    else:
                        st.warning("🔴 Low Confidence")
    
    def render_classification_badge(self, classification: str):
        """Render classification badge with emoji"""
        badges = {
            'Health': "🏥 **Health**",
            'Environmental': "🌱 **Environmental**",
            'Social economics': "💰 **Social Economics**",
            'Conspiracy theory': "🤔 **Conspiracy Theory**",
            'Corporate control': "🏢 **Corporate Control**",
            'Ethical/religious issues': "⛪ **Ethical/Religious**",
            'Seed ownership': "🌾 **Seed Ownership**",
            'Scientific authority': "🔬 **Scientific Authority**",
            'Other': "📋 **Other**"
        }
        st.markdown(badges.get(classification, "📋 **Other**"))
    
    def render_fact_myth_status(self, status: str):
        """Render fact/myth status with appropriate styling"""
        if status == 'Fact':
            st.success("✅ **Fact**")
        elif status == 'Myth':
            st.error("❌ **Myth**")
        else:
            st.warning("❓ **Unclear**")
    
    def render_charts(self):
        """Render charts and visualizations"""
        import plotly.express as px
        import pandas as pd
        
        if not st.session_state.results:
            st.info("No data available for charts.")
            return
        
        # Prepare data
        df = pd.DataFrame(st.session_state.results)
        
        # Classification chart
        if 'classification' in df.columns:
            fig_class = px.pie(df, names='classification', title='Articles by Classification')
            st.plotly_chart(fig_class, use_container_width=True)
        
        # Fact/Myth status chart
        if 'fact_myth_status' in df.columns:
            fig_status = px.bar(df, x='fact_myth_status', title='Articles by Fact/Myth Status')
            st.plotly_chart(fig_status, use_container_width=True)
    
    def render_export_options(self):
        """Render export options"""
        st.subheader("📥 Export Results")
        
        # JSON export
        if st.button("Export as JSON"):
            results_json = json.dumps(st.session_state.results, indent=2)
            st.download_button(
                label="Download JSON",
                data=results_json,
                file_name=f"article_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        # CSV export
        if st.button("Export as CSV"):
            import pandas as pd
            df = pd.DataFrame(st.session_state.results)
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name=f"article_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    def run(self):
        """Main method to run the Streamlit UI"""
        self.render_header()
        self.render_main_content() 