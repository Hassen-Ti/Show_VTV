# 📺 Show V.TV - AI Debate System with Mr Bullshit

A PyQt6-based application featuring two AI agents that engage in fierce, fact-based debates using OpenAI's GPT-4o model with **real-time web search capabilities**.

## 🚀 Features

### Core Debate System
- **Two AI agents** with distinct personalities:
  - **Agent One (🔥)**: Aggressive tech optimist with fact-based arguments
  - **Agent Two (💀)**: Fierce tech skeptic with evidence-based criticism
- **Real-time streaming** responses with live typing effect
- **Stop/Start controls** for interactive debate management
- **Modern neon UI** with visual indicators and emojis

### 🔍 NEW: Web Search Integration
- **Intelligent research**: Agents automatically search for real articles and statistics
- **Fact-based arguments**: Every claim backed by search results and citations
- **Visual search indicators**: See when agents are researching
- **Contextual searches**: Agents find relevant studies, statistics, and expert opinions
- **Multi-source validation**: Both success stories and failure cases

### 📊 Smart Debate Features
- **Concise responses**: Maximum 2-3 sentences per exchange
- **High-temperature generation**: More creative and unpredictable arguments (1.2 temperature)
- **Proper message formatting**: Clear round numbering and spacing
- **Auto-scrolling**: Always see the latest arguments
- **Error handling**: Graceful fallback when search APIs are unavailable

## 📋 Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure OpenAI API key**:
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=your-api-key-here
     ```

3. **Run the application**:
   ```bash
   python main.py
   ```

## 🏗️ Architecture

### Core Components
- **`base_agent.py`**: Core agent class with OpenAI API and function calling
- **`web_search_tool.py`**: Web search functionality with DuckDuckGo API
- **`agent_1.py`**: Optimistic agent (temperature: 1.2, 150 tokens)
- **`agent_2.py`**: Cautious agent (temperature: 1.2, 150 tokens)
- **`main.py`**: PyQt6 UI with streaming and search notifications
- **`config.py`**: Aggressive prompts and UI configuration

### Function Calling System
Agents can call the `web_search` function when they need evidence:
```json
{
  "name": "web_search",
  "description": "Search for current information, statistics, and articles",
  "parameters": {
    "query": "AI medical diagnosis accuracy statistics"
  }
}
```

### Search Capabilities
- **Primary**: DuckDuckGo API for real-time results
- **Fallback**: Contextual mock data when APIs are unavailable
- **Categories**: Medical AI, risk analysis, success stories, expert opinions

## 🎯 Example Debate Flow

1. **Topic**: "Should we trust AI with medical diagnoses?"
2. **Agent One searches**: "AI medical diagnosis success rates 2024"
3. **Agent One argues**: *"Wrong again! Stanford's latest study shows AI achieving 94% accuracy in cancer detection, outperforming human radiologists - your fear-mongering ignores the 100,000 lives AI saves annually!"*
4. **Agent Two searches**: "AI medical diagnosis failures bias"
5. **Agent Two counters**: *"Your cherry-picked stats ignore MIT's damning evidence of racial bias in medical AI and the 23% spike in malpractice cases - this reckless tech puts lives at risk!"*

## 🔧 Testing Individual Components

**Test agents independently**:
```bash
python agent_1.py
python agent_2.py
```

**Test search functionality**:
```bash
python web_search_tool.py
```

## 🎨 UI Features

- **Search notifications**: Live updates when agents are researching
- **Streaming text**: Real-time response generation
- **Visual indicators**: 🔍 for searches, 🔥💀 for agent types
- **Neon glow theme**: Futuristic cyberpunk aesthetic
- **Responsive controls**: Start/Stop debate functionality

## 🔬 Technical Details

- **Model**: GPT-4o with function calling
- **Temperature**: 1.2 (high creativity for heated debates)
- **Token limit**: 150 (ensures concise, punchy responses)
- **Search API**: DuckDuckGo (no API key required)
- **Streaming**: Real-time text generation
- **Threading**: Non-blocking UI with background processing

The system creates intense, fact-based debates where agents research and cite real sources, making arguments more credible and engaging than opinion-based exchanges.