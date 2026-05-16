# AI Dining Concierge

An intelligent restaurant recommendation agent built with **LangGraph**, **RAG (ChromaDB)**, and **OpenAI GPT-4** — designed as a proof-of-concept for AI-powered dining experiences.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                      │
│              (Chat UI + Preference Sidebar)                │
└─────────────────────────┬─────────────────────────────────┘
                          │
┌─────────────────────────▼─────────────────────────────────┐
│                   LangGraph Agent                          │
│            (State Machine + Tool Router)                   │
├───────────────────────────────────────────────────────────┤
│  Tools:                                                    │
│  ┌──────────────┐ ┌──────────────┐ ┌───────────────────┐ │
│  │ Semantic     │ │ Structured   │ │ Availability      │ │
│  │ Search (RAG) │ │ Filter       │ │ Checker           │ │
│  └──────────────┘ └──────────────┘ └───────────────────┘ │
│  ┌──────────────┐                                         │
│  │ Amex Rewards │                                         │
│  │ Lookup       │                                         │
│  └──────────────┘                                         │
└───────────────────────────┬───────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────┐
│                   RAG Pipeline                             │
│         ChromaDB + OpenAI Embeddings                      │
│         (50 restaurants indexed)                           │
└───────────────────────────────────────────────────────────┘
```

## Features

- **Multi-Tool Agent**: LangGraph-based agent that intelligently selects the right tool for each query
- **RAG Pipeline**: Semantic search over restaurant descriptions using ChromaDB vector store
- **Structured Filtering**: Budget, location, cuisine, dietary needs, and occasion-based filtering
- **Availability Checking**: Real-time slot availability lookup
- **Amex Benefits Integration**: Exclusive card member rewards and discounts
- **Multi-Turn Conversations**: Maintains context across conversation turns
- **Preference-Aware**: Sidebar preferences automatically enhance queries

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Agent Framework | LangChain + LangGraph |
| LLM | OpenAI GPT-4o-mini |
| Vector Database | ChromaDB (in-memory) |
| Embeddings | OpenAI text-embedding-3-small |
| Frontend | Streamlit |
| Data | 50 curated restaurants (JSON) |

## Quick Start

### Prerequisites
- Python 3.10+
- OpenAI API key

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-dining-concierge.git
cd ai-dining-concierge

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Run Locally

```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`

## Example Conversations

```
User: "Find me a romantic restaurant in Bangalore under ₹3000 for two"
Agent: [Uses semantic_search + filter] → Returns Olive Beach, The Fatty Bao...

User: "Does Olive Beach have availability at 8pm?"
Agent: [Uses check_availability] → Shows available time slots

User: "What Amex benefits do I get there?"
Agent: [Uses get_amex_benefits] → 15% off + 3x points + complimentary dessert
```

## Project Structure

```
ai-dining-concierge/
├── app.py                 # Streamlit frontend
├── agent/
│   ├── graph.py           # LangGraph agent definition
│   ├── tools.py           # 4 agent tools
│   ├── prompts.py         # System prompt
│   └── memory.py          # Chat history management
├── data/
│   ├── restaurants.json   # Restaurant dataset
│   └── load_data.py       # Data utilities
├── rag/
│   ├── vectorstore.py     # ChromaDB + retrieval
│   └── embeddings.py      # Embedding config
└── requirements.txt
```

## Deployment

Deployed on Streamlit Cloud. To deploy your own:

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo and set `app.py` as the main file
4. Add `OPENAI_API_KEY` in the Secrets section
5. Deploy!

## Key Design Decisions

1. **LangGraph over simple chain**: Enables multi-step reasoning — the agent can search, refine, and cross-reference across tools
2. **ChromaDB in-memory**: Zero infrastructure cost, sufficient for demo scale, embeddings regenerated on startup
3. **Separate semantic search + structured filter**: RAG handles vague queries ("something romantic"), structured filter handles specific criteria ("under ₹2000 in Bangalore")
4. **GPT-4o-mini**: Cost-efficient for tool-calling, fast response times while maintaining quality

## Future Enhancements

- Real-time restaurant availability via API integrations
- User preference learning from booking history
- Multi-language support (Hindi, Kannada, Marathi)
- Integration with Amex card transaction data for personalized recommendations
- Photo gallery and menu previews
- Reservation booking flow with payment

---

*Built as a portfolio project demonstrating Agentic AI, RAG pipelines, and product thinking for the hospitality tech space.*
