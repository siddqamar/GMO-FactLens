# Refactored Agent System Documentation

## Overview

The agent system has been successfully refactored to include a comprehensive workflow with summarization and fact-checking capabilities. The system now provides real-time streaming results to Streamlit while maintaining all existing functionality.

## New Architecture

### 1. Updated `scrape_agent.py`

**Enhanced Features:**
- ✅ Creates a `temp` folder at project root for file storage
- ✅ Saves scraped results in JSON format with URL, content, and title
- ✅ Extracts article titles from metadata or URL fallback
- ✅ Preserves all existing functionality
- ✅ Real-time progress streaming to Streamlit

**Data Format:**
```json
{
  "url": "https://example.com/article",
  "content": "Extracted article content...",
  "title": "Article Title"
}
```

### 2. New `summary_agent.py`

**Purpose:** Generate concise summaries of scraped content using Google Gemini

**Features:**
- ✅ Takes JSON output from `scrape_agent.py` as input
- ✅ Uses Google Gemini API for intelligent summarization
- ✅ Generates 2-3 sentence summaries focusing on key points
- ✅ Saves results to temp folder as JSON
- ✅ Real-time progress streaming with error handling

**Output Format:**
```json
{
  "url": "https://example.com/article",
  "title": "Article Title",
  "content": "Original content...",
  "summary": "Concise summary of the article..."
}
```

### 3. New `fact_check.py`

**Purpose:** Verify claims from summaries using Google Fact Check API

**Features:**
- ✅ Extracts individual claims from summaries
- ✅ Processes each claim individually through Google Fact Check API
- ✅ Determines fact/myth/unsure status for each claim
- ✅ Calculates overall fact status based on claim results
- ✅ Includes publisher information and review URLs
- ✅ Rate limiting and error handling

**Output Format:**
```json
{
  "url": "https://example.com/article",
  "title": "Article Title",
  "content": "Original content...",
  "summary": "Article summary...",
  "claims": ["Claim 1", "Claim 2"],
  "fact_check_results": [
    {
      "claim": "Claim 1",
      "status": "Fact",
      "rating": "True",
      "publisher": "FactCheck.org",
      "publisher_site": "factcheck.org",
      "review_url": "https://...",
      "review_date": "2024-01-01",
      "confidence": "high"
    }
  ],
  "overall_status": "Fact"
}
```

### 4. Updated `analysis_agent.py`

**New Role:** Main orchestration agent for classification and analysis

**Enhanced Features:**
- ✅ Orchestrates the complete workflow: scraping → summarization → fact-checking → classification
- ✅ Uses Gemini NLP for intelligent classification and analysis
- ✅ Integrates fact-check results into classification decisions
- ✅ Provides comprehensive analysis including sentiment, credibility scores, and key themes
- ✅ Maintains real-time streaming to Streamlit
- ✅ Saves final results to temp folder

**Final Output Format:**
```json
{
  "url": "https://example.com/article",
  "title": "Article Title",
  "content": "Original content...",
  "summary": "Article summary...",
  "claims": ["Claim 1", "Claim 2"],
  "fact_check_results": [...],
  "overall_fact_status": "Fact",
  "classification": "Health",
  "confidence": "high",
  "key_themes": ["health", "science"],
  "analysis_notes": "Reliable source with verified claims",
  "sentiment": "positive",
  "credibility_score": 0.85
}
```

## Workflow Process

### Step 1: Scraping
1. `ScrapeAgent` processes URLs and extracts content
2. Creates temp folder and saves scraped data as JSON
3. Extracts titles from metadata or URL fallback
4. Streams real-time progress to Streamlit

### Step 2: Summarization
1. `SummaryAgent` takes scraped articles as input
2. Uses Google Gemini to generate concise summaries
3. Saves summarized data to temp folder
4. Maintains real-time progress streaming

### Step 3: Fact-Checking
1. `FactCheckAgent` extracts claims from summaries
2. Processes each claim through Google Fact Check API
3. Determines individual and overall fact status
4. Saves fact-check results to temp folder

### Step 4: Classification & Analysis
1. `AnalysisAgent` orchestrates the complete workflow
2. Uses Gemini NLP for intelligent classification
3. Integrates all previous results for comprehensive analysis
4. Provides final results with credibility scores and themes
5. Saves complete analysis to temp folder

## Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Required for summarization and classification
GOOGLE_API_KEY=your_google_gemini_api_key_here

# Required for fact-checking
GOOGLE_FACT_CHECK_API_KEY=your_google_fact_check_api_key_here

# Optional: Database configuration
DATABASE_URL=sqlite:///articles.db

# Optional: Streamlit configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
```

## Dependencies

Updated `requirements.txt` includes:
```
streamlit>=1.28.0
crewai>=0.11.0
trafilatura
google-generativeai>=0.3.0
requests>=2.31.0
python-dotenv>=1.0.0
plotly>=5.15.0
pandas>=2.0.0
google-api-python-client>=2.0.0
```

## File Structure

```
project1/
├── agents/
│   ├── __init__.py
│   ├── scrape_agent.py          # ✅ Updated
│   ├── summary_agent.py         # ✅ New
│   ├── fact_check.py            # ✅ New
│   ├── analysis_agent.py        # ✅ Updated
│   └── search_agent.py          # Unchanged
├── temp/                        # ✅ New folder for file storage
│   ├── scraped_articles_*.json
│   ├── summarized_articles_*.json
│   ├── fact_checked_articles_*.json
│   └── final_analysis_*.json
├── ui/
├── database/
├── requirements.txt             # ✅ Updated
├── test_agents.py              # ✅ New test script
└── REFACTORED_SYSTEM_README.md # ✅ This file
```

## Testing

Run the test script to verify the system:

```bash
python test_agents.py
```

This will:
- ✅ Test all agent imports
- ✅ Verify agent initialization
- ✅ Check temp folder creation
- ✅ Validate environment variables

## Real-Time Streaming

All agents maintain real-time streaming to Streamlit:
- ✅ Progress bars for each step
- ✅ Status messages for each article
- ✅ Success/error notifications
- ✅ File save confirmations

## Error Handling

Comprehensive error handling throughout:
- ✅ API failures with fallback results
- ✅ Network timeouts and retries
- ✅ JSON parsing errors
- ✅ Missing environment variables
- ✅ File system errors

## Benefits of Refactoring

1. **Modular Design:** Each agent has a specific responsibility
2. **Comprehensive Analysis:** Fact-checking adds credibility assessment
3. **Real-Time Feedback:** Users see progress at each step
4. **Data Persistence:** All results saved to temp folder for review
5. **Scalable Architecture:** Easy to add new agents or modify existing ones
6. **Better Error Handling:** Graceful degradation when services fail
7. **Enhanced Classification:** Fact-check results inform classification decisions

## Usage Example

```python
from agents.analysis_agent import AnalysisAgent

# Initialize the main agent (orchestrates everything)
agent = AnalysisAgent()

# Process articles through the complete workflow
urls = ["https://example.com/article1", "https://example.com/article2"]
scraped_articles = scrape_agent.scrape_urls(urls)

# The analysis agent handles the entire workflow internally
final_results = agent.analyze_articles(scraped_articles)

# Results include scraping, summarization, fact-checking, and classification
for result in final_results:
    print(f"URL: {result['url']}")
    print(f"Title: {result['title']}")
    print(f"Summary: {result['summary']}")
    print(f"Fact Status: {result['overall_fact_status']}")
    print(f"Classification: {result['classification']}")
    print(f"Credibility Score: {result['credibility_score']}")
    print("---")
```

## Next Steps

The refactored system is ready for use. You can now:
1. Set up your environment variables
2. Run the test script to verify everything works
3. Use the system through your existing Streamlit interface
4. Review the generated JSON files in the temp folder
5. Customize the classification prompts as needed

All existing functionality has been preserved while adding powerful new capabilities for summarization and fact-checking!
