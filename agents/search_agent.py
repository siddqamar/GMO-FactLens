import requests
import os
from typing import List
import streamlit as st

class SearchAgent:
    """Agent responsible for searching and finding relevant URLs using SerperAPI"""
    
    def __init__(self):
        self.api_key = os.getenv('SERPER_API_KEY')
        self.base_url = "https://google.serper.dev/search"
    
    def search_urls(self, topic: str, max_results: int = 3) -> List[str]:
        """
        Search for URLs related to the given topic using SerperAPI
        
        Args:
            topic (str): The search topic
            max_results (int): Maximum number of results to return (default: 10)
            
        Returns:
            List[str]: List of URLs found
        """
        if not self.api_key:
            st.error("SERPER_API_KEY not found in environment variables")
            return []
        
        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
        payload = {
            'q': topic,
            'num': max_results
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            urls = []
            if 'organic' in data:
                for result in data['organic'][:max_results]:
                    if 'link' in result:
                        urls.append(result['link'])
            
            st.success(f"Found {len(urls)} URLs for topic: '{topic}'")
            return urls
            
        except requests.exceptions.RequestException as e:
            st.error(f"Error searching for URLs: {str(e)}")
            return []
        except Exception as e:
            st.error(f"Unexpected error during search: {str(e)}")
            return []
    
    def validate_urls(self, urls: List[str]) -> List[str]:
        """
        Validate URLs and filter out invalid ones
        
        Args:
            urls (List[str]): List of URLs to validate
            
        Returns:
            List[str]: List of valid URLs
        """
        valid_urls = []
        for url in urls:
            if url.startswith(('http://', 'https://')):
                valid_urls.append(url)
            else:
                st.warning(f"Skipping invalid URL: {url}")
        
        return valid_urls 