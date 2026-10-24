"""Shared dark styling for notebook and exported Plotly charts."""


def dark_theme(figure):
    """Style both Plotly Express figures and vectorbt figures in place."""
    figure.update_layout(
        template="plotly_dark",
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font_color="#e5e7eb",
        legend=dict(bgcolor="#111827", font_color="#e5e7eb"),
    )
    figure.update_xaxes(gridcolor="#374151", zerolinecolor="#4b5563")
    figure.update_yaxes(gridcolor="#374151", zerolinecolor="#4b5563")
    return figure
