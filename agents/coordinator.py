# TODOs based on system_idea.txt
# - Implement advanced agent communication framework (message protocol, broker, protocol handlers)
# - Add collaborative decision-making: agent voting/consensus for ambiguous reviews
# - Integrate semantic memory with vector DB (Qdrant) and OpenAI embeddings
# - Enable proactive information sharing and broadcasting between agents
# - Implement conflict resolution protocols for agent disagreements
# - Add continuous learning: memory consolidation and improvement over time
# - Support Net Promoter Score (NPS) for business-oriented customer categorization
# - Enhance visualization with Matplotlib/Seaborn in ReporterAgent
# - Expand business value: emotion pattern detection, topic/trend discovery
# - Modularize agents for independent and collaborative workflows

# agents/coordinator.py
import json
import os
from dataclasses import dataclass
from agents.scraper import ScraperAgent
from agents.preprocessor import PreprocessorAgent
from agents.analyzer import AnalyzerAgent
from agents.memory_manager import MemoryManagerAgent
from agents.reporter import ReporterAgent
from langgraph.graph import StateGraph, END

@dataclass
class MultiAnalyzerState:
    review: dict
    analyzer_outputs: list
    consensus: dict

class CoordinatorAgent:
    def __init__(self, config=None):
        if config is None:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
            with open(config_path, 'r') as f:
                config = json.load(f)
        self.config = config or {}
        self.scraper = ScraperAgent()
        self.preprocessor = PreprocessorAgent(use_llm=False, config=self.config)
        # Instantiate 3 AnalyzerAgents for voting/consensus
        self.analyzers = [AnalyzerAgent(config=self.config) for _ in range(3)]
        self.memory = MemoryManagerAgent()
        self.reporter = ReporterAgent()
        self.graph = self._build_langgraph()

    def _build_langgraph(self):
        g = StateGraph(MultiAnalyzerState)
        def analyze_step(state: MultiAnalyzerState):
            review = state.review
            outputs = []
            for analyzer in self.analyzers:
                try:
                    result = analyzer.analyze([review])[0]
                except Exception:
                    result = {"sentiment": "Unknown", "emotions": [], "topics": [], "explanation": "Error"}
                outputs.append(result)
            return MultiAnalyzerState(review=review, analyzer_outputs=outputs, consensus={})
        def consensus_step(state: MultiAnalyzerState):
            # Voting/consensus logic
            sentiments = [o.get("sentiment", "Unknown") for o in state.analyzer_outputs]
            from collections import Counter
            sentiment_counts = Counter(sentiments)
            majority = sentiment_counts.most_common(1)[0][0]
            # Merge all emotions/topics
            all_emotions = sum([o.get("emotions", []) for o in state.analyzer_outputs], [])
            all_topics = sum([o.get("topics", []) for o in state.analyzer_outputs], [])
            consensus = {
                "sentiment": majority,
                "emotions": list(set(all_emotions)),
                "topics": list(set(all_topics)),
                "explanation": f"Majority sentiment: {majority}. Votes: {dict(sentiment_counts)}"
            }
            return MultiAnalyzerState(review=state.review, analyzer_outputs=state.analyzer_outputs, consensus=consensus)
        g.add_node("analyze", analyze_step)
        g.add_node("consensus_step", consensus_step)
        g.add_edge("analyze", "consensus_step")
        g.add_edge("consensus_step", END)
        g.set_entry_point("analyze")
        return g.compile()

    def run_workflow(self, product_id=None):
        reviews = self.scraper.get_reviews(product_id)
        cleaned = self.preprocessor.clean(reviews)
        analyzed = []
        for review in cleaned:
            # Use LangGraph to orchestrate multi-analyzer voting/consensus
            state = MultiAnalyzerState(review=review, analyzer_outputs=[], consensus={})
            result = self.graph.invoke(state)
            analyzed.append({**review, **result["consensus"]})
        self.memory.store(analyzed)  # Placeholder for semantic memory
        report = self.reporter.report(analyzed)
        return report
