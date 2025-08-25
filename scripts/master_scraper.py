#!/usr/bin/env python3
"""
Master Course Scraping Orchestrator

This script reads configuration from scraping_config.yaml and orchestrates
multiple scraper runs across different platforms and topics.

Usage:
    pipenv run python scripts/master_scraper.py                    # Use default config
    pipenv run python scripts/master_scraper.py --config custom_config.yaml
    pipenv run python scripts/master_scraper.py --dry-run          # Show what would be scraped
    pipenv run python scripts/master_scraper.py --topic "AI"       # Scrape only specific topic
    pipenv run python scripts/master_scraper.py --platform coursera # Scrape only specific platform
"""

import argparse
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

import yaml


class MasterScraper:
    """Orchestrates course scraping across multiple platforms and topics"""
    
    def __init__(self, config_path: str = "config/scraping_config.yaml"):
        self.config_path = config_path
        self.config = self.load_config()
        self.script_dir = Path(__file__).parent
        self.scraper_script = self.script_dir / "course_scraper.py"
        self.results = {"success": [], "failed": [], "skipped": []}
        
    def load_config(self) -> Dict[str, Any]:
        """Load and validate YAML configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Validate required sections
            if 'topics' not in config:
                raise ValueError("Configuration must contain 'topics' section")
            
            return config
        except FileNotFoundError:
            print(f"❌ Configuration file not found: {self.config_path}")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"❌ Error parsing YAML configuration: {e}")
            sys.exit(1)
        except ValueError as e:
            print(f"❌ Configuration error: {e}")
            sys.exit(1)
    
    def get_python_command(self) -> List[str]:
        """Get the correct Python command using pipenv"""
        # Always use pipenv run to ensure proper dependency management
        return ["pipenv", "run", "python"]
    
    def build_scraper_command(self, topic: str, platform: str, count: int, process_llm: bool) -> List[str]:
        """Build the command to run the individual scraper"""
        python_cmd = self.get_python_command()
        
        cmd = python_cmd + [
            str(self.scraper_script),
            "--topic", topic,
            "--platform", platform,
            "--count", str(count)
        ]
        
        if process_llm:
            cmd.append("--process-llm")
            
        return cmd
    
    def run_scraper(self, topic: str, platform: str, count: int, process_llm: bool, dry_run: bool = False) -> bool:
        """Run the scraper for a specific topic/platform combination"""
        cmd = self.build_scraper_command(topic, platform, count, process_llm)
        
        print(f"🔄 Scraping '{topic}' from {platform} ({count} courses){' [LLM]' if process_llm else ''}")
        
        if dry_run:
            print(f"   Would run: {' '.join(cmd)}")
            return True
        
        try:
            # Run the scraper
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                print(f"   ✅ Success")
                self.results["success"].append({
                    "topic": topic,
                    "platform": platform,
                    "count": count,
                    "timestamp": datetime.now().isoformat()
                })
                return True
            else:
                print(f"   ❌ Failed (exit code {result.returncode})")
                print(f"   Error: {result.stderr.strip()}")
                self.results["failed"].append({
                    "topic": topic,
                    "platform": platform,
                    "error": result.stderr.strip(),
                    "timestamp": datetime.now().isoformat()
                })
                return False
                
        except subprocess.TimeoutExpired:
            print(f"   ⏱️  Timeout (5 minutes)")
            self.results["failed"].append({
                "topic": topic,
                "platform": platform,
                "error": "Timeout after 5 minutes",
                "timestamp": datetime.now().isoformat()
            })
            return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.results["failed"].append({
                "topic": topic,
                "platform": platform,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            return False
    
    def get_delay_for_platform(self, platform: str) -> float:
        """Get delay setting for a platform"""
        platform_settings = self.config.get('platform_settings', {})
        platform_config = platform_settings.get(platform, {})
        return platform_config.get('delay_between_requests', 2.0)
    
    def run_all(self, dry_run: bool = False, topic_filter: str = None, platform_filter: str = None):
        """Run scraping for all configured topics and platforms"""
        defaults = self.config.get('defaults', {})
        default_count = defaults.get('count', 10)
        default_process_llm = defaults.get('process_llm', False)
        
        total_jobs = 0
        successful_jobs = 0
        
        print(f"🚀 Starting master scraper with config: {self.config_path}")
        if dry_run:
            print("🔍 DRY RUN MODE - No actual scraping will be performed")
        print()
        
        for topic_config in self.config['topics']:
            topic_name = topic_config['name']
            
            # Apply topic filter if specified
            if topic_filter and topic_filter.lower() not in topic_name.lower():
                continue
            
            topic_process_llm = topic_config.get('process_llm', default_process_llm)
            
            print(f"📚 Topic: '{topic_name}'")
            
            for platform_config in topic_config['platforms']:
                platform_name = platform_config['name']
                
                # Apply platform filter if specified
                if platform_filter and platform_filter.lower() != platform_name.lower():
                    continue
                
                platform_count = platform_config.get('count', default_count)
                
                total_jobs += 1
                
                # Run the scraper
                success = self.run_scraper(
                    topic_name, 
                    platform_name, 
                    platform_count, 
                    topic_process_llm,
                    dry_run
                )
                
                if success:
                    successful_jobs += 1
                
                # Add delay between scraping jobs (unless dry run)
                if not dry_run and not success:
                    delay = self.get_delay_for_platform(platform_name)
                    print(f"   ⏳ Waiting {delay}s before next request...")
                    time.sleep(delay)
            
            print()  # Empty line between topics
        
        # Print summary
        print("="*60)
        print(f"📊 SCRAPING SUMMARY")
        print(f"Total jobs: {total_jobs}")
        print(f"Successful: {successful_jobs}")
        print(f"Failed: {len(self.results['failed'])}")
        print(f"Success rate: {(successful_jobs/total_jobs*100) if total_jobs > 0 else 0:.1f}%")
        
        if self.results['failed']:
            print(f"\n❌ Failed jobs:")
            for job in self.results['failed']:
                print(f"   {job['topic']} ({job['platform']}): {job['error']}")
        
        if not dry_run:
            print(f"\n💾 Scraped data saved to: data/scraped_courses/raw_data/")


def main():
    parser = argparse.ArgumentParser(description='Master course scraping orchestrator')
    parser.add_argument('--config', default='config/scraping_config.yaml',
                       help='Path to YAML configuration file')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be scraped without actually running')
    parser.add_argument('--topic', help='Only scrape courses for this topic (partial match)')
    parser.add_argument('--platform', help='Only scrape from this platform')
    
    args = parser.parse_args()
    
    # Validate that the individual scraper script exists
    script_dir = Path(__file__).parent
    scraper_script = script_dir / "course_scraper.py"
    
    if not scraper_script.exists():
        print(f"❌ Course scraper not found: {scraper_script}")
        return 1
    
    try:
        scraper = MasterScraper(args.config)
        scraper.run_all(
            dry_run=args.dry_run,
            topic_filter=args.topic,
            platform_filter=args.platform
        )
        return 0
    except KeyboardInterrupt:
        print("\n⚠️  Scraping interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
