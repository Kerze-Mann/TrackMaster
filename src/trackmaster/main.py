#!/usr/bin/env python3
"""
Main entry point for TrackMaster server.
"""

import uvicorn
from trackmaster.api import create_app
from trackmaster.config import settings
from trackmaster.utils import setup_logging


def main():
    """Start the TrackMaster server."""
    # Setup logging
    setup_logging(settings.LOG_LEVEL)
    
    # Create the FastAPI app
    app = create_app()
    
    # Run the server
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower()
    )


if __name__ == "__main__":
    main()
