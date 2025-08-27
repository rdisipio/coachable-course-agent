"""
Udemy scraper implementation
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from .base_scraper import BaseScraper


class UdemyScraper(BaseScraper):
    """Scraper for Udemy courses"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.udemy.com"
        self.search_url = f"{self.base_url}/courses/search/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        self.delay_range = (3, 6)  # Longer delays for Udemy
    
    def search_courses(self, topic: str, count: int) -> List[Dict]:
        """Search for courses on Udemy"""
        courses = []
        
        try:
            params = {
                'q': topic,
                'sort': 'relevance',
                'src': 'ukw'
            }
            
            print(f"  Searching Udemy for '{topic}'...")
            response = requests.get(self.search_url, params=params, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find course cards (selector may need adjustment)
            course_cards = soup.find_all('div', class_='course-card--container--1QM2W')[:count]
            
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
            print(f"    Error searching Udemy: {e}")
        
        if courses:
            print(f"    Successfully scraped {len(courses)} real courses")
        else:
            print(f"    No courses found")
            
        return courses
    
    def extract_course_data(self, course_element) -> Dict:
        """Extract course data from Udemy course card"""
        try:
            # Extract title
            title_elem = course_element.find('h3') or course_element.find('h2')
            title = title_elem.get_text(strip=True) if title_elem else ''
            
            # Extract URL
            link_elem = course_element.find('a', href=True)
            url = self.base_url + link_elem['href'] if link_elem and link_elem['href'].startswith('/') else link_elem['href'] if link_elem else ''
            
            # Extract instructor
            instructor_elem = course_element.find('span', class_='instructor-name')
            instructor = instructor_elem.get_text(strip=True) if instructor_elem else ''
            
            # Extract rating
            rating_elem = course_element.find('span', class_='star-rating-module--rating-number')
            rating = None
            if rating_elem:
                try:
                    rating = float(rating_elem.get_text(strip=True))
                except:
                    pass
            
            # Extract price
            price_elem = course_element.find('span', class_='price-text')
            price = price_elem.get_text(strip=True) if price_elem else ''
            
            # Extract duration
            duration_elem = course_element.find('span', class_='curriculum-info-container')
            duration = duration_elem.get_text(strip=True) if duration_elem else ''
            
            # Extract level
            level_elem = course_element.find('span', class_='course-badge')
            level = level_elem.get_text(strip=True) if level_elem else 'unknown'
            
            return {
                'title': title,
                'provider': 'Udemy',
                'url': url,
                'description': '',  # Would need course page for full description
                'rating': rating,
                'instructor': instructor,
                'level': level,
                'duration': duration,
                'price': price,
                'format': 'self-paced',
                'language': 'en',
                'certificate': True,  # Most Udemy courses offer certificates
            }
            
        except Exception as e:
            print(f"      Error extracting course data: {e}")
            return {}
