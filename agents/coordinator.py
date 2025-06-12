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
from typing import Optional
from agents.scraper import ScraperAgent
from agents.preprocessor import PreprocessorAgent
from agents.analyzer import AnalyzerAgent
from agents.memory_manager import MemoryManagerAgent
from agents.reporter import ReporterAgent
from langgraph.graph import StateGraph, END
from copy import deepcopy

# Load all agent personas from personas.json
PERSONAS_PATH = os.path.join(os.path.dirname(__file__), 'personas.json')
with open(PERSONAS_PATH, 'r', encoding='utf-8') as f:
    _ALL_PERSONAS = json.load(f)

# Helper to get persona by agent name
def get_persona(name, default=None):
    for p in _ALL_PERSONAS:
        if p['name'] == name:
            return p['persona']
    return default

@dataclass
class MultiAnalyzerState:
    review: dict
    analyzer_outputs: list
    consensus: dict
    discussion_history: list = None
    round: int = 0

class CoordinatorAgent:
    def __init__(self, config=None, use_langgraph: Optional[bool] = True, max_rounds: int = 3):
        if config is None:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
            with open(config_path, 'r') as f:
                config = json.load(f)
        self.config = config or {}
        self.use_langgraph = use_langgraph
        self.scraper = ScraperAgent(persona=get_persona("ScraperAgent"))
        self.preprocessor = PreprocessorAgent(use_llm=False, config=self.config, persona=get_persona("PreprocessorAgent"))
        analyzer_names = [
            "Product Quality Specialist",
            "Customer Service and Delivery Specialist",
            "Style and User Experience Specialist"
        ]
        analyzer_personas = [get_persona(name) for name in analyzer_names]
        self.analyzers = [AnalyzerAgent(config=self.config, persona=analyzer_personas[i]) for i in range(len(analyzer_personas))]
        self.memory = MemoryManagerAgent(persona=get_persona("MemoryManagerAgent"))
        self.reporter = ReporterAgent(config=self.config, persona=get_persona("ReporterAgent"))
        self.max_rounds = max_rounds
        self.graph = self._build_langgraph()

    def _build_langgraph(self):
        g = StateGraph(MultiAnalyzerState)

        def analyze_step(state: MultiAnalyzerState):
            review = state.review
            print(f"\n[Coordinator] Analyzing review: {review.get('text', review)}")
            outputs = []
            for analyzer in self.analyzers:
                print(f"[Coordinator] Calling {analyzer.persona.split('.')[0]}...")
                try:
                    result = analyzer.analyze([review])[0]
                    print(f"[Coordinator] {analyzer.persona.split('.')[0]} output: {result}")
                except Exception as e:
                    result = {"sentiment": "Unknown", "emotions": [], "facets": [], "facet_emotions": {}, "explanation": f"Error: {str(e)}"}
                    print(f"[Coordinator] {analyzer.persona.split('.')[0]} error: {e}")
                outputs.append(result)
            return MultiAnalyzerState(
                review=review,
                analyzer_outputs=outputs,
                consensus={},
                discussion_history=[],
                round=0
            )

        def discussion_step(state: MultiAnalyzerState):
            print(f"\n[Coordinator] Discussion round {state.round+1}")
            discussion_history = deepcopy(state.discussion_history) or []
            new_outputs = []
            for idx, analyzer in enumerate(self.analyzers):
                persona = analyzer.persona
                prev_output = state.analyzer_outputs[idx]
                prompt_context = {
                    "review": state.review,
                    "all_outputs": state.analyzer_outputs,
                    "discussion_history": discussion_history,
                    "round": state.round,
                    "persona": persona
                }
                try:
                    revised = analyzer.analyze([state.review])[0]
                    comment = f"[{persona.split('.')[0]}] Round {state.round+1}: My perspective remains: {revised['sentiment']}."
                except Exception as e:
                    revised = prev_output
                    comment = f"[{persona.split('.')[0]}] Round {state.round+1}: Error in analysis."
                print(f"[Coordinator] {persona.split('.')[0]} says: {comment}")
                discussion_history.append({
                    "agent": persona,
                    "round": state.round+1,
                    "output": revised,
                    "comment": comment
                })
                new_outputs.append(revised)
            print("[Coordinator] Discussion history so far:")
            for msg in discussion_history[-len(self.analyzers):]:
                print(f"  {msg['agent'].split('.')[0]}: {msg['comment']}")
            return MultiAnalyzerState(
                review=state.review,
                analyzer_outputs=new_outputs,
                consensus=state.consensus,
                discussion_history=discussion_history,
                round=state.round+1
            )

        def consensus_step(state: MultiAnalyzerState):
            print(f"\n[Coordinator] Consensus step after {state.round} rounds.")
            sentiments = [o.get("sentiment", "Unknown") for o in state.analyzer_outputs]
            from collections import Counter
            sentiment_counts = Counter(sentiments)
            majority = sentiment_counts.most_common(1)[0][0]
            all_emotions = sum([o.get("emotions", []) for o in state.analyzer_outputs], [])
            all_facets = sum([o.get("facets", []) for o in state.analyzer_outputs], [])
            merged_facet_emotions = {}
            for o in state.analyzer_outputs:
                fe = o.get("facet_emotions", {})
                for facet, emotions in fe.items():
                    if facet not in merged_facet_emotions:
                        merged_facet_emotions[facet] = set()
                    merged_facet_emotions[facet].update(emotions)
            merged_facet_emotions = {k: list(v) for k, v in merged_facet_emotions.items()}
            consensus = {
                "sentiment": majority,
                "emotions": list(set(all_emotions)),
                "topics": list(set(all_facets)),
                "facets": list(set(all_facets)),
                "topic_emotions": merged_facet_emotions,
                "facet_emotions": merged_facet_emotions,
                "explanation": f"Majority sentiment: {majority}. Votes: {dict(sentiment_counts)}",
                "analyzer_outputs": state.analyzer_outputs,
                "discussion_history": state.discussion_history
            }
            print(f"[Coordinator] Consensus: {consensus['sentiment']} (votes: {dict(sentiment_counts)})")
            return MultiAnalyzerState(
                review=state.review,
                analyzer_outputs=state.analyzer_outputs,
                consensus=consensus,
                discussion_history=state.discussion_history,
                round=state.round
            )

        g.add_node("analyze", analyze_step)
        g.add_node("discussion", discussion_step)
        g.add_node("consensus_step", consensus_step)
        g.add_edge("analyze", "discussion")
        # Loop: discussion -> discussion (if not consensus or max rounds), else -> consensus_step
        def discussion_or_consensus(state: MultiAnalyzerState):
            sentiments = [o.get("sentiment", "Unknown") for o in state.analyzer_outputs]
            if len(set(sentiments)) == 1 or state.round >= self.max_rounds:
                return "consensus_step"
            return "discussion"
        g.add_conditional_edges("discussion", discussion_or_consensus)
        g.set_entry_point("analyze")
        return g.compile()

    def run_workflow(self, product_id=None, reviews=None):
        if reviews is not None:
            if isinstance(reviews, str):
                reviews = [reviews]
            if isinstance(reviews, list) and all(isinstance(r, str) for r in reviews):
                self.scraper.set_reviews(reviews)
            elif isinstance(reviews, list) and all(isinstance(r, dict) for r in reviews):
                self.scraper.set_reviews(reviews)
        reviews = self.scraper.get_reviews(product_id)
        cleaned = self.preprocessor.clean(reviews)
        analyzed = []
        for review in cleaned:
            state = MultiAnalyzerState(review=review, analyzer_outputs=[], consensus={}, discussion_history=[], round=0)
            result = self.graph.invoke(state)
            analyzed.append({**review, **result["consensus"]})
        self.memory.store(analyzed)
        report = self.reporter.report(analyzed)
        return report
