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
        
        if courses:
            print(f"    Successfully scraped {len(courses)} real courses")
        else:
            print(f"    No courses found")
            
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
