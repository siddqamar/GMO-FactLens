import requests
import os
from typing import List, Dict, Any
import streamlit as st
import json
import time
import re


class FactCheckAgent:
    """Agent responsible for fact-checking claims using Google Fact Check API"""
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_FACT_CHECK_API_KEY')
        if not self.api_key:
            st.error("GOOGLE_FACT_CHECK_API_KEY not found in environment variables")
            self.api_key = None
        
        self.base_url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
        
        # Create temp folder at project root if it doesn't exist
        self.temp_dir = os.path.join(os.getcwd(), 'temp')
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def fact_check_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Fact-check claims in summarized articles
        
        Args:
            articles (List[Dict[str, Any]]): List of articles with summaries
            
        Returns:
            List[Dict[str, Any]]: List of articles with fact-check results
        """
        if not self.api_key:
            st.error("Cannot perform fact-checking without API key")
            return articles
        
        fact_checked_articles = []
        total_articles = len(articles)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, article in enumerate(articles):
            status_text.text(f"Fact-checking {i+1}/{total_articles}: {article['url']}")
            
            try:
                fact_check_result = self._fact_check_single_article(article)
                fact_checked_articles.append(fact_check_result)
                st.success(f"✅ Successfully fact-checked: {article['url']}")
                
            except Exception as e:
                st.error(f"❌ Error fact-checking {article['url']}: {str(e)}")
                # Add fallback result
                fact_checked_articles.append(self._create_fallback_result(article))
            
            # Update progress
            progress = (i + 1) / total_articles
            progress_bar.progress(progress)
            
            # Small delay to avoid rate limiting
            if i < total_articles - 1:
                time.sleep(1.0)
        
        progress_bar.empty()
        status_text.empty()
        
        st.success(f"Fact-checking complete! Successfully checked {len(fact_checked_articles)} articles")
        
        # Save results to JSON file in temp folder
        if fact_checked_articles:
            timestamp = int(time.time())
            json_filename = f"fact_checked_articles_{timestamp}.json"
            json_filepath = os.path.join(self.temp_dir, json_filename)
            
            with open(json_filepath, 'w', encoding='utf-8') as f:
                json.dump(fact_checked_articles, f, ensure_ascii=False, indent=2)
            
            st.info(f"🔖 Fact-checked data saved to: `{json_filepath}`")
        
        return fact_checked_articles
    
    def _fact_check_single_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fact-check claims in a single article
        
        Args:
            article (Dict[str, Any]): Article with summary
            
        Returns:
            Dict[str, Any]: Article with fact-check results
        """
        # Extract claims from summary
        claims = self._extract_claims(article['summary'])
        
        # Fact-check each claim
        fact_check_results = []
        for claim in claims:
            claim_result = self._check_single_claim(claim)
            fact_check_results.append(claim_result)
        
        # Determine overall fact/myth status
        overall_status = self._determine_overall_status(fact_check_results)
        
        return {
            'url': article['url'],
            'title': article.get('title', 'Untitled'),
            'content': article.get('content', ''),
            'summary': article['summary'],
            'claims': claims,
            'fact_check_results': fact_check_results,
            'overall_status': overall_status
        }
    
    def _extract_claims(self, summary: str) -> List[str]:
        """
        Extract individual claims from summary text
        
        Args:
            summary (str): Summary text to extract claims from
            
        Returns:
            List[str]: List of individual claims
        """
        # Split by sentences and filter out very short ones
        sentences = re.split(r'[.!?]+', summary)
        claims = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20:  # Only consider substantial sentences
                claims.append(sentence)
        
        # If no substantial claims found, return the summary as a single claim
        if not claims:
            claims = [summary]
        
        return claims[:5]  # Limit to 5 claims to avoid API rate limits
    
    def _check_single_claim(self, claim: str) -> Dict[str, Any]:
        """
        Check a single claim using Google Fact Check API
        
        Args:
            claim (str): Claim to check
            
        Returns:
            Dict[str, Any]: Fact-check result
        """
        try:
            params = {
                'query': claim,
                'key': self.api_key,
                'languageCode': 'en'
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'claims' in data and data['claims']:
                # Found fact-check results
                claim_data = data['claims'][0]
                claimReview = claim_data.get('claimReview', [])
                
                if claimReview:
                    review = claimReview[0]
                    publisher = review.get('publisher', {})
                    
                    return {
                        'claim': claim,
                        'status': 'Fact' if review.get('textualRating', '').lower() in ['true', 'fact'] else 'Myth',
                        'rating': review.get('textualRating', 'Unknown'),
                        'publisher': publisher.get('name', 'Unknown'),
                        'publisher_site': publisher.get('site', ''),
                        'review_url': review.get('url', ''),
                        'review_date': review.get('reviewDate', ''),
                        'confidence': 'high'
                    }
            
            # No fact-check results found
            return {
                'claim': claim,
                'status': 'Unsure',
                'rating': 'No fact-check found',
                'publisher': 'None',
                'publisher_site': '',
                'review_url': '',
                'review_date': '',
                'confidence': 'low'
            }
            
        except Exception as e:
            st.warning(f"Error checking claim '{claim[:50]}...': {str(e)}")
            return {
                'claim': claim,
                'status': 'Unsure',
                'rating': 'Error occurred',
                'publisher': 'None',
                'publisher_site': '',
                'review_url': '',
                'review_date': '',
                'confidence': 'low'
            }
    
    def _determine_overall_status(self, fact_check_results: List[Dict[str, Any]]) -> str:
        """
        Determine overall fact/myth status based on individual claim results
        
        Args:
            fact_check_results (List[Dict[str, Any]]): Results for individual claims
            
        Returns:
            str: Overall status (Fact, Myth, or Unsure)
        """
        if not fact_check_results:
            return 'Unsure'
        
        fact_count = sum(1 for result in fact_check_results if result['status'] == 'Fact')
        myth_count = sum(1 for result in fact_check_results if result['status'] == 'Myth')
        unsure_count = sum(1 for result in fact_check_results if result['status'] == 'Unsure')
        
        # If we have clear results, use majority
        if fact_count > myth_count and fact_count > unsure_count:
            return 'Fact'
        elif myth_count > fact_count and myth_count > unsure_count:
            return 'Myth'
        else:
            return 'Unsure'
    
    def _create_fallback_result(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a fallback result when fact-checking fails
        
        Args:
            article (Dict[str, Any]): Original article
            
        Returns:
            Dict[str, Any]: Fallback fact-check result
        """
        return {
            'url': article['url'],
            'title': article.get('title', 'Untitled'),
            'content': article.get('content', ''),
            'summary': article.get('summary', ''),
            'claims': [],
            'fact_check_results': [],
            'overall_status': 'Unsure'
        }
