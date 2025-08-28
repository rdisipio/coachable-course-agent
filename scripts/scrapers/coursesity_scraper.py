"""
Coursesity scraper implementation - Course aggregator platform
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import time
import random
import re
from urllib.parse import urljoin, quote_plus
from .base_scraper import BaseScraper


class CoursesityScraper(BaseScraper):
    """Scraper for Coursesity course aggregator"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://coursesity.com"
        
        # Headers to appear like a regular browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
        # Initialize session for better state management
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.delay_range = (2, 4)  # Moderate delays
    
    def search_courses(self, topic: str, count: int) -> List[Dict]:
        """Search for courses on Coursesity using topic-based URLs"""
        courses = []
        
        try:
            # Add random delay to avoid detection
            time.sleep(random.uniform(*self.delay_range))
            
            # Try different search approaches for the topic
            search_urls = self._build_search_urls(topic)
            
            print(f"  Searching Coursesity for '{topic}'...")
            
            for search_url in search_urls:
                try:
                    print(f"    Trying URL: {search_url}")
                    
                    response = self.session.get(
                        search_url,
                        timeout=(10, 30),
                        allow_redirects=True
                    )
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        page_courses = self._extract_courses_from_page(soup, topic, count - len(courses))
                        courses.extend(page_courses)
                        
                        if len(courses) >= count:
                            break
                            
                        # Small delay between pages
                        time.sleep(random.uniform(1, 2))
                    else:
                        print(f"      Status code: {response.status_code}")
                        
                except Exception as e:
                    print(f"    Error with URL {search_url}: {e}")
                    continue
                    
        except Exception as e:
            print(f"    Unexpected error: {e}")
            
        return courses[:count]
    
    def _build_search_urls(self, topic: str) -> List[str]:
        """Build search URLs for the given topic"""
        urls = []
        
        # Clean topic for URL
        clean_topic = topic.lower().replace(' ', '-').replace('_', '-')
        
        # Primary topic-based search
        topic_url = f"{self.base_url}/free-tutorials-learn/{clean_topic}"
        urls.append(topic_url)
        
        # Try variations for common topics
        topic_variations = {
            'machine-learning': ['machine-learning', 'ml', 'artificial-intelligence'],
            'data-science': ['data-science', 'data-analysis', 'statistics'],
            'web-development': ['web-development', 'html', 'css', 'javascript'],
            'python': ['python', 'programming'],
            'javascript': ['javascript', 'js', 'web-development'],
            'react': ['react-js', 'react', 'frontend'],
            'artificial-intelligence': ['artificial-intelligence', 'ai', 'machine-learning'],
            'cyber-security': ['cybersecurity', 'security', 'ethical-hacking'],
            'blockchain': ['blockchain', 'cryptocurrency', 'bitcoin']
        }
        
        if clean_topic in topic_variations:
            for variation in topic_variations[clean_topic]:
                if variation != clean_topic:
                    urls.append(f"{self.base_url}/free-tutorials-learn/{variation}")
        
        # Try section-based search for broader categories
        section_mappings = {
            'programming': 'development',
            'coding': 'development',
            'design': 'design',
            'marketing': 'marketing',
            'business': 'business'
        }
        
        for keyword, section in section_mappings.items():
            if keyword in topic.lower():
                urls.append(f"{self.base_url}/section/{section}")
                break
        
        return urls
    
    def _extract_courses_from_page(self, soup: BeautifulSoup, topic: str, max_courses: int) -> List[Dict]:
        """Extract course information from a Coursesity page"""
        courses = []
        
        # Look for JSON data in script tags
        script_tags = soup.find_all('script', id='app-root-state')
        
        if script_tags:
            try:
                import json
                json_text = script_tags[0].get_text()
                data = json.loads(json_text)
                
                # Extract course data from JSON
                course_list = data.get('COURSE_LIST', {}).get('courseData', [])
                print(f"    Found {len(course_list)} courses in JSON data")
                
                for course_json in course_list[:max_courses]:
                    course_data = self._extract_course_from_json(course_json, topic)
                    if course_data:
                        courses.append(course_data)
                        print(f"      Extracted: {course_data.get('title', 'No title')}")
                
                return courses
                
            except Exception as e:
                print(f"    Error parsing JSON data: {e}")
        
        # Fallback to HTML parsing if JSON not found
        print("    JSON not found, falling back to HTML parsing")
        
        # Look for course links as fallback
        course_links = soup.find_all('a', href=lambda x: x and '/course-detail/' in x)
        if course_links:
            print(f"    Found {len(course_links)} course links as fallback")
            for link in course_links[:max_courses]:
                course_data = self._extract_course_from_link(link, topic)
                if course_data:
                    courses.append(course_data)
                    print(f"      Extracted: {course_data.get('title', 'No title')}")
        else:
            print(f"    No course elements or links found on page")
        
        return courses
    
    def _extract_course_from_json(self, course_json: Dict, topic: str) -> Dict:
        """Extract course data from JSON course object"""
        try:
            title = course_json.get('title', '')
            
            # Skip if no relevant title
            if not title or not self._is_relevant_course(title, topic):
                return {}
            
            # Extract basic course information
            url = course_json.get('url', '')
            if not url:
                # Build URL from urlSlug if available
                url_slug = course_json.get('urlSlug')
                if url_slug:
                    url = f"{self.base_url}/course-detail/{url_slug}"
            
            # Extract other fields
            description = course_json.get('headline', '')
            rating = course_json.get('avgRating')
            provider = course_json.get('providerName', 'Multiple Platforms')
            duration = course_json.get('durationHours', '')
            price_type = course_json.get('priceType', '')
            course_section = course_json.get('courseSection', '')
            author = course_json.get('authorName', '')
            
            # Determine if it's free
            is_free = price_type.lower() in ['free', 'free trial', 'free (audit)']
            
            return {
                'title': title,
                'provider': provider,
                'url': url,
                'description': description,
                'rating': rating,
                'instructor': author,
                'level': 'unknown',
                'duration': duration,
                'price': price_type if is_free else '',
                'format': 'self-paced',
                'language': 'en',
                'certificate': True,
            }
            
        except Exception as e:
            print(f"      Error extracting course from JSON: {e}")
            return {}
    
    def _extract_course_from_link(self, link_element, topic: str) -> Dict:
        """Extract course data from a course detail link"""
        try:
            # Get the link URL
            course_url = link_element.get('href')
            if not course_url:
                return {}
                
            if not course_url.startswith('http'):
                course_url = urljoin(self.base_url, course_url)
            
            # Get title from link text or nearby elements
            title = link_element.get_text(strip=True)
            
            # Look for title in parent elements if link text is empty
            if not title or len(title) < 10:
                parent = link_element.parent
                while parent and not title:
                    title_elem = parent.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        break
                    parent = parent.parent
            
            # Skip if no relevant title found or doesn't match topic
            if not title or not self._is_relevant_course(title, topic):
                return {}
            
            # Look for additional info in surrounding elements
            container = link_element.find_parent(['div', 'article', 'section'])
            if not container:
                container = link_element.parent
            
            # Extract rating
            rating = self._extract_rating(container)
            
            # Extract duration
            duration = self._extract_duration(container)
            
            # Extract provider
            provider = self._extract_provider(container)
            
            # Extract price/free status
            is_free = self._is_free_course(container)
            
            return {
                'title': title,
                'provider': provider or 'Coursesity',
                'url': course_url,
                'description': '',
                'rating': rating,
                'instructor': '',
                'level': 'unknown',
                'duration': duration,
                'price': 'Free' if is_free else '',
                'format': 'self-paced',
                'language': 'en',
                'certificate': True,
            }
            
        except Exception as e:
            print(f"        Error extracting from link: {e}")
            return {}
    
    def extract_course_data(self, course_element) -> Dict:
        """
        Extract course data from a single course element (required by base class)
        This is a wrapper around _extract_course_data for compatibility
        """
        # Since we don't have a topic context here, we'll accept any course
        return self._extract_course_data(course_element, topic="")
    
    def _extract_course_data(self, course_element, topic: str) -> Dict:
        """Extract detailed course data from a course element"""
        try:
            # Extract title
            title_elem = course_element.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            title = title_elem.get_text(strip=True) if title_elem else ''
            
            # Skip if no relevant title
            if not title or not self._is_relevant_course(title, topic):
                return {}
            
            # Extract URL
            link_elem = course_element.find('a', href=True)
            url = ''
            if link_elem:
                url = link_elem.get('href')
                if url and not url.startswith('http'):
                    url = urljoin(self.base_url, url)
            
            # Extract rating
            rating = self._extract_rating(course_element)
            
            # Extract duration
            duration = self._extract_duration(course_element)
            
            # Extract provider
            provider = self._extract_provider(course_element)
            
            # Extract description
            desc_elem = course_element.find(['p', 'div'], class_=lambda x: x and ('description' in x.lower() or 'summary' in x.lower()))
            description = desc_elem.get_text(strip=True) if desc_elem else ''
            
            # Extract price/free status
            is_free = self._is_free_course(course_element)
            
            return {
                'title': title,
                'provider': provider or 'Multiple Platforms',
                'url': url,
                'description': description,
                'rating': rating,
                'instructor': '',
                'level': 'unknown',
                'duration': duration,
                'price': 'Free' if is_free else '',
                'format': 'self-paced',
                'language': 'en',
                'certificate': True,
            }
            
        except Exception as e:
            print(f"      Error extracting course data: {e}")
            return {}
    
    def _extract_rating(self, element) -> float:
        """Extract rating from element"""
        try:
            # Look for rating in various formats
            rating_patterns = [
                r'(\d+\.?\d*)\s*(?:★|stars?|rating)',
                r'★+\s*(\d+\.?\d*)',
                r'(\d+\.?\d*)/5',
                r'rating.*?(\d+\.?\d*)'
            ]
            
            text = element.get_text()
            for pattern in rating_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return float(match.group(1))
            
            # Look for star elements
            stars = element.find_all(class_=lambda x: x and 'star' in x.lower())
            if stars:
                return len([s for s in stars if 'filled' in s.get('class', [])])
                
        except:
            pass
        return None
    
    def _extract_duration(self, element) -> str:
        """Extract duration from element"""
        try:
            # Look for duration patterns
            duration_patterns = [
                r'(\d+)\s*h(?:ours?)?\s*(\d+)?\s*m(?:inutes?)?',
                r'(\d+)\s*hours?',
                r'(\d+)\s*minutes?',
                r'(\d+)\s*h',
                r'(\d+)\s*m'
            ]
            
            text = element.get_text()
            for pattern in duration_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return match.group(0)
                    
            # Look for duration in image alt text or specific elements
            duration_elem = element.find(attrs={'alt': lambda x: x and ('duration' in x.lower() or 'time' in x.lower())})
            if duration_elem:
                return duration_elem.get('alt', '')
                
        except:
            pass
        return ''
    
    def _extract_provider(self, element) -> str:
        """Extract provider/platform from element"""
        try:
            # Common provider names to look for
            providers = ['Udemy', 'Coursera', 'edX', 'Udacity', 'Skillshare', 'Codecademy', 'Pluralsight', 'Khan Academy']
            
            text = element.get_text()
            for provider in providers:
                if provider.lower() in text.lower():
                    return provider
                    
            # Look for provider links
            provider_link = element.find('a', href=lambda x: x and any(p.lower() in x.lower() for p in providers))
            if provider_link:
                for provider in providers:
                    if provider.lower() in provider_link.get('href', '').lower():
                        return provider
                        
        except:
            pass
        return ''
    
    def _is_free_course(self, element) -> bool:
        """Check if course is free"""
        try:
            text = element.get_text().lower()
            free_indicators = ['free', '$0', 'no cost', 'complimentary']
            return any(indicator in text for indicator in free_indicators)
        except:
            return True  # Default to free since we're looking at free courses
    
    def _is_relevant_course(self, title: str, topic: str) -> bool:
        """Check if course title is relevant to the search topic"""
        # If no topic specified, accept all courses
        if not topic:
            return True
            
        title_lower = title.lower()
        topic_lower = topic.lower()
        
        # Direct match
        if topic_lower in title_lower:
            return True
            
        # Topic synonyms and related terms
        topic_synonyms = {
            'python': ['python', 'py', 'programming'],
            'javascript': ['javascript', 'js', 'web dev', 'frontend'],
            'machine learning': ['machine learning', 'ml', 'ai', 'artificial intelligence'],
            'data science': ['data science', 'data analysis', 'analytics', 'statistics'],
            'web development': ['web dev', 'html', 'css', 'frontend', 'backend'],
            'artificial intelligence': ['ai', 'artificial intelligence', 'machine learning', 'neural'],
            'cyber security': ['cyber', 'security', 'hacking', 'cybersecurity'],
            'blockchain': ['blockchain', 'crypto', 'bitcoin', 'ethereum']
        }
        
        synonyms = topic_synonyms.get(topic_lower, [topic_lower])
        return any(synonym in title_lower for synonym in synonyms)
