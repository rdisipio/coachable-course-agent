#!/bin/bash
# Course Pipeline Management Script
# 
# Usage examples:
#   ./pipeline.sh                    # Use existing data, run consolidation + cleanup
#   ./pipeline.sh --scrape           # Scrape new data, then consolidate + cleanup  
#   ./pipeline.sh --scrape-topic machine-learning
#   ./pipeline.sh --scrape-platform coursera
#   ./pipeline.sh --validate-only    # Just run quality validation

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏗️  Course Data Pipeline${NC}"
echo "=================================="

# Check if in correct directory
if [ ! -f "app.py" ] || [ ! -d "scripts" ]; then
    echo -e "${RED}❌ Please run from the coachable-course-agent root directory${NC}"
    exit 1
fi

# Check prerequisites  
if [ ! -d "data/esco_chroma" ]; then
    echo -e "${RED}❌ ESCO vectorstore not found. Please run: python scripts/load_esco.py${NC}"
    exit 1
fi

# Activate pipenv
echo -e "${BLUE}🔧 Activating pipenv environment...${NC}"
if ! command -v pipenv &> /dev/null; then
    echo -e "${RED}❌ pipenv not found. Please install pipenv first.${NC}"
    exit 1
fi

# Parse arguments and run pipeline
if [ "$1" = "--validate-only" ]; then
    echo -e "${YELLOW}🔍 Running quality validation only...${NC}"
    pipenv run python scripts/pipeline_orchestrator.py
elif [ "$1" = "--scrape" ]; then
    shift  # Remove --scrape from args
    echo -e "${YELLOW}🚀 Running full pipeline with new scraping...${NC}"
    pipenv run python scripts/pipeline_orchestrator.py --scrape "$@"
elif [ "$1" = "--scrape-topic" ]; then
    if [ -z "$2" ]; then
        echo -e "${RED}❌ Please specify a topic after --scrape-topic${NC}"
        exit 1
    fi
    echo -e "${YELLOW}🎯 Scraping topic: $2${NC}"
    pipenv run python scripts/pipeline_orchestrator.py --scrape --topic "$2"
elif [ "$1" = "--scrape-platform" ]; then
    if [ -z "$2" ]; then
        echo -e "${RED}❌ Please specify a platform after --scrape-platform${NC}"
        exit 1
    fi
    echo -e "${YELLOW}🌐 Scraping platform: $2${NC}"
    pipenv run python scripts/pipeline_orchestrator.py --scrape --platform "$2"
elif [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Course Data Pipeline Management"
    echo ""
    echo "Usage:"
    echo "  ./pipeline.sh                           # Use existing data, consolidate + cleanup"
    echo "  ./pipeline.sh --scrape                  # Scrape all configured topics"
    echo "  ./pipeline.sh --scrape-topic TOPIC      # Scrape specific topic"  
    echo "  ./pipeline.sh --scrape-platform PLATFORM # Scrape specific platform"
    echo "  ./pipeline.sh --validate-only           # Just validate existing data"
    echo "  ./pipeline.sh --help                    # Show this help"
    echo ""
    echo "Examples:"
    echo "  ./pipeline.sh --scrape-topic 'machine learning'"
    echo "  ./pipeline.sh --scrape-platform coursera"
    exit 0
else
    echo -e "${YELLOW}📊 Running pipeline with existing data...${NC}"
    pipenv run python scripts/pipeline_orchestrator.py
fi

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Pipeline completed successfully!${NC}"
    echo -e "${GREEN}📁 Output: data/course_catalog_esco.json${NC}"
else
    echo -e "${RED}❌ Pipeline failed. Check the output above for details.${NC}"
    exit 1
fi
