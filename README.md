# Article Analysis Tool

A comprehensive web application that uses **Streamlit** for the frontend and **crewAI** for backend processing to find, scrape, summarize, and classify online articles. The application determines if article claims are based on fact or myth and classifies them into predefined categories.

## 🏗️ Project Structure

```
project1/
├── main.py                 # Main entry point
├── crewai_workflow.py      # CrewAI workflow orchestration
├── database/
│   ├── __init__.py
│   └── db_manager.py       # SQLite database operations
├── agents/
│   ├── __init__.py
│   ├── search_agent.py     # Web search using SerperAPI
│   ├── scrape_agent.py     # Content scraping using trafilatura
│   └── analysis_agent.py   # AI analysis using Google Gemini
├── ui/
│   ├── __init__.py
│   └── streamlit_ui.py     # Streamlit user interface
├── pyproject.toml          # Project dependencies
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── .gitignore             # Git ignore patterns
└── articles.db            # SQLite database (created automatically)
```

## ✨ Features

- 🔍 **Web Search**: Uses SerperAPI to find relevant articles
- 📄 **Content Scraping**: Extracts clean content using trafilatura
- 🤖 **AI Analysis**: Uses Google Gemini for summarization and classification
- ✅ **Fact Checking**: Assesses claims as Fact, Myth, or Unclear
- 🗂️ **Database Storage**: Saves results to SQLite database with session tracking
- 📊 **Beautiful UI**: Clean Streamlit interface with real-time updates
- 📈 **Data Visualization**: Charts and graphs using Plotly
- 📥 **Export Results**: Download analysis as JSON or CSV
- 🔄 **Session History**: Track analysis sessions and results
- ⚙️ **Configurable Options**: Choose between direct processing or CrewAI framework

## 📋 Article Categories

The application classifies articles into nine categories:
1. **Health** 🏥
2. **Environmental** 🌱
3. **Social Economics** 💰
4. **Conspiracy Theory** 🤔
5. **Corporate Control** 🏢
6. **Ethical/Religious Issues** ⛪
7. **Seed Ownership** 🌾
8. **Scientific Authority** 🔬
9. **Other** 📋

## 🛠️ Prerequisites

- Python 3.11 or higher
- SerperAPI key (for web search)
- Google API key (for Gemini AI)

## 📦 Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API keys**:
   
   Create a `.env` file in the project root:
   ```env
   SERPER_API_KEY=your_serper_api_key_here
   GOOGLE_API_KEY=your_google_api_key_here
   ```
   
   Or set environment variables:
   ```bash
   # Windows
   set SERPER_API_KEY=your_serper_api_key_here
   set GOOGLE_API_KEY=your_google_api_key_here
   
   # Linux/Mac
   export SERPER_API_KEY=your_serper_api_key_here
   export GOOGLE_API_KEY=your_google_api_key_here
   ```

## 🔑 Getting API Keys

### SerperAPI Key
1. Visit [serper.dev](https://serper.dev)
2. Sign up for a free account
3. Get your API key from the dashboard

### Google API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Enable the Gemini API

## 🚀 Usage

1. **Run the application**:
   ```bash
   streamlit run main.py
   ```

2. **Open your browser** and navigate to the URL shown (usually `http://localhost:8501`)

3. **Enter a topic** in the sidebar (e.g., "global warming myths", "vaccine safety", "5G conspiracy")

4. **Configure options**:
   - Choose between CrewAI framework or direct processing
   - Set maximum number of results (5-20)

5. **Click "Run Analysis"** to start the process

6. **View results** in organized tabs:
   - **Articles**: Individual article analysis with expandable details
   - **Charts**: Visualizations of classification and fact/myth distribution
   - **Export**: Download results as JSON or CSV

## 🔄 Application Workflow

1. **User Input**: Topic entered in Streamlit interface
2. **Search Agent**: Uses SerperAPI to find top 10 relevant URLs
3. **Scrape Agent**: Extracts content using trafilatura with progress tracking
4. **Analysis Agent**: Uses Gemini to:
   - Generate summaries
   - Classify articles
   - Assess fact/myth status
   - Provide confidence levels
5. **Database Storage**: Results saved to `articles.db` with session tracking
6. **Display**: Results shown in clean, organized format with visualizations

## 🗄️ Database Schema

The application creates a SQLite database (`articles.db`) with two main tables:

### Articles Table
```sql
CREATE TABLE articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL UNIQUE,
    title TEXT,
    summary TEXT,
    classification TEXT,
    fact_myth_status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Analysis Sessions Table
```sql
CREATE TABLE analysis_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL,
    articles_found INTEGER,
    facts_count INTEGER,
    myths_count INTEGER,
    unclear_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🏛️ Architecture

### Modular Design
- **Database Layer**: Handles all SQLite operations with proper error handling
- **Agent Layer**: Three specialized agents for search, scraping, and analysis
- **Workflow Layer**: Orchestrates the entire process using crewAI
- **UI Layer**: Clean Streamlit interface with advanced features

### Key Components
- **DatabaseManager**: Handles database operations and statistics
- **SearchAgent**: Manages web search using SerperAPI
- **ScrapeAgent**: Handles content extraction with progress tracking
- **AnalysisAgent**: Performs AI analysis using Google Gemini
- **CrewAIWorkflow**: Orchestrates the entire workflow
- **StreamlitUI**: Manages all user interface components

## 🔧 Configuration

### Environment Variables
- `SERPER_API_KEY`: Required for web search functionality
- `GOOGLE_API_KEY`: Required for AI analysis

### Analysis Options
- **CrewAI Framework**: Use the full crewAI workflow (recommended)
- **Direct Processing**: Use direct agent calls (faster but less robust)
- **Maximum Results**: Configure number of articles to analyze (5-20)

## 📊 Features

### Real-time Progress Tracking
- Progress bars for each processing step
- Status messages with detailed information
- Error handling with user-friendly messages

### Data Visualization
- Pie charts for article classification
- Bar charts for fact/myth distribution
- Interactive charts using Plotly

### Export Options
- JSON export with full analysis data
- CSV export for spreadsheet analysis
- Timestamped filenames for organization

### Session Management
- Track analysis history
- Database statistics in sidebar
- Recent session display

## 🐛 Troubleshooting

### Common Issues

1. **API Key Errors**:
   - Ensure both API keys are set correctly
   - Check the API key status in the sidebar
   - Verify API keys have sufficient credits

2. **No Results Found**:
   - Try a different search term
   - Check internet connection
   - Verify SerperAPI is working

3. **Analysis Failures**:
   - Check Google API key and Gemini access
   - Some articles may fail to scrape (this is normal)
   - Check the console for detailed error messages

4. **Import Errors**:
   - Ensure all dependencies are installed
   - Check Python version (3.11+ required)
   - Verify project structure is intact

### Performance Notes

- The application processes only the top 10 search results by default
- Content is limited to 5000 characters for analysis
- Processing time depends on article count and content length
- Use specific search terms for better results
- CrewAI framework provides better error handling but may be slower

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve the application.

## 📄 License

This project is open source and available under the MIT License.

## 🔄 Version History

- **v2.0**: Modular architecture with enhanced features
- **v1.0**: Initial single-file implementation
