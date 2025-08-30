# Course Scraping System

This directory contains the orchestrated course scraping system that can collect course data from multiple platforms using configurable topics and counts.

## Prerequisites

- **Pipenv**: All commands use `pipenv run` to ensure proper dependency management
- **Python 3.11+**: Required for the project environment
- **Dev Dependencies**: Scraping tools require development dependencies

Install Pipenv if you haven't already: 
```bash
pip install pipenv
```

Install all dependencies (including scraping tools):
```bash
pipenv install --dev
```

> **Note**: The scraping system uses dev dependencies (`pyyaml`, `beautifulsoup4`, `requests`, `lxml`) since it's intended for content management, not end-user functionality. Production deployments only need `pipenv install` for the core recommendation system.

## Components

### 1. Individual Scraper (`course_scraper.py`)
Scrapes courses from a single platform for a specific topic.

```bash
pipenv run python scripts/course_scraper.py --topic "machine learning" --platform coursera --count 10
```

### 2. Master Orchestrator (`master_scraper.py`) 
Python script that reads YAML configuration and orchestrates multiple scraping runs.

```bash
pipenv run python scripts/master_scraper.py --dry-run
pipenv run python scripts/master_scraper.py --topic "AI" --platform coursera
```

### 3. Bash Wrapper (`scrape.sh`)
Convenient bash interface for the master scraper.

```bash
./scripts/scrape.sh --dry-run
./scripts/scrape.sh --topic "python" --platform udemy
```

### 4. Configuration (`config/scraping_config.yaml`)
YAML file that defines what to scrape, from which platforms, and how many courses.

## Quick Start

1. **Test the configuration**:
   ```bash
   ./scripts/scrape.sh --dry-run
   ```

2. **Scrape specific topics**:
   ```bash
   ./scripts/scrape.sh --topic "machine learning"
   ```

3. **Scrape from specific platform**:
   ```bash
   ./scripts/scrape.sh --platform coursera
   ```

4. **Full scraping run**:
   ```bash
   ./scripts/scrape.sh
   ```

## Configuration

Edit `config/scraping_config.yaml` to customize:

- **Topics**: What subjects to search for
- **Platforms**: Which platforms to scrape (coursera, udemy, edx)
- **Counts**: How many courses to get per topic/platform
- **LLM Processing**: Whether to enhance data with LLM
- **Delays**: Request timing between platforms

Example configuration:
```yaml
defaults:
  count: 10
  process_llm: false

topics:
  - name: "machine learning"
    platforms:
      - name: "coursera"
        count: 15
      - name: "udemy"
        count: 10
```

## Output

Scraped courses are saved to `data/scraped_courses/raw_data/` with filenames like:
- `coursera_machine_learning_20250825_201532.json`
- `udemy_python_programming_20250825_201600.json`

Each file contains:
- **Metadata**: Topic, platform, scraping timestamp, course count
- **Courses**: Array of course objects with unique IDs, titles, descriptions, URLs, etc.

## Features

✅ **Unique Course IDs**: Each course gets a UUID for deduplication  
✅ **Complete Descriptions**: No more truncated text  
✅ **Platform-Specific Files**: Clean organization by platform  
✅ **Configurable**: Easy YAML configuration  
✅ **Filtering**: Run specific topics or platforms  
✅ **Dry Run**: Test configurations without scraping  
✅ **Error Handling**: Robust error reporting and recovery  
✅ **Rate Limiting**: Configurable delays between requests  

## Supported Platforms

- **Coursera**: ✅ Working
- **Udemy**: ⚠️ Often blocked (403 Forbidden)  
- **edX**: 🔧 Needs selector updates

## Command Reference

### Individual Scraper
```bash
pipenv run python scripts/course_scraper.py --topic TOPIC --platform PLATFORM [--count N] [--process-llm]
```

### Master Scraper (Python)
```bash
pipenv run python scripts/master_scraper.py [--config FILE] [--dry-run] [--topic FILTER] [--platform FILTER]
```

### Master Scraper (Bash)
```bash
./scripts/scrape.sh [-c FILE] [-d] [-t TOPIC] [-p PLATFORM] [-h]
```

## Troubleshooting

- **403 Forbidden**: Platform is blocking requests (common with Udemy)
- **No courses found**: Check if platform selectors need updating
- **Config errors**: Validate YAML syntax and required fields
- **Module not found (pyyaml, beautifulsoup4, etc.)**: Install dev dependencies with `pipenv install --dev`

## Deployment Notes

### Production Environment
For end-user deployments (course recommendation system only):
```bash
pipenv install  # Core dependencies only
```

### Development/Content Management Environment  
For updating course database and scraping:
```bash
pipenv install --dev  # Includes scraping tools
```

The scraping system is intentionally in dev dependencies since it's for content management, not end-user functionality.
