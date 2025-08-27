# Course Data Pipeline Documentation

## Overview

The course data pipeline ensures consistent, high-quality course recommendations by automating the entire data processing workflow from scraping to cleanup.

## Pipeline Components

### 1. **Course Scraping** (Optional)
- Scrapes courses from multiple platforms (Coursera, Udemy, edX)
- Supports 42 topics across 8 domains
- Configurable platform and topic filtering

### 2. **Course Consolidation**
- Deduplicates courses across platforms
- Matches course descriptions to ESCO skills taxonomy
- Creates unified course catalog

### 3. **Automatic Cleanup** 
- Removes duplicate skills within courses
- Filters false positive skill matches
- Improves recommendation quality

### 4. **Quality Validation**
- Validates dataset completeness
- Reports domain coverage and statistics
- Updates metadata with quality metrics

## Usage

### Quick Start (Recommended)
```bash
# Use existing scraped data, run consolidation + cleanup
./pipeline.sh

# Scrape new data, then process everything
./pipeline.sh --scrape
```

### Advanced Usage
```bash
# Scrape specific topic
./pipeline.sh --scrape-topic "machine learning"

# Scrape specific platform
./pipeline.sh --scrape-platform coursera

# Just validate existing data
./pipeline.sh --validate-only
```

### Python Interface
```bash
# Full pipeline with existing data
pipenv run python scripts/pipeline_orchestrator.py

# Full pipeline with new scraping
pipenv run python scripts/pipeline_orchestrator.py --scrape

# Scrape specific topics
pipenv run python scripts/pipeline_orchestrator.py --scrape --topic "data science" --topic "ai"

# Manual consolidation (with auto-cleanup)
pipenv run python scripts/consolidate_courses.py

# Manual consolidation (skip cleanup)
pipenv run python scripts/consolidate_courses.py --no-cleanup

# Manual cleanup only
pipenv run python scripts/clean_course_catalog.py
```

## Pipeline Guarantees

✅ **Consistency**: Same process every time  
✅ **Quality**: Automatic cleanup never forgotten  
✅ **Validation**: Quality metrics and error detection  
✅ **Flexibility**: Can run full pipeline or individual steps  
✅ **Safety**: Backup files and error handling  

## Output

The pipeline produces:
- **`data/course_catalog_esco.json`**: Clean, deduplicated course catalog with ESCO skills
- **Quality metrics**: Domain coverage, skill counts, validation results
- **Metadata**: Processing timestamps and pipeline statistics

## Troubleshooting

### Prerequisites Missing
```bash
# ESCO vectorstore not found
pipenv run python scripts/load_esco.py

# No scraped data
./pipeline.sh --scrape
```

### Quality Issues
- **Courses without skills**: Check ESCO matching thresholds
- **False positives**: Update `FALSE_POSITIVE_PATTERNS` in cleanup script
- **Low domain coverage**: Add more diverse scraping topics

## Configuration

### Scraping Topics (config/scraping_config.yaml)
- 42 topics across 8 domains
- Platform-specific course counts
- Configurable delays and processing options

### Cleanup Filters (scripts/clean_course_catalog.py)
- False positive patterns
- Topic-specific skill filters
- Quality thresholds

This automated pipeline ensures you never forget the cleanup step and maintains consistent, high-quality course recommendations! 🚀
