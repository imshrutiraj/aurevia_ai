import io
import base64
import json
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List

class CareerChartVisualizer:
    """
    Data Visualization Engine utilizing Plotly and Matplotlib to produce interactive
    and static visual charts reflecting genuine candidate analysis metrics.
    """

    @classmethod
    def generate_ats_gauge_plotly(cls, ats_score: float) -> str:
        """
        Generates interactive Plotly gauge chart JSON for ATS Score.
        """
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=ats_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "ATS Compatibility Score", 'font': {'size': 18, 'color': "#D6B77A"}},
            number={'suffix': "/100", 'font': {'color': "#F4F0E8"}},
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': "#A9A6B9"},
                'bar': {'color': "#D6B77A"},
                'bgcolor': "#141A2B",
                'borderwidth': 2,
                'bordercolor': "#232A42",
                'steps': [
                    {'range': [0, 50], 'color': 'rgba(235, 87, 87, 0.3)'},
                    {'range': [50, 75], 'color': 'rgba(242, 201, 76, 0.3)'},
                    {'range': [75, 100], 'color': 'rgba(39, 174, 96, 0.3)'}
                ],
                'threshold': {
                    'line': {'color': "#B8A5E8", 'width': 4},
                    'thickness': 0.75,
                    'value': 80
                }
            }
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={'color': "#F4F0E8"},
            margin=dict(l=20, r=20, t=50, b=20),
            height=260
        )
        return json.dumps(fig.to_dict())

    @classmethod
    def generate_skills_breakdown_plotly(cls, skill_counts: Dict[str, int]) -> str:
        """
        Generates interactive horizontal bar chart JSON of skills across categories.
        """
        categories = [k.replace("_", " ").title() for k in skill_counts.keys()]
        values = list(skill_counts.values())

        fig = go.Figure(go.Bar(
            x=values,
            y=categories,
            orientation='h',
            marker=dict(
                color=values,
                colorscale=[[0, '#B8A5E8'], [1, '#D6B77A']],
                line=dict(color='#D6B77A', width=1)
            )
        ))
        fig.update_layout(
            title={'text': "Identified Skills Distribution", 'font': {'size': 16, 'color': "#D6B77A"}},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={'color': "#F4F0E8"},
            xaxis=dict(title="Skills Count", gridcolor="#232A42"),
            yaxis=dict(gridcolor="#232A42", autorange="reversed"),
            margin=dict(l=20, r=20, t=40, b=20),
            height=280
        )
        return json.dumps(fig.to_dict())

    @classmethod
    def generate_role_matches_plotly(cls, predicted_roles: List[Dict[str, Any]]) -> str:
        """
        Generates interactive bar chart JSON of Top 5 predicted job role matches.
        """
        roles = [r["role"] for r in predicted_roles]
        confidences = [r["confidence_score"] for r in predicted_roles]

        fig = go.Figure(go.Bar(
            x=roles,
            y=confidences,
            text=[f"{c}%" for c in confidences],
            textposition='auto',
            marker=dict(
                color='#D6B77A',
                line=dict(color='#E9D5A5', width=1.5)
            )
        ))
        fig.update_layout(
            title={'text': "Career Role Suitability Prediction", 'font': {'size': 16, 'color': "#D6B77A"}},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={'color': "#F4F0E8"},
            xaxis=dict(gridcolor="#232A42", tickangle=-15),
            yaxis=dict(title="Suitability %", range=[0, 105], gridcolor="#232A42"),
            margin=dict(l=20, r=20, t=40, b=50),
            height=280
        )
        return json.dumps(fig.to_dict())

    @classmethod
    def generate_skill_coverage_pie_matplotlib(cls, matched_count: int, missing_count: int) -> str:
        """
        Generates base64 encoded PNG pie chart using Matplotlib for PDF report export or embedding.
        """
        plt.figure(figsize=(4.5, 3.5), facecolor="#141A2B")
        ax = plt.subplot(111)
        ax.set_facecolor("#141A2B")

        labels = ['Matched Skills', 'Skill Gaps']
        sizes = [max(matched_count, 1), max(missing_count, 0)]
        colors = ['#D6B77A', '#B8A5E8']
        explode = (0.05, 0)

        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            autopct='%1.1f%%',
            startangle=140,
            colors=colors,
            explode=explode if missing_count > 0 else (0, 0),
            textprops=dict(color="#F4F0E8")
        )
        for autotext in autotexts:
            autotext.set_color("#141A2B")
            autotext.set_weight("bold")

        plt.title("Target Role Skill Alignment", color="#D6B77A", fontsize=12, pad=10)
        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', facecolor="#141A2B", dpi=120)
        plt.close()
        buffer.seek(0)
        encoded = base64.b64encode(buffer.read()).decode('utf-8')
        return f"data:image/png;base64,{encoded}"
