try:
    from .styles import apply_custom_styles
    from .tab_ingestion import render_tab_ingestion
    from .tab_analysis import render_tab_analysis
    from .tab_slips import render_tab_slips
    from .tab_admin import render_tab_admin
except (ImportError, KeyError, Exception):
    from ui.styles import apply_custom_styles
    from ui.tab_ingestion import render_tab_ingestion
    from ui.tab_analysis import render_tab_analysis
    from ui.tab_slips import render_tab_slips
    from ui.tab_admin import render_tab_admin

__all__ = [
    "apply_custom_styles",
    "render_tab_ingestion",
    "render_tab_analysis",
    "render_tab_slips",
    "render_tab_admin"
]


