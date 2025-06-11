# agents/reporter.py
import matplotlib.pyplot as plt
import os

class ReporterAgent:
    """Business Insights Reporter: Summarizes sentiment analysis and generates visual insights and recommendations for stakeholders."""
    def report(self, analyzed_reviews):
        summary = {"positive": 0, "neutral": 0, "negative": 0}
        emotion_counts = {}
        topic_counts = {}
        for r in analyzed_reviews:
            sentiment = r.get("sentiment", "neutral").lower()
            if sentiment in summary:
                summary[sentiment] += 1
            else:
                summary["neutral"] += 1  # fallback for unexpected values
            # Count emotions
            for emotion in r.get("emotions", []):
                emotion = emotion.lower()
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            # Count topics
            for topic in r.get("topics", []):
                topic = topic.lower()
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
        total = len(analyzed_reviews)
        # Calculate percentages
        sentiment_pct = {k: (v / total * 100 if total else 0) for k, v in summary.items()}
        emotion_pct = {k: (v / total * 100 if total else 0) for k, v in emotion_counts.items()}
        topic_pct = {k: (v / total * 100 if total else 0) for k, v in topic_counts.items()}
        # Generate recommendation
        recommendation = self._generate_recommendation(sentiment_pct, emotion_pct, topic_pct)
        # Generate and save chart
        chart_path = self._save_sentiment_chart(summary)
        summary_text = (
            f"Out of {total} reviews for this product: "
            f"{summary['positive']} positive ({sentiment_pct['positive']:.1f}%), "
            f"{summary['neutral']} neutral ({sentiment_pct['neutral']:.1f}%), "
            f"{summary['negative']} negative ({sentiment_pct['negative']:.1f}%)."
        )
        return {
            "total_reviews": total,
            "summary": summary,
            "sentiment_percent": sentiment_pct,
            "emotion_percent": emotion_pct,
            "topic_percent": topic_pct,
            "summary_text": summary_text,
            "insight": summary_text,  # for backward compatibility
            "recommendation": recommendation,
            "visualization": chart_path  # path to the chart image for this product analysis
        }

    def _generate_recommendation(self, sentiment_pct, emotion_pct, topic_pct):
        # Simple rules for actionable recommendations
        recs = []
        if sentiment_pct.get("negative", 0) > 30:
            recs.append("High negative sentiment detected. Investigate top negative topics and address customer pain points urgently.")
        elif sentiment_pct.get("positive", 0) > 60:
            recs.append("Overall positive sentiment. Continue current practices and consider promoting top positive topics.")
        else:
            recs.append("Mixed sentiment. Focus on improving areas with most negative feedback and reinforce positive experiences.")
        if emotion_pct:
            top_emotion = max(emotion_pct, key=emotion_pct.get)
            recs.append(f"Most common emotion: {top_emotion.title()}.")
        if topic_pct:
            top_topic = max(topic_pct, key=topic_pct.get)
            recs.append(f"Most discussed topic: {top_topic.title()}.")
        return " ".join(recs)

    def _save_sentiment_chart(self, summary):
        labels = list(summary.keys())
        values = list(summary.values())
        fig, ax = plt.subplots()
        ax.bar(labels, values, color=["green", "gray", "red"])
        ax.set_xlabel("Sentiment")
        ax.set_ylabel("Count")
        ax.set_title("Sentiment Distribution")
        plt.tight_layout()
        chart_dir = os.path.join(os.path.dirname(__file__), "..", "charts")
        os.makedirs(chart_dir, exist_ok=True)
        chart_path = os.path.join(chart_dir, "sentiment_chart.png")
        plt.savefig(chart_path)
        plt.close(fig)
        return chart_path
