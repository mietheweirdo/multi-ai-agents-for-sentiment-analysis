# Multi-AI Agents for Sentiment Analysis

This project implements a modular, multi-agent system for advanced sentiment analysis of e-commerce product reviews. It leverages the LangChain and LangGraph frameworks, OpenAI LLMs, and the A2A protocol for agent-to-agent communication.

## Features

- **Scraper Agent (Data Acquisition Specialist):** Collects product reviews (mocked for demo, can be extended for Shopee API).
- **Preprocessor Agent (Text Data Specialist):** Cleans and normalizes review text for analysis, optionally using LLMs.
- **Analyzer Agents (Customer Insights Analysts):** Multiple LLM-based agents analyze each review for sentiment, emotion, and topics. Results are combined using a voting/consensus mechanism (LangGraph orchestrated).
- **Memory Manager Agent:** Placeholder for semantic memory (Qdrant/embeddings integration planned).
- **Reporter Agent (Business Insights Reporter):** Summarizes results, generates actionable recommendations, and creates visualizations (charts).
- **A2A Protocol Server:** Exposes the workflow via a FastAPI endpoint, supporting standardized agent-to-agent communication.

## Architecture

- **Workflow:**
  1. Scraper collects all reviews for a product.
  2. Preprocessor cleans each review.
  3. Each review is analyzed by multiple Analyzer agents (LLMs).
  4. Results are consolidated via voting/consensus (LangGraph).
  5. Reporter aggregates, summarizes, and visualizes the overall product sentiment.

- **Visualization:**
  - Generates a sentiment distribution chart for each product (saved as PNG in `charts/`).
  - Chart can be served via an API endpoint.

## How to Run

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Configure OpenAI API Key:**
   - Edit `config.json` with your OpenAI API key and model name.

3. **Start the A2A server:**
   ```bash
   uvicorn a2a_server:app --reload
   ```

4. **Test the workflow:**
   - Run the test script:
     ```bash
     python test_a2a_workflow.py
     ```
   - Or send a POST request to `http://127.0.0.1:8000/tasks/send` with a review or product ID.

5. **View the chart:**
   - The sentiment chart is saved in the `charts/` directory (e.g., `charts/sentiment_chart.png`).
   - (Optional) Access the chart via an API endpoint (see `a2a_server.py`).

## Project Structure

- `agents/` - All agent implementations (scraper, preprocessor, analyzer, memory manager, reporter)
- `a2a_server.py` - FastAPI server exposing the workflow via A2A protocol
- `test_a2a_workflow.py` - Test script for sending sample reviews
- `charts/` - Output directory for generated sentiment charts
- `config.json` - Configuration for API keys and model

## TODO (from system_idea.txt)
- Implement advanced agent communication framework (message protocol, broker, protocol handlers)
- Add collaborative decision-making: agent voting/consensus for ambiguous reviews
- Integrate semantic memory with vector DB (Qdrant) and OpenAI embeddings
- Enable proactive information sharing and broadcasting between agents
- Implement conflict resolution protocols for agent disagreements
- Add continuous learning: memory consolidation and improvement over time
- Support Net Promoter Score (NPS) for business-oriented customer categorization
- Enhance visualization with Matplotlib/Seaborn in ReporterAgent
- Expand business value: emotion pattern detection, topic/trend discovery
- Modularize agents for independent and collaborative workflows

## Credits
- Built with LangChain, LangGraph, OpenAI, FastAPI, and Matplotlib.
- Inspired by the A2A protocol and multi-agent system design patterns.
