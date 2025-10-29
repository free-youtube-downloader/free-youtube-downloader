#!/usr/bin/env python6
"""
TokLabs Video Downloader - Main Entry Point

A powerful, cross-platform video downloader application built with Python and PySide6.
Supports downloading videos and audio from various platforms with advanced features.
"""

import sys
from core.app_factory import main as app_main


def main() -> None:
    """Application entry point"""
    exit_code = app_main(sys.argv)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
