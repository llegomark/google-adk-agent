# Info Hub Agent

A multi-functional information retrieval agent built with Google's Agent Development Kit (ADK) that provides access to multiple information sources through a unified interface.

## Features

- **Web Search**: Search the internet for general information, weather, and news
- **Tech News**: Get the latest posts from Hacker News and trending GitHub repositories
- **Education News**: Access the latest news, press releases, and memoranda from the Department of Education (DepEd)
- **Unified Interface**: Ask questions naturally and the agent will route to the appropriate specialized agent

## Prerequisites

- Python
- Google Gemini API Key

## Installation

1. **Install ADK and helper libraries**:
```bash
pip install google-adk
pip install requests beautifulsoup4
```

2. **Set up your credentials**:
   - Create a `.env` file in the info_hub_agent directory. Replace the 
   ```
   GOOGLE_GENAI_USE_VERTEXAI="False"
   GOOGLE_API_KEY="AIzaSyD......"
   ```

## Usage

1. **Start the Web UI**:
```bash
adk web
```

2. **Access the interface**:
   - Visit [http://localhost:8000/](http://localhost:8000/) in your browser

3. **Example queries**:
   - "What's the latest tech news?"
   - "Show me trending GitHub repositories"
   - "What are the recent DepEd memoranda?"
   - "What's the weather in Manila today?"
   - "Tell me about the latest education initiatives in the Philippines"

## Architecture

This agent uses a coordinator pattern with specialized sub-agents:

- **Information Coordinator**: Routes requests to the appropriate specialized agent
- **Search Assistant**: Handles general web searches using Google Search
- **HackerNews Agent**: Retrieves tech news from Hacker News and GitHub trending repositories
- **DepEd Agent**: Fetches and parses news from the Department of Education RSS feed

## 🙏 Acknowledgements

Built with [Google Agent Development Kit (ADK)](https://github.com/google/adk-python), an open-source toolkit for building AI agents.