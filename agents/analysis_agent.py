import google.generativeai as genai
import os
from typing import List, Dict, Any
import streamlit as st
import json
import time

class AnalysisAgent:
    """Agent responsible for analyzing, summarizing, and classifying articles using Google Gemini"""
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
        
        # Predefined categories for classification
        self.categories = [
            "Health", "Environmental", "Social economics", "Conspiracy theory",
            "Corporate control", "Ethical/religious issues", "Seed ownership",
            "Scientific authority", "Other"
        ]
    
    def analyze_articles(self, articles: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Analyze a list of articles for summarization, classification, and fact-checking
        
        Args:
            articles (List[Dict[str, str]]): List of articles with URL and content
            
        Returns:
            List[Dict[str, Any]]: List of analyzed articles with results
        """
        if not self.model:
            st.error("GOOGLE_API_KEY not found in environment variables")
            return []
        
        analyzed_articles = []
        total_articles = len(articles)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, article in enumerate(articles):
            status_text.text(f"Analyzing {i+1}/{total_articles}: {article['url']}")
            
            try:
                analysis_result = self._analyze_single_article(article)
                analyzed_articles.append(analysis_result)
                st.success(f"✅ Successfully analyzed: {article['url']}")
                
            except Exception as e:
                st.error(f"❌ Error analyzing {article['url']}: {str(e)}")
                # Add fallback result
                analyzed_articles.append(self._create_fallback_result(article))
            
            # Update progress
            progress = (i + 1) / total_articles
            progress_bar.progress(progress)
            
            # Small delay to avoid rate limiting
            if i < total_articles - 1:
                time.sleep(0.5)
        
        progress_bar.empty()
        status_text.empty()
        
        st.success(f"Analysis complete! Successfully analyzed {len(analyzed_articles)} articles")
        return analyzed_articles
    
    def _analyze_single_article(self, article: Dict[str, str]) -> Dict[str, Any]:
        """
        Analyze a single article
        
        Args:
            article (Dict[str, str]): Article with URL and content
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        # Create analysis prompt
        prompt = self._create_analysis_prompt(article)
        
        # Get response from Gemini
        response = self.model.generate_content(prompt)
        
        # Parse JSON response
        try:
            analysis = json.loads(response.text)
            
            return {
                'url': article['url'],
                'title': self._extract_title_from_url(article['url']),
                'summary': analysis.get('summary', ''),
                'classification': analysis.get('classification', 'Other'),
                'fact_myth_status': analysis.get('fact_myth_status', 'Unclear'),
                'confidence': analysis.get('confidence', 'medium'),
                'key_claims': analysis.get('key_claims', []),
                'analysis_notes': analysis.get('analysis_notes', '')
            }
            
        except json.JSONDecodeError as e:
            st.warning(f"Failed to parse JSON response for {article['url']}: {str(e)}")
            return self._create_fallback_result(article)
    
    def _create_analysis_prompt(self, article: Dict[str, str]) -> str:
        """
        Create a comprehensive analysis prompt for Gemini
        
        Args:
            article (Dict[str, str]): Article to analyze
            
        Returns:
            str: Formatted prompt
        """
        return f"""
        Analyze the following article content and provide a comprehensive analysis in JSON format.
        
        Article URL: {article['url']}
        Article Content: {article['content'][:3000]}
        
        Please provide the following analysis in JSON format:
        {{
            "summary": "A concise 2-3 sentence summary of the main points",
            "classification": "One of these categories: {', '.join(self.categories)}",
            "fact_myth_status": "One of: Fact, Myth, or Unclear",
            "confidence": "One of: high, medium, low",
            "key_claims": ["List of main claims made in the article"],
            "analysis_notes": "Brief notes about the analysis process"
        }}
        
        Guidelines:
        - Be objective and analytical
        - Classify based on the main topic/theme of the article
        - Assess fact/myth status based on verifiable claims
        - Provide confidence level based on clarity of claims
        - Focus on the most important claims for key_claims array
        
        Respond only with valid JSON.
        """
    
    def _extract_title_from_url(self, url: str) -> str:
        """
        Extract a readable title from URL
        
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
    
    def _create_fallback_result(self, article: Dict[str, str]) -> Dict[str, Any]:
        """
        Create a fallback result when analysis fails
        
        Args:
            article (Dict[str, str]): Original article
            
        Returns:
            Dict[str, Any]: Fallback analysis result
        """
        return {
            'url': article['url'],
            'title': self._extract_title_from_url(article['url']),
            'summary': 'Analysis failed - unable to process content',
            'classification': 'Other',
            'fact_myth_status': 'Unclear',
            'confidence': 'low',
            'key_claims': [],
            'analysis_notes': 'Analysis failed due to processing error'
        }
    
    def get_analysis_summary(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary statistics for analyzed articles
        
        Args:
            articles (List[Dict[str, Any]]): List of analyzed articles
            
        Returns:
            Dict[str, Any]: Summary statistics
        """
        if not articles:
            return {}
        
        # Count by classification
        classification_counts = {}
        for category in self.categories:
            classification_counts[category] = sum(
                1 for a in articles if a.get('classification') == category
            )
        
        # Count by fact/myth status
        status_counts = {
            'Fact': sum(1 for a in articles if a.get('fact_myth_status') == 'Fact'),
            'Myth': sum(1 for a in articles if a.get('fact_myth_status') == 'Myth'),
            'Unclear': sum(1 for a in articles if a.get('fact_myth_status') == 'Unclear')
        }
        
        # Count by confidence
        confidence_counts = {
            'high': sum(1 for a in articles if a.get('confidence') == 'high'),
            'medium': sum(1 for a in articles if a.get('confidence') == 'medium'),
            'low': sum(1 for a in articles if a.get('confidence') == 'low')
        }
        
        return {
            'total_articles': len(articles),
            'classification_counts': classification_counts,
            'status_counts': status_counts,
            'confidence_counts': confidence_counts,
            'successful_analyses': sum(1 for a in articles if a.get('summary') != 'Analysis failed - unable to process content')
        } 