# Multi-AI Agents for Sentiment Analysis

This project implements a modular, multi-agent system for advanced sentiment analysis of e-commerce product reviews. It leverages the LangChain and LangGraph frameworks, OpenAI LLMs, and the A2A protocol for agent-to-agent communication.

## Features

- **Scraper Agent (Data Acquisition Specialist):** Collects product reviews (mocked for demo, can be extended for Lazada API). Shows progress in terminal.
- **Preprocessor Agent (Text Data Specialist):** Cleans and normalizes review text for analysis, optionally using LLMs. Shows progress in terminal.
- **Analyzer Agents (Customer Insights Analysts):** Multiple LLM-based agents analyze each review for sentiment, emotion, and topics. Results are combined using a voting/consensus mechanism (LangGraph orchestrated). Each agent's analysis and group chat/discussion are printed in the terminal for transparency and debugging.
- **Memory Manager Agent:** Placeholder for semantic memory (Qdrant/embeddings integration planned). Shows storing progress in terminal.
- **Reporter Agent (Business Insights Reporter):** Summarizes results, generates actionable recommendations, and creates visualizations (charts). Shows progress and chart generation in terminal.
- **A2A Protocol Server:** Exposes the workflow via a FastAPI endpoint, supporting standardized agent-to-agent communication.

## Architecture

- **Workflow:**
  1. Scraper collects all reviews for a product.
  2. Preprocessor cleans each review.
  3. Each review is analyzed by multiple Analyzer agents (LLMs).
  4. Results are consolidated via voting/consensus (LangGraph). Group chat/discussion and consensus process are visible in the terminal.
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
   - **Debugging:** All agent progress, analysis, and group chat/discussion will be printed in the terminal for each review.

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
- [x] Add collaborative decision-making: agent voting/consensus for ambiguous reviews
- [x] Enhance visualization with Matplotlib/Seaborn in ReporterAgent
- [x] Modularize agents for independent and collaborative workflows
- [x] Enable proactive information sharing and broadcasting between agents (basic group chat/discussion visible in terminal)
- [x] Implement conflict resolution protocols for agent disagreements (basic consensus mechanism)
- [x] Show agent progress and group chat/discussion in terminal for debugging
- [ ] Implement advanced agent communication framework (message protocol, broker, protocol handlers)
- [ ] Integrate semantic memory with vector DB (Qdrant) and OpenAI embeddings
- [ ] Add continuous learning: memory consolidation and improvement over time
- [ ] Support Net Promoter Score (NPS) for business-oriented customer categorization
- [ ] Expand business value: emotion pattern detection, topic/trend discovery

## Credits
- Built with LangChain, LangGraph, OpenAI, FastAPI, and Matplotlib.
- Inspired by the A2A protocol and multi-agent system design patterns.

## Agent Workflow & Collaboration Mechanism

The system is built around a collaborative, multi-agent workflow for product review analysis. Here is how the agents interact:

1. **Scraper Agent**: Collects all reviews for a given product (mocked data for demo, can be extended to real APIs).
2. **Preprocessor Agent**: Cleans and normalizes each review for downstream analysis.
3. **Analyzer Agents**: Multiple LLM-based agents, each with a unique persona/focus, independently analyze each review for sentiment, emotions, facets (topics), and facet→emotions mapping.
4. **Group Chat & Consensus (LangGraph)**: If analyzer agents disagree, a group chat/discussion is orchestrated (visible in terminal). Agents can comment, challenge, and revise their outputs. After several rounds, a consensus is reached via voting or majority.
5. **Memory Manager Agent**: Stores the results for future reference and enables learning across analyses (semantic memory integration planned).
6. **Reporter Agent**: Aggregates all results, calculates statistics (percentages, trends), generates a summary and actionable recommendations using an LLM, and creates a sentiment chart (PNG).
7. **A2A Protocol Server**: Exposes the entire workflow as a FastAPI endpoint, following the A2A protocol for agent-to-agent communication. The endpoint can be called with a batch of reviews or a product ID.

**Key Mechanisms:**
- Each agent prints its progress and actions in the terminal for transparency and debugging.
- The group chat/discussion and consensus process are visible in the terminal, showing how agents communicate and resolve disagreements.
- The workflow is modular: each agent can be extended or replaced independently.
- The system is designed for extensibility (e.g., adding new agent types, integrating semantic memory, or supporting new communication protocols).
