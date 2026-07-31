try:
    from .gemini_ingestion import GeminiIngestionService
    from .odds_api_ingestion import OddsApiService
    from .oddsportal_ingestion import OddsPortalIngestionService
    from .api_football_ingestion import ApiFootballIngestionService
    from .exporter import ReportExporter
    from .email_service import EmailService
    from .colab_generator import ColabNotebookGenerator
except (ImportError, KeyError, Exception):
    from services.gemini_ingestion import GeminiIngestionService
    from services.odds_api_ingestion import OddsApiService
    from services.oddsportal_ingestion import OddsPortalIngestionService
    from services.api_football_ingestion import ApiFootballIngestionService
    from services.exporter import ReportExporter
    from services.email_service import EmailService
    from services.colab_generator import ColabNotebookGenerator

__all__ = [
    "GeminiIngestionService",
    "OddsApiService",
    "OddsPortalIngestionService",
    "ApiFootballIngestionService",
    "ReportExporter",
    "EmailService",
    "ColabNotebookGenerator"
]



