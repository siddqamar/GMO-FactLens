import os
import time
from typing import Dict, Any, Optional
from notion_client import Client
from notion_client.errors import APIResponseError

# Try to import streamlit, but don't fail if not available
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    # Create a mock st object for when not in Streamlit context
    class MockStreamlit:
        def info(self, msg): print(f"INFO: {msg}")
        def success(self, msg): print(f"SUCCESS: {msg}")
        def error(self, msg): print(f"ERROR: {msg}")
        def warning(self, msg): print(f"WARNING: {msg}")
    st = MockStreamlit()

class NotionPublisher:
    """Agent responsible for publishing analysis results to Notion"""
    
    def __init__(self):
        self.token = os.getenv('NOTION_TOKEN')
        self.parent_page_id = os.getenv('NOTION_PARENT_PAGE_ID')
        self.publish_to_notion = os.getenv('PUBLISH_TO_NOTION', 'false').lower() == 'true'
        self.create_db_each_run = os.getenv('NOTION_CREATE_DB_EACH_RUN', 'false').lower() == 'true'
        
        if self.token and self.parent_page_id:
            try:
                self.client = Client(auth=self.token)
                if STREAMLIT_AVAILABLE:
                    st.success("✅ Notion integration ready")
            except Exception as e:
                if STREAMLIT_AVAILABLE:
                    st.error(f"❌ Failed to initialize Notion client: {str(e)}")
                else:
                    print(f"ERROR: Failed to initialize Notion client: {str(e)}")
                self.client = None
        else:
            self.client = None
            if self.publish_to_notion:
                if STREAMLIT_AVAILABLE:
                    st.warning("⚠️ Notion integration disabled: Missing NOTION_TOKEN or NOTION_PARENT_PAGE_ID")
                else:
                    print(f"WARNING: Notion integration disabled: Missing NOTION_TOKEN or NOTION_PARENT_PAGE_ID")
    
    def create_run_database(self, run_name: str) -> Optional[str]:
        """
        Create a new full-page database under the parent page
        
        Args:
            run_name (str): Name for this analysis run
            
        Returns:
            Optional[str]: Database ID if successful, None otherwise
        """
        if STREAMLIT_AVAILABLE:
            st.info(f"🔍 Creating Notion database for run: {run_name}")
        else:
            print(f"INFO: Creating Notion database for run: {run_name}")
        
        if not self.client or not self.parent_page_id:
            error_msg = f"❌ Cannot create database: client={'✅ Ready' if self.client else '❌ Not ready'}, parent_page_id={'✅ Set' if self.parent_page_id else '❌ Missing'}"
            if STREAMLIT_AVAILABLE:
                st.error(error_msg)
            else:
                print(f"ERROR: {error_msg}")
            return None
            
        try:
            # Create database properties
            properties = {
                "Title": {"title": {}},
                "URL": {"url": {}},
                "Content": {"rich_text": {}},
                "Summary": {"rich_text": {}},
                "Claims": {"rich_text": {}},
                "Fact Status": {"select": {
                    "options": [
                        {"name": "Fact", "color": "green"},
                        {"name": "Myth", "color": "red"},
                        {"name": "Unclear", "color": "yellow"}
                    ]
                }},
                "Classification": {"select": {
                    "options": [
                        {"name": "Health", "color": "blue"},
                        {"name": "Environmental", "color": "green"},
                        {"name": "Social economics", "color": "orange"},
                        {"name": "Conspiracy theory", "color": "red"},
                        {"name": "Corporate control", "color": "purple"},
                        {"name": "Ethical/religious issues", "color": "pink"},
                        {"name": "Seed ownership", "color": "brown"},
                        {"name": "Scientific authority", "color": "gray"},
                        {"name": "Other", "color": "default"}
                    ]
                }},
                "Confidence": {"select": {
                    "options": [
                        {"name": "High", "color": "green"},
                        {"name": "Medium", "color": "yellow"},
                        {"name": "Low", "color": "red"}
                    ]
                }},
                "Analysis Date": {"date": {}}
            }
            
            # Create the database
            database = self.client.databases.create(
                parent={"page_id": self.parent_page_id},
                title=[{"text": {"content": f"Analysis Run: {run_name}"}}],
                properties=properties,
                is_inline=False  # This makes it a full-page database
            )
            
            if STREAMLIT_AVAILABLE:
                st.success(f"✅ Created Notion database: {database['title'][0]['text']['content']}")
            else:
                print(f"SUCCESS: Created Notion database: {database['title'][0]['text']['content']}")
            return database['id']
            
        except APIResponseError as e:
            if e.code == "rate_limited":
                warning_msg = "Rate limited by Notion API. Retrying in 1 second..."
                if STREAMLIT_AVAILABLE:
                    st.warning(warning_msg)
                else:
                    print(f"WARNING: {warning_msg}")
                time.sleep(1)
                return self.create_run_database(run_name)  # Retry once
            else:
                error_msg = f"Error creating Notion database: {e.message}"
                if STREAMLIT_AVAILABLE:
                    st.error(error_msg)
                else:
                    print(f"ERROR: {error_msg}")
                return None
        except Exception as e:
            error_msg = f"Unexpected error creating Notion database: {str(e)}"
            if STREAMLIT_AVAILABLE:
                st.error(error_msg)
            else:
                print(f"ERROR: {error_msg}")
            return None
    
    def publish_to_notion(self, item: Dict[str, Any], database_id: str) -> bool:
        """
        Insert a result item as a page in the Notion database
        
        Args:
            item (Dict[str, Any]): The analysis result item
            database_id (str): The Notion database ID to publish to
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.client or not database_id:
            return False
            
        try:
            # Prepare the page properties
            properties = {
                "Title": {
                    "title": [{"text": {"content": str(item.get('title', 'Untitled'))[:2000]}}]
                },
                "URL": {
                    "url": str(item.get('url', ''))
                },
                "Content": {
                    "rich_text": [{"text": {"content": str(item.get('content', ''))[:2000]}}]
                },
                "Summary": {
                    "rich_text": [{"text": {"content": str(item.get('summary', ''))[:2000]}}]
                },
                "Claims": {
                    "rich_text": [{"text": {"content": str(item.get('key_claims', []))[:2000]}}]
                },
                "Fact Status": {
                    "select": {"name": str(item.get('fact_myth_status', 'Unclear'))}
                },
                "Classification": {
                    "select": {"name": str(item.get('classification', 'Other'))}
                },
                "Confidence": {
                    "select": {"name": str(item.get('confidence', 'Medium'))}
                },
                "Analysis Date": {
                    "date": {"start": str(item.get('analysis_date', time.strftime('%Y-%m-%d')))}
                }
            }
            
            # Create the page
            page = self.client.pages.create(
                parent={"database_id": database_id},
                properties=properties
            )
            
            return True
            
        except APIResponseError as e:
            if e.code == "rate_limited":
                warning_msg = "Rate limited by Notion API. Retrying in 1 second..."
                if STREAMLIT_AVAILABLE:
                    st.warning(warning_msg)
                else:
                    print(f"WARNING: {warning_msg}")
                time.sleep(1)
                return self.publish_to_notion(item, database_id)  # Retry once
            else:
                error_msg = f"Error publishing to Notion: {e.message}"
                if STREAMLIT_AVAILABLE:
                    st.error(error_msg)
                else:
                    print(f"ERROR: {error_msg}")
                return False
        except Exception as e:
            error_msg = f"Unexpected error publishing to Notion: {str(e)}"
            if STREAMLIT_AVAILABLE:
                st.error(error_msg)
            else:
                print(f"ERROR: {error_msg}")
            return False
    
    def get_database_url(self, database_id: str) -> str:
        """
        Get the URL for a Notion database
        
        Args:
            database_id (str): The Notion database ID
            
        Returns:
            str: The URL to the database
        """
        return f"https://www.notion.so/{database_id.replace('-', '')}"
    
    def is_enabled(self) -> bool:
        """
        Check if Notion publishing is enabled
        
        Returns:
            bool: True if enabled, False otherwise
        """
        return self.publish_to_notion and self.client is not None and self.parent_page_id is not None
