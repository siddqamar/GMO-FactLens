import os
from crewai import Agent, Task, Crew, Process
from typing import List, Dict, Any
import streamlit as st
from agents.search_agent import SearchAgent
from agents.scrape_agent import ScrapeAgent
from agents.analysis_agent import AnalysisAgent

# NEW: Import the Google Generative AI model from LangChain
from langchain_google_genai import ChatGoogleGenerativeAI

class CrewAIWorkflow:
    """Orchestrates the entire crewAI workflow for article analysis"""
    
    def __init__(self):
        self.search_agent = SearchAgent()
        self.scrape_agent = ScrapeAgent()
        self.analysis_agent = AnalysisAgent()
    
    def run_analysis(self, topic: str) -> List[Dict[str, Any]]:
        """
        Run the complete analysis workflow
        
        Args:
            topic (str): Topic to search for and analyze
            
        Returns:
            List[Dict[str, Any]]: List of analyzed articles
        """
        st.info(f"Starting analysis for topic: '{topic}'")
        
        # Step 1: Search for URLs
        with st.spinner("🔍 Searching for relevant articles..."):
            urls = self.search_agent.search_urls(topic, max_results=10)
            if not urls:
                st.error("No URLs found. Please try a different topic.")
                return []
            
            # Validate URLs
            valid_urls = self.search_agent.validate_urls(urls)
            if not valid_urls:
                st.error("No valid URLs found after validation.")
                return []
        
        # Step 2: Scrape content
        with st.spinner("📄 Scraping article content..."):
            scraped_articles = self.scrape_agent.scrape_urls(valid_urls)
            if not scraped_articles:
                st.error("No articles could be scraped successfully.")
                return []
        
        # Step 3: Analyze articles
        with st.spinner("🤖 Analyzing and classifying articles..."):
            analyzed_articles = self.analysis_agent.analyze_articles(scraped_articles)
            if not analyzed_articles:
                st.error("No articles could be analyzed successfully.")
                return []
        
        st.success(f"✅ Analysis complete! Processed {len(analyzed_articles)} articles.")
        return analyzed_articles
    
    def run_crewai_workflow(self, topic: str) -> List[Dict[str, Any]]:
        """
        Run the analysis using crewAI framework (alternative method)
        
        Args:
            topic (str): Topic to search for and analyze
            
        Returns:
            List[Dict[str, Any]]: List of analyzed articles
        """
        # NEW: Configure the Google Generative AI model
        # Make sure your GOOGLE_API_KEY is set in your .env file
        if not os.getenv("GOOGLE_API_KEY"):
            st.error("GOOGLE_API_KEY environment variable not set. Please add it to your .env file.")
            return []
            
        llm_model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",  # You can also use "gemini-1.5-flash"
            verbose=True,
            temperature=0.2
        )
        
        # Create crewAI agents
        # The key change is adding `llm=llm_model` to each agent
        search_agent = Agent(
            role='Web Search Specialist',
            goal='Find the most relevant URLs for the given topic',
            backstory='Expert at finding high-quality, relevant web content using SerperAPI',
            verbose=True,
            allow_delegation=False,
            # llm=llm_model, # Search agents typically don't need an LLM unless they're reasoning
            function=self._search_agent_function
        )
        
        scrape_agent = Agent(
            role='Content Scraper',
            goal='Extract clean, readable content from web pages',
            backstory='Specialist in extracting and cleaning web content using trafilatura',
            verbose=True,
            allow_delegation=False,
            # llm=llm_model, # Scrape agents typically don't need an LLM
            function=self._scrape_agent_function
        )
        
        analyze_agent = Agent(
            role='Content Analyst',
            goal='Analyze, summarize, and classify article content',
            backstory='Expert at content analysis and classification using Google Gemini',
            verbose=True,
            allow_delegation=False,
            llm=llm_model, # <-- This is where the LLM is needed and passed
            function=self._analysis_agent_function
        )
        
        # Create tasks
        search_task = Task(
            description=f'Search for the top 10 most relevant URLs about "{topic}"',
            agent=search_agent,
            expected_output='List of 10 relevant URLs'
        )
        
        scrape_task = Task(
            description='Scrape content from the provided URLs',
            agent=scrape_agent,
            expected_output='List of scraped articles with content',
            context=[search_task]
        )
        
        analyze_task = Task(
            description='Analyze, summarize, and classify the scraped articles',
            agent=analyze_agent,
            expected_output='List of analyzed articles with summaries and classifications',
            context=[scrape_task]
        )
        
        # Create and run crew
        crew = Crew(
            agents=[search_agent, scrape_agent, analyze_agent],
            tasks=[search_task, scrape_task, analyze_task],
            process=Process.sequential,
            verbose=True
        )
        
        try:
            result = crew.kickoff()
            
            # Extract the final results from the analyze task
            if hasattr(result, 'raw') and result.raw:
                return result.raw
            else:
                st.warning("CrewAI workflow completed but no results returned.")
                return []
                
        except Exception as e:
            st.error(f"Error in crewAI workflow: {str(e)}")
            return []
    
    def _search_agent_function(self, topic: str) -> List[str]:
        """Function wrapper for search agent in crewAI"""
        return self.search_agent.search_urls(topic, max_results=10)
    
    def _scrape_agent_function(self, urls: List[str]) -> List[Dict[str, str]]:
        """Function wrapper for scrape agent in crewAI"""
        return self.scrape_agent.scrape_urls(urls)
    
    def _analysis_agent_function(self, articles: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Function wrapper for analysis agent in crewAI"""
        return self.analysis_agent.analyze_articles(articles)
    
    def get_workflow_summary(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a summary of the workflow results
        
        Args:
            articles (List[Dict[str, Any]]): List of analyzed articles
            
        Returns:
            Dict[str, Any]: Workflow summary
        """
        if not articles:
            return {}
        
        # Get analysis summary
        analysis_summary = self.analysis_agent.get_analysis_summary(articles)
        
        # Add workflow-specific metrics
        workflow_summary = {
            'workflow_type': 'article_analysis',
            'total_articles_processed': len(articles),
            'successful_analyses': analysis_summary.get('successful_analyses', 0),
            'failed_analyses': len(articles) - analysis_summary.get('successful_analyses', 0),
            'analysis_summary': analysis_summary
        }
        
        return workflow_summary