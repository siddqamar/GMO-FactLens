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
                # Notion client initialized successfully (no UI message needed)
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

    def publish_item_to_notion(self, item: Dict[str, Any], database_id: str) -> bool:
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
            # Helper function to safely get and format text content
            def safe_text_content(value, max_length=2000):
                if value is None:
                    return ""
                if isinstance(value, list):
                    # Join list items with commas
                    text = ", ".join(str(item) for item in value if item)
                else:
                    text = str(value)
                return text[:max_length] if text else ""

            # Helper function to validate select field values
            def validate_select_value(value, field_name, default_value):
                if value is None:
                    return default_value

                # Convert to string and handle boolean values
                str_value = str(value).strip()

                # Define valid options for each select field
                valid_options = {
                    "Fact Status": ["Fact", "Myth", "Unclear"],
                    "Classification": ["Health", "Environmental", "Social economics", "Conspiracy theory",
                                    "Corporate control", "Ethical/religious issues", "Seed ownership",
                                    "Scientific authority", "Other"],
                    "Confidence": ["High", "Medium", "Low"]
                }

                if field_name in valid_options:
                    # Check if the value matches any valid option (case-insensitive)
                    for option in valid_options[field_name]:
                        if str_value.lower() == option.lower():
                            return option
                    # If no match found, return default
                    return default_value

                return str_value

            # Prepare the page properties
            properties = {
                "Title": {
                    "title": [{"text": {"content": safe_text_content(item.get('title', 'Untitled'), 2000)}}]
                },
                "URL": {
                    "url": str(item.get('url', '')) if item.get('url') else ""
                },
                "Content": {
                    "rich_text": [{"text": {"content": safe_text_content(item.get('content', ''), 2000)}}]
                },
                "Summary": {
                    "rich_text": [{"text": {"content": safe_text_content(item.get('summary', ''), 2000)}}]
                },
                "Claims": {
                    "rich_text": [{"text": {"content": safe_text_content(item.get('key_claims', []), 2000)}}]
                },
                "Fact Status": {
                    "select": {"name": validate_select_value(item.get('fact_myth_status'), "Fact Status", "Unclear")}
                },
                "Classification": {
                    "select": {"name": validate_select_value(item.get('classification'), "Classification", "Other")}
                },
                "Confidence": {
                    "select": {"name": validate_select_value(item.get('confidence'), "Confidence", "Medium")}
                },
                "Analysis Date": {
                    "date": {"start": str(item.get('analysis_date', time.strftime('%Y-%m-%d')))}
                }
            }

            # Filter out empty properties to avoid API errors
            filtered_properties = {}
            for key, value in properties.items():
                if key == "Title":
                    # Title is required, always include it
                    filtered_properties[key] = value
                elif key == "URL":
                    # URL can be empty string
                    filtered_properties[key] = value
                elif key == "Analysis Date":
                    # Date is required, always include it
                    filtered_properties[key] = value
                elif isinstance(value, dict) and "rich_text" in value:
                    # Only include rich_text if it has content
                    if value["rich_text"][0]["text"]["content"].strip():
                        filtered_properties[key] = value
                elif isinstance(value, dict) and "select" in value:
                    # Only include select if it has a valid name
                    if value["select"]["name"]:
                        filtered_properties[key] = value
                else:
                    filtered_properties[key] = value

            # Create the page
            page = self.client.pages.create(
                parent={"database_id": database_id},
                properties=filtered_properties
            )

            if STREAMLIT_AVAILABLE:
                st.success(f"✅ Published item to Notion: {item.get('title', 'Untitled')[:50]}...")
            else:
                print(f"SUCCESS: Published item to Notion: {item.get('title', 'Untitled')[:50]}...")

            return True

        except APIResponseError as e:
            if e.code == "rate_limited":
                warning_msg = "Rate limited by Notion API. Retrying in 1 second..."
                if STREAMLIT_AVAILABLE:
                    st.warning(warning_msg)
                else:
                    print(f"WARNING: {warning_msg}")
                time.sleep(1)
                return self.publish_item_to_notion(item, database_id)  # Retry once
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
