import trafilatura
from typing import List, Dict
import streamlit as st
import time
import json
import os
import tempfile


class ScrapeAgent:
    """Agent responsible for scraping content from URLs using trafilatura"""
    
    def __init__(self, max_content_length: int = 5000, delay_between_requests: float = 1.0):
        self.max_content_length = max_content_length
        self.delay_between_requests = delay_between_requests
        # Create temp folder at project root if it doesn't exist
        self.temp_dir = os.path.join(os.getcwd(), 'temp')
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def scrape_urls(self, urls: List[str]) -> List[Dict[str, str]]:
        """
        Scrape content from a list of URLs
        
        Args:
            urls (List[str]): List of URLs to scrape
            
        Returns:
            List[Dict[str, str]]: List of scraped articles with URL, content, and title
        """
        scraped_articles = []
        total_urls = len(urls)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, url in enumerate(urls):
            status_text.text(f"Scraping {i+1}/{total_urls}: {url}")
            
            try:
                # Download and extract content
                downloaded = trafilatura.fetch_url(url)
                if downloaded:
                    extracted_text = trafilatura.extract(downloaded, include_formatting=True)
                    if extracted_text:
                        # Clean and limit content
                        cleaned_text = self._clean_content(extracted_text)
                        if cleaned_text:
                            # Extract metadata including title
                            metadata = self.get_article_metadata(url)
                            title = metadata.get('title', self._extract_title_from_url(url))
                            
                            article_data = {
                                'url': url,
                                'content': cleaned_text,
                                'title': title
                            }
                            scraped_articles.append(article_data)
                            st.success(f"✅ Successfully scraped: {url}")
                        else:
                            st.warning(f"⚠️ No usable content found: {url}")
                    else:
                        st.warning(f"⚠️ Failed to extract content: {url}")
                else:
                    st.warning(f"⚠️ Failed to download: {url}")
                    
            except Exception as e:
                st.error(f"❌ Error scraping {url}: {str(e)}")
            
            # Update progress
            progress = (i + 1) / total_urls
            progress_bar.progress(progress)
            
            # Delay between requests to be respectful
            if i < total_urls - 1:  # Don't delay after the last request
                time.sleep(self.delay_between_requests)
        
        progress_bar.empty()
        status_text.empty()
        
        st.success(f"Scraping complete! Successfully scraped {len(scraped_articles)} out of {total_urls} URLs")

        # Save results to JSON file in temp folder
        if scraped_articles:
            timestamp = int(time.time())
            json_filename = f"scraped_articles_{timestamp}.json"
            json_filepath = os.path.join(self.temp_dir, json_filename)
            
            with open(json_filepath, 'w', encoding='utf-8') as f:
                json.dump(scraped_articles, f, ensure_ascii=False, indent=2)
            
            st.info(f"🔖 Scraped data saved to: `{json_filepath}`")

        return scraped_articles
    
    def _clean_content(self, text: str) -> str:
        """
        Clean and prepare content for analysis
        
        Args:
            text (str): Raw extracted text
            
        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        cleaned = ' '.join(text.split())
        
        # Remove very short content (likely not useful)
        if len(cleaned) < 100:
            return ""
        
        # Limit content length
        if len(cleaned) > self.max_content_length:
            cleaned = cleaned[:self.max_content_length] + "..."
        
        return cleaned
    
    def _extract_title_from_url(self, url: str) -> str:
        """
        Extract a readable title from URL as fallback
        
        Args:
            url (str): URL to extract title from
            
        Returns:
            str: Extracted title
        """
        try:
            # Try to get the last part of the URL path
            path = url.split('/')[-1]
            if path and '.' not in path:
                return path.replace('-', ' ').replace('_', ' ').title()
            else:
                # Fallback to domain name
                domain = url.split('//')[1].split('/')[0]
                return domain.replace('www.', '').title()
        except:
            return "Untitled"
    
    def get_article_metadata(self, url: str) -> Dict[str, str]:
        """
        Extract metadata from a URL (title, description, etc.)
        
        Args:
            url (str): URL to extract metadata from
            
        Returns:
            Dict[str, str]: Metadata dictionary
        """
        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                metadata = trafilatura.extract_metadata(downloaded)
                return {
                    'title': metadata.title if metadata.title else '',
                    'description': metadata.description if metadata.description else '',
                    'author': metadata.author if metadata.author else '',
                    'date': metadata.date if metadata.date else ''
                }
        except Exception as e:
            st.warning(f"Failed to extract metadata from {url}: {str(e)}")
        
        return {
            'title': '',
            'description': '',
            'author': '',
            'date': ''
        } 