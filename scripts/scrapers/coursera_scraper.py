"""
Coursera scraper implementation
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from .base_scraper import BaseScraper


class CourseraScraper(BaseScraper):
    """Scraper for Coursera courses"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.coursera.org"
        self.search_url = f"{self.base_url}/search"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def search_courses(self, topic: str, count: int) -> List[Dict]:
        """Search for courses on Coursera"""
        courses = []
        
        try:
            # Coursera search params
            params = {
                'query': topic,
                'tab': 'courses',
                'page': 1
            }
            
            print(f"  Searching Coursera for '{topic}'...")
            response = requests.get(self.search_url, params=params, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find course cards (this selector may need adjustment based on Coursera's current HTML)
            course_cards = soup.find_all('div', class_='cds-CommonCard-container')[:count]
            
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
            print(f"    Error searching Coursera: {e}")
            # Return mock data for now - you can remove this once scraping works
            return self._get_mock_coursera_data(topic, count)
        
        return courses
    
    def extract_course_data(self, course_element) -> Dict:
        """Extract course data from Coursera course card"""
        try:
            # These selectors may need adjustment based on current Coursera HTML structure
            title_elem = course_element.find('h3') or course_element.find('h2')
            title = title_elem.get_text(strip=True) if title_elem else ''
            
            # Extract URL
            link_elem = course_element.find('a', href=True)
            url = self.base_url + link_elem['href'] if link_elem and link_elem['href'].startswith('/') else link_elem['href'] if link_elem else ''
            
            # Extract provider/university
            provider_elem = course_element.find('span', class_='partner-name') or course_element.find('div', class_='partner')
            provider = provider_elem.get_text(strip=True) if provider_elem else 'Coursera'
            
            # Extract rating
            rating_elem = course_element.find('span', class_='ratings-text')
            rating = None
            if rating_elem:
                rating_text = rating_elem.get_text(strip=True)
                try:
                    rating = float(rating_text.split()[0])
                except:
                    pass
            
            # Extract enrollment count
            enrollment_elem = course_element.find('span', class_='enrollment-number')
            enrollment = None
            if enrollment_elem:
                enrollment_text = enrollment_elem.get_text(strip=True)
                # Parse enrollment (e.g., "1.2M", "500K")
                try:
                    if 'M' in enrollment_text:
                        enrollment = int(float(enrollment_text.replace('M', '')) * 1000000)
                    elif 'K' in enrollment_text:
                        enrollment = int(float(enrollment_text.replace('K', '')) * 1000)
                except:
                    pass
            
            return {
                'title': title,
                'provider': provider,
                'url': url,
                'description': '',  # Would need to visit individual course page for full description
                'rating': rating,
                'enrollment_count': enrollment,
                'level': 'unknown',  # Would need course page for level
                'duration': '',  # Would need course page for duration
                'price': '',  # Would need course page for price
                'format': 'online',
                'language': 'en',
                'certificate': True,  # Most Coursera courses offer certificates
            }
            
        except Exception as e:
            print(f"      Error extracting course data: {e}")
            return {}
    
    def _get_mock_coursera_data(self, topic: str, count: int) -> List[Dict]:
        """Return mock Coursera data for testing (remove once scraping works)"""
        mock_courses = []
        for i in range(min(count, 3)):
            course = {
                'title': f'Introduction to {topic.title()} - Part {i+1}',
                'provider': 'Stanford University' if i == 0 else 'University of Washington' if i == 1 else 'Google',
                'url': f'https://www.coursera.org/learn/{topic.replace(" ", "-")}-{i+1}',
                'description': f'Learn the fundamentals of {topic} in this comprehensive course.',
                'duration_hours': 20 + i * 10,
                'level': 'beginner' if i == 0 else 'intermediate' if i == 1 else 'advanced',
                'format': 'self-paced',
                'price': 0.0 if i == 0 else 49.0 + i * 10,
                'rating': 4.5 - i * 0.2,
                'enrollment_count': 100000 - i * 20000,
                'language': 'en',
                'certificate': True,
                'instructor': f'Dr. {topic.title()} Expert {i+1}',
                'skills': [],
            }
            mock_courses.append(course)
        
        print(f"    Using mock data: {len(mock_courses)} courses")
        return mock_courses
