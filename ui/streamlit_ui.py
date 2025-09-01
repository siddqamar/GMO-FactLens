import streamlit as st
import os
from typing import List, Dict, Any
from datetime import datetime
import json
#from ..database.db_manager import DatabaseManager
#from crewai_workflow import CrewAIWorkflow
from agents.notion_publisher import NotionPublisher

class StreamlitUI:
    """Clean, production-ready UI for GMO FactLens"""

    def __init__(self):
        self.db_manager = DatabaseManager()
        self.workflow = CrewAIWorkflow()
        self.notion_publisher = NotionPublisher()
        self.setup_page_config()
        self.init_session_state()

    def setup_page_config(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title="GMO FactLens",
            page_icon="🔬",
            layout="wide",
            initial_sidebar_state="collapsed"
        )

        # Custom CSS matching GMO FactLens color scheme
        st.markdown("""
        <style>
        .main-header {
            text-align: center;
            padding: 2rem 0;
            background: linear-gradient(135deg, #14b8a6 0%, #0891b2 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        .search-container {
            background: #f0fdfa;
            padding: 2rem;
            border-radius: 10px;
            border: 1px solid #99f6e4;
            margin-bottom: 2rem;
        }
        .metric-card {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid #99f6e4;
            text-align: center;
        }
        .fact-badge {
            background: #dcfce7;
            color: #166534;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.875rem;
            font-weight: 600;
        }
        .myth-badge {
            background: #fef2f2;
            color: #dc2626;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.875rem;
            font-weight: 600;
        }
        .unclear-badge {
            background: #fef3c7;
            color: #d97706;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.875rem;
            font-weight: 600;
        }
        .stButton > button {
            width: 100%;
            background: linear-gradient(135deg, #14b8a6 0%, #0891b2 100%);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-weight: 600;
        }
        .stButton > button:hover {
            background: linear-gradient(135deg, #0f766e 0%, #0e7490 100%);
        }
        .topic-header {
            background: #f0fdfa;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #14b8a6;
            margin-bottom: 1rem;
        }
        </style>
        """, unsafe_allow_html=True)

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

    def check_api_keys(self):
        """Check if required API keys are configured"""
        serper_key = os.getenv('SERPER_API_KEY')
        google_key = os.getenv('GOOGLE_API_KEY')
        return bool(serper_key and google_key)

    def render_header(self):
        """Render the main page header"""
        st.markdown("""
        <div class="main-header">
            <h1>🧬 GMO FactLens <span style="opacity: 0.7; font-size: 0.7em;">(Beta)</span></h1>
            <p style="font-size: 1.2rem; margin: 0; opacity: 0.9;">
                AI-powered fact-checking and analysis for GMO-related content
            </p>
        </div>
        """, unsafe_allow_html=True)

    def render_search_interface(self):
        """Render the main search interface"""
        st.markdown('<div class="search-container">', unsafe_allow_html=True)

        col1, col2 = st.columns([3, 1])

        with col1:
            topic = st.text_input(
                "",
                placeholder="Enter a topic to analyze (e.g., GMO can cause cancer, GMO is harmful for envoirment, organic vs GMO)",
                label_visibility="collapsed",
                key="topic_input"
            )

        with col2:
            # Advanced options in expander
            with st.expander("⚙️ Options"):
                use_crewai = st.checkbox(
                    "Enhanced Analysis",
                    value=False,
                    help="Use advanced AI workflow for deeper analysis"
                )
                max_results = st.slider(
                    "Max Articles",
                    min_value=5,
                    max_value=20,
                    value=10,
                    help="Number of articles to analyze"
                )

        # Center the analyze button with better spacing
        st.markdown("<br>", unsafe_allow_html=True)  # Add some space
        col_left, col_center, col_right = st.columns([2, 1, 2])
        with col_center:
            analyze_button = st.button(
                "Analyze Topic",
                type="primary",
                disabled=st.session_state.is_processing or not self.check_api_keys(),
                use_container_width=True
            )

        st.markdown('</div>', unsafe_allow_html=True)

        # Show configuration warning if API keys missing
        if not self.check_api_keys():
            st.warning("⚠️ Please configure your API keys to use GMO FactLens")

        return topic, use_crewai, max_results, analyze_button

    def render_processing_status(self):
        """Render processing status"""
        if st.session_state.is_processing:
            with st.container():
                st.info("🔄 Analyzing articles... This may take a few minutes.")
                progress_bar = st.progress(0)
                status_text = st.empty()

                # Simulate progress (in real implementation, you'd update this based on actual progress)
                import time
                for i in range(100):
                    progress_bar.progress(i + 1)
                    if i < 30:
                        status_text.text("🔍 Searching for articles...")
                    elif i < 60:
                        status_text.text("📄 Analyzing content...")
                    elif i < 90:
                        status_text.text("🤖 Fact-checking claims...")
                    else:
                        status_text.text("✅ Finalizing results...")
                    time.sleep(0.1)

    def handle_analysis_request(self, topic: str, use_crewai: bool, max_results: int):
        """Handle the analysis request from user"""
        if not self.check_api_keys():
            st.error("API keys not configured. Please check your environment variables.")
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

                # Publish to Notion if enabled
                if self.notion_publisher.is_enabled():
                    self.publish_results_to_notion(topic, results)

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

                st.success(f"✅ Analysis complete! Analyzed {len(results)} articles.")
                st.rerun()
            else:
                st.warning("No articles found for this topic. Try a different search term.")
                st.session_state.is_processing = False

        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")
            st.session_state.is_processing = False

    def publish_results_to_notion(self, topic: str, results: List[Dict[str, Any]]):
        """Publish analysis results to Notion"""
        try:
            run_name = f"{topic}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            if self.notion_publisher.create_db_each_run:
                database_id = self.notion_publisher.create_run_database(run_name)
                if not database_id:
                    return
            else:
                database_id = os.getenv('NOTION_DATABASE_ID')
                if not database_id:
                    return

            published_count = 0
            for item in results:
                if 'analysis_date' not in item:
                    item['analysis_date'] = datetime.now().strftime('%Y-%m-%d')

                if self.notion_publisher.publish_item_to_notion(item, database_id):
                    published_count += 1

            if published_count > 0:
                notion_url = self.notion_publisher.get_database_url(database_id)
                st.session_state.notion_run_url = notion_url

        except Exception as e:
            # Silently handle Notion errors to not disrupt main workflow
            pass

    def render_results_summary(self):
        """Render simplified results summary with topic and Notion link"""
        if not st.session_state.results:
            return

        # Topic header with clean styling
        st.markdown(f"""
        <div class="topic-header">
            <h3 style="margin: 0; color: #0f766e;">📋 Analysis: {st.session_state.current_topic}</h3>
            <p style="margin: 0.5rem 0 0 0; color: #64748b; font-size: 0.9rem;">
                Found {len(st.session_state.results)} articles • {datetime.now().strftime('%B %d, %Y')}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Show Notion link if available
        if hasattr(st.session_state, 'notion_run_url') and st.session_state.notion_run_url:
            st.success(f"📊 **View detailed results in Notion:** [Click here]({st.session_state.notion_run_url})")

        # Optional expandable summary stats
        with st.expander("📊 View Summary Statistics", expanded=False):
            # Calculate metrics
            total = len(st.session_state.results)
            facts = sum(1 for r in st.session_state.results if r.get('fact_myth_status') == 'Fact')
            myths = sum(1 for r in st.session_state.results if r.get('fact_myth_status') == 'Myth')
            unclear = sum(1 for r in st.session_state.results if r.get('fact_myth_status') == 'Unclear')
            successful = sum(1 for r in st.session_state.results
                            if r.get('summary') != 'Analysis failed - unable to process content')

            # Display metrics in cards
            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                st.metric("📄 Total Articles", total)
            with col2:
                st.metric("✅ Facts", facts, delta=f"{facts/total*100:.1f}%" if total > 0 else "0%")
            with col3:
                st.metric("❌ Myths", myths, delta=f"{myths/total*100:.1f}%" if total > 0 else "0%")
            with col4:
                st.metric("❓ Unclear", unclear, delta=f"{unclear/total*100:.1f}%" if total > 0 else "0%")
            with col5:
                st.metric("🎯 Success Rate", f"{successful/total*100:.1f}%" if total > 0 else "0%")

    def render_results_tabs(self):
        """Render results in organized tabs"""
        if not st.session_state.results:
            return

        tab1, tab2, tab3 = st.tabs(["📄 Articles", "📈 Analytics", "💾 Export"])

        with tab1:
            self.render_articles_grid()

        with tab2:
            self.render_analytics()

        with tab3:
            self.render_export_options()

    def render_articles_grid(self):
        """Render articles as expandable items with minimal initial display"""
        for i, article in enumerate(st.session_state.results):
            # Create expandable item showing only title and status initially
            title = article.get('title', 'Untitled Article')
            status = article.get('fact_myth_status', 'Unclear')

            # Status emoji for the expander header
            status_emoji = {"Fact": "✅", "Myth": "❌", "Unclear": "❓"}
            emoji = status_emoji.get(status, "❓")

            with st.expander(f"{emoji} {title}", expanded=False):
                # Article content inside expander
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"**Summary:** {article.get('summary', 'No summary available')}")

                    if article.get('key_claims'):
                        st.markdown("**Key Claims:**")
                        for claim in article.get('key_claims', []):
                            st.markdown(f"• {claim}")

                    st.markdown(f"🔗 [Read Original Article]({article['url']})")

                with col2:
                    # Status badge
                    if status == 'Fact':
                        st.markdown('<span class="fact-badge">✅ Fact</span>', unsafe_allow_html=True)
                    elif status == 'Myth':
                        st.markdown('<span class="myth-badge">❌ Myth</span>', unsafe_allow_html=True)
                    else:
                        st.markdown('<span class="unclear-badge">❓ Unclear</span>', unsafe_allow_html=True)

                    st.markdown("---")

                    # Classification
                    classification = article.get('classification', 'Other')
                    st.markdown(f"**Category:** {classification}")

                    # Confidence
                    confidence = article.get('confidence', 'medium')
                    confidence_emoji = {"high": "🟢", "medium": "🟡", "low": "🔴"}
                    st.markdown(f"**Confidence:** {confidence_emoji.get(confidence, '🟡')} {confidence.title()}")

    def render_analytics(self):
        """Render analytics and charts"""
        try:
            import plotly.express as px
            import pandas as pd

            if not st.session_state.results:
                st.info("No data available for analytics.")
                return

            df = pd.DataFrame(st.session_state.results)

            col1, col2 = st.columns(2)

            with col1:
                # Fact/Myth distribution
                if 'fact_myth_status' in df.columns:
                    status_counts = df['fact_myth_status'].value_counts()
                    fig_status = px.pie(
                        values=status_counts.values,
                        names=status_counts.index,
                        title="Fact vs Myth Distribution",
                        color_discrete_map={
                            'Fact': '#22c55e',
                            'Myth': '#ef4444',
                            'Unclear': '#f59e0b'
                        }
                    )
                    st.plotly_chart(fig_status, use_container_width=True)

            with col2:
                # Classification distribution
                if 'classification' in df.columns:
                    class_counts = df['classification'].value_counts()
                    fig_class = px.bar(
                        x=class_counts.index,
                        y=class_counts.values,
                        title="Articles by Category",
                        labels={'x': 'Category', 'y': 'Count'}
                    )
                    fig_class.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig_class, use_container_width=True)

        except ImportError:
            st.info("Install plotly to view analytics charts: `pip install plotly`")

    def render_export_options(self):
        """Render export options"""
        st.markdown("### 📥 Export Your Results")

        col1, col2 = st.columns(2)

        with col1:
            # JSON export
            if st.button("📄 Export as JSON", use_container_width=True):
                results_json = json.dumps(st.session_state.results, indent=2)
                st.download_button(
                    label="Download JSON File",
                    data=results_json,
                    file_name=f"gmo_factlens_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )

        with col2:
            # CSV export
            if st.button("📊 Export as CSV", use_container_width=True):
                try:
                    import pandas as pd
                    df = pd.DataFrame(st.session_state.results)
                    csv_data = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV File",
                        data=csv_data,
                        file_name=f"gmo_factlens_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                except ImportError:
                    st.error("Install pandas to export CSV: `pip install pandas`")

    def render_recent_analyses(self):
        """Render recent analysis history in sidebar"""
        if st.session_state.analysis_history:
            with st.sidebar:
                st.markdown("### 📚 Recent Analyses")
                for analysis in st.session_state.analysis_history[-3:]:
                    with st.container():
                        st.markdown(f"**{analysis['topic'][:25]}...**")
                        st.caption(f"{analysis['articles_count']} articles • {analysis['timestamp'][:10]}")
                        st.markdown("---")

    def run(self):
        """Main method to run the Streamlit UI"""
        self.render_header()

        # Main search interface
        topic, use_crewai, max_results, analyze_button = self.render_search_interface()

        # Handle analysis request
        if analyze_button and topic:
            self.handle_analysis_request(topic, use_crewai, max_results)

        # Show processing status
        if st.session_state.is_processing:
            self.render_processing_status()

        # Show results if available
        if st.session_state.results and not st.session_state.is_processing:
            self.render_results_summary()
            self.render_results_tabs()

        # Show recent analyses in sidebar
        self.render_recent_analyses()
