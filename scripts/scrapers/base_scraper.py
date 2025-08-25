"""
Base scraper interface for course platforms
"""

from abc import ABC, abstractmethod
from typing import List, Dict
import time
import random


class BaseScraper(ABC):
    """Abstract base class for all course scrapers"""
    
    def __init__(self):
        self.delay_range = (1, 3)  # Random delay between requests (seconds)
    
    @abstractmethod
    def search_courses(self, topic: str, count: int) -> List[Dict]:
        """
        Search for courses on the platform
        
        Args:
            topic: Search topic/keyword
            count: Maximum number of courses to return
            
        Returns:
            List of course dictionaries with standardized fields
        """
        pass
    
    @abstractmethod
    def extract_course_data(self, course_element) -> Dict:
        """
        Extract course data from a single course element/page
        
        Args:
            course_element: Platform-specific course element/data
            
        Returns:
            Dictionary with course metadata
        """
        pass
    
    def sleep_between_requests(self):
        """Add random delay to avoid rate limiting"""
        delay = random.uniform(*self.delay_range)
        time.sleep(delay)
    
    def standardize_course_data(self, raw_data: Dict) -> Dict:
        """
        Standardize course data to common format
        
        Args:
            raw_data: Platform-specific course data
            
        Returns:
            Standardized course dictionary
        """
        return {
            'title': raw_data.get('title', ''),
            'provider': raw_data.get('provider', ''),
            'url': raw_data.get('url', ''),
            'description': raw_data.get('description', ''),
            'duration_hours': self._parse_duration(raw_data.get('duration', '')),
            'level': self._standardize_level(raw_data.get('level', '')),
            'format': self._standardize_format(raw_data.get('format', '')),
            'price': self._parse_price(raw_data.get('price', '')),
            'rating': raw_data.get('rating', None),
            'enrollment_count': raw_data.get('enrollment_count', None),
            'language': raw_data.get('language', 'en'),
            'certificate': raw_data.get('certificate', False),
            'instructor': raw_data.get('instructor', ''),
            'skills': raw_data.get('skills', []),  # Will be populated later with ESCO mapping
        }
    
    def _parse_duration(self, duration_str: str) -> int:
        """Parse duration string to hours (basic implementation)"""
        if not duration_str:
            return 0
        
        # Handle common patterns
        duration_str = duration_str.lower()
        
        if 'hour' in duration_str:
            # Extract number before 'hour'
            import re
            match = re.search(r'(\d+(?:\.\d+)?)\s*hours?', duration_str)
            if match:
                return int(float(match.group(1)))
        
        if 'week' in duration_str:
            # Assume 2-3 hours per week on average
            import re
            match = re.search(r'(\d+)\s*weeks?', duration_str)
            if match:
                return int(match.group(1)) * 3
        
        return 0
    
    def _standardize_level(self, level_str: str) -> str:
        """Standardize course level"""
        if not level_str:
            return 'unknown'
        
        level_str = level_str.lower()
        
        if any(word in level_str for word in ['beginner', 'intro', 'basic', 'entry']):
            return 'beginner'
        elif any(word in level_str for word in ['intermediate', 'medium']):
            return 'intermediate'
        elif any(word in level_str for word in ['advanced', 'expert', 'professional']):
            return 'advanced'
        else:
            return 'unknown'
    
    def _standardize_format(self, format_str: str) -> str:
        """Standardize course format"""
        if not format_str:
            return 'online'
        
        format_str = format_str.lower()
        
        if any(word in format_str for word in ['self-paced', 'self paced', 'on-demand']):
            return 'self-paced'
        elif any(word in format_str for word in ['instructor-led', 'live', 'scheduled']):
            return 'instructor-led'
        else:
            return 'online'
    
    def _parse_price(self, price_str: str) -> float:
        """Parse price string to float"""
        if not price_str:
            return 0.0
        
        # Remove currency symbols and extract number
        import re
        match = re.search(r'([\d,]+(?:\.\d{2})?)', str(price_str).replace(',', ''))
        if match:
            return float(match.group(1))
        
        # Check for "free"
        if 'free' in str(price_str).lower():
            return 0.0
        
        return 0.0
