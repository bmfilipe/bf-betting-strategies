try:
    from .gemini_ingestion import GeminiIngestionService
    from .odds_api_ingestion import OddsApiService
    from .oddsportal_ingestion import OddsPortalIngestionService
    from .api_football_ingestion import ApiFootballIngestionService
    from .live_matches_service import LiveMatchesService
    from .h2h_scraper import H2HScraperService
    from .exporter import ReportExporter
    from .email_service import EmailService
    from .colab_generator import ColabNotebookGenerator
except (ImportError, KeyError, Exception):
    from services.gemini_ingestion import GeminiIngestionService
    from services.odds_api_ingestion import OddsApiService
    from services.oddsportal_ingestion import OddsPortalIngestionService
    from services.api_football_ingestion import ApiFootballIngestionService
    from services.live_matches_service import LiveMatchesService
    from services.h2h_scraper import H2HScraperService
    from services.exporter import ReportExporter
    from services.email_service import EmailService
    from services.colab_generator import ColabNotebookGenerator

__all__ = [
    "GeminiIngestionService",
    "OddsApiService",
    "OddsPortalIngestionService",
    "ApiFootballIngestionService",
    "LiveMatchesService",
    "H2HScraperService",
    "ReportExporter",
    "EmailService",
    "ColabNotebookGenerator"
]



