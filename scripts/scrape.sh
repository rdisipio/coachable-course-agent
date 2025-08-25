#!/bin/bash

# Master Course Scraper - Bash Wrapper
# This is a convenience wrapper around the Python master scraper

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Default values
CONFIG_FILE="$PROJECT_ROOT/config/scraping_config.yaml"
DRY_RUN=false
TOPIC=""
PLATFORM=""

# Function to show usage
show_usage() {
    echo -e "${BLUE}Master Course Scraper${NC}"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -c, --config FILE     Use custom configuration file (default: config/scraping_config.yaml)"
    echo "  -d, --dry-run         Show what would be scraped without actually running"
    echo "  -t, --topic TOPIC     Only scrape courses for this topic (partial match)"
    echo "  -p, --platform PLATFORM  Only scrape from this platform (coursera, udemy, edx)"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Scrape everything in config"
    echo "  $0 --dry-run                         # Show what would be scraped"
    echo "  $0 --topic \"machine learning\"        # Only scrape ML courses"
    echo "  $0 --platform coursera               # Only scrape from Coursera"
    echo "  $0 --topic python --platform udemy   # Only Python courses from Udemy"
    echo ""
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -t|--topic)
            TOPIC="$2"
            shift 2
            ;;
        -p|--platform)
            PLATFORM="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo -e "${RED}Error: Unknown option $1${NC}"
            show_usage
            exit 1
            ;;
    esac
done

# Check if config file exists
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo -e "${RED}Error: Configuration file not found: $CONFIG_FILE${NC}"
    exit 1
fi

# Find Python executable using pipenv
if ! command -v pipenv &> /dev/null; then
    echo -e "${RED}Error: pipenv not found. Please install pipenv first.${NC}"
    echo "Install with: pip install pipenv"
    exit 1
fi

# Build the command using pipenv run
CMD=("pipenv" "run" "python" "$SCRIPT_DIR/master_scraper.py" "--config" "$CONFIG_FILE")

if [[ "$DRY_RUN" == true ]]; then
    CMD+=("--dry-run")
fi

if [[ -n "$TOPIC" ]]; then
    CMD+=("--topic" "$TOPIC")
fi

if [[ -n "$PLATFORM" ]]; then
    CMD+=("--platform" "$PLATFORM")
fi

# Show what we're about to run
echo -e "${BLUE}Running master scraper...${NC}"
echo -e "${YELLOW}Config:${NC} $CONFIG_FILE"
if [[ "$DRY_RUN" == true ]]; then
    echo -e "${YELLOW}Mode:${NC} DRY RUN"
fi
if [[ -n "$TOPIC" ]]; then
    echo -e "${YELLOW}Topic filter:${NC} $TOPIC"
fi
if [[ -n "$PLATFORM" ]]; then
    echo -e "${YELLOW}Platform filter:${NC} $PLATFORM"
fi
echo ""

# Change to project directory
cd "$PROJECT_ROOT"

# Run the command
if "${CMD[@]}"; then
    echo -e "${GREEN}✅ Master scraper completed successfully${NC}"
else
    echo -e "${RED}❌ Master scraper failed${NC}"
    exit 1
fi
