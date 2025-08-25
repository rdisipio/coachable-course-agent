"""
edX scraper implementation
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from .base_scraper import BaseScraper


class EdxScraper(BaseScraper):
    """Scraper for edX courses"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.edx.org"
        self.search_url = f"{self.base_url}/search"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def search_courses(self, topic: str, count: int) -> List[Dict]:
        """Search for courses on edX"""
        courses = []
        
        try:
            params = {
                'q': topic,
                'tab': 'course'
            }
            
            print(f"  Searching edX for '{topic}'...")
            response = requests.get(self.search_url, params=params, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find course cards (selector may need adjustment)
            course_cards = soup.find_all('div', class_='discovery-card')[:count]
            
            for card in course_cards:
                try:
                    course_data = self.extract_course_data(card)
                    if course_data:
                        standardized = self.standardize_course_data(course_data)
                        courses.append(standardized)
                        
                        if len(courses) >= count:
                            break
                            
                except Exception as e:
                    print(f"    Warning: Failed to extract course data: {e}")
                    continue
                
                self.sleep_between_requests()
            
        except Exception as e:
            print(f"    Error searching edX: {e}")
            # Return mock data for now
            return self._get_mock_edx_data(topic, count)
        
        return courses
    
    def extract_course_data(self, course_element) -> Dict:
        """Extract course data from edX course card"""
        try:
            # Extract title
            title_elem = course_element.find('h3') or course_element.find('h2')
            title = title_elem.get_text(strip=True) if title_elem else ''
            
            # Extract URL
            link_elem = course_element.find('a', href=True)
            url = self.base_url + link_elem['href'] if link_elem and link_elem['href'].startswith('/') else link_elem['href'] if link_elem else ''
            
            # Extract university/provider
            provider_elem = course_element.find('span', class_='partner-name') or course_element.find('div', class_='school')
            provider = provider_elem.get_text(strip=True) if provider_elem else 'edX'
            
            # Extract duration
            duration_elem = course_element.find('span', class_='course-duration')
            duration = duration_elem.get_text(strip=True) if duration_elem else ''
            
            # Extract level
            level_elem = course_element.find('span', class_='course-level')
            level = level_elem.get_text(strip=True) if level_elem else 'unknown'
            
            # Extract price (edX often has free and paid options)
            price_elem = course_element.find('span', class_='course-price')
            price = price_elem.get_text(strip=True) if price_elem else 'Free'
            
            return {
                'title': title,
                'provider': provider,
                'url': url,
                'description': '',  # Would need course page for full description
                'level': level,
                'duration': duration,
                'price': price,
                'format': 'self-paced',  # Most edX courses are self-paced
                'language': 'en',
                'certificate': True,  # edX offers verified certificates
            }
            
        except Exception as e:
            print(f"      Error extracting course data: {e}")
            return {}
    
    def _get_mock_edx_data(self, topic: str, count: int) -> List[Dict]:
        """Return mock edX data for testing (remove once scraping works)"""
        mock_courses = []
        for i in range(min(count, 3)):
            course = {
                'title': f'{topic.title()} Fundamentals - MITx',
                'provider': 'MIT' if i == 0 else 'Harvard' if i == 1 else 'UC Berkeley',
                'url': f'https://www.edx.org/course/{topic.replace(" ", "-")}-fundamentals-{i+1}',
                'description': f'Learn {topic} from world-class universities.',
                'duration_hours': 40 + i * 20,
                'level': 'intermediate' if i == 0 else 'advanced' if i == 1 else 'beginner',
                'format': 'self-paced',
                'price': 0.0 if i == 2 else 99.0 + i * 50,  # Some free, some paid
                'rating': 4.4 + i * 0.1,
                'enrollment_count': 25000 + i * 5000,
                'language': 'en',
                'certificate': True,
                'instructor': f'Professor {topic.title()} {i+1}',
                'skills': [],
            }
            mock_courses.append(course)
        
        print(f"    Using mock data: {len(mock_courses)} courses")
        return mock_courses
