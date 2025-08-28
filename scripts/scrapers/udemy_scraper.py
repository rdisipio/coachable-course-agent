"""
Udemy scraper implementation - Enhanced version based on Medium article techniques
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import time
import random
from urllib.parse import quote_plus
from .base_scraper import BaseScraper


class UdemyScraper(BaseScraper):
    """Enhanced Udemy scraper with better anti-detection measures"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.udemy.com"
        self.search_url = f"{self.base_url}/courses/search/"
        
        # Enhanced headers based on Medium article recommendations
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Ch-Ua-Platform': '"macOS"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.udemy.com/'
        }
        
        # Initialize session for better cookie and state management
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.delay_range = (3, 6)  # Longer delays for Udemy
    
    def search_courses(self, topic: str, count: int) -> List[Dict]:
        """Enhanced search for courses on Udemy using alternative endpoints"""
        courses = []
        
        try:
            # First visit the homepage to establish session (Medium article technique)
            print(f"  Establishing session with Udemy...")
            home_response = self.session.get(self.base_url, timeout=(5, 60))
            home_response.raise_for_status()
            
            # Add some random delay to avoid detection
            time.sleep(random.uniform(*self.delay_range))
            
            # Try different search approaches
            search_approaches = [
                # Approach 1: Standard search
                {
                    'url': f"{self.base_url}/courses/search/",
                    'params': {'q': topic, 'sort': 'relevance', 'src': 'ukw'}
                },
                # Approach 2: Category browse (if search fails)
                {
                    'url': f"{self.base_url}/courses/development/",
                    'params': {}
                }
            ]
            
            for approach in search_approaches:
                print(f"  Trying search approach: {approach['url']}")
                
                response = self.session.get(
                    approach['url'], 
                    params=approach['params'],
                    timeout=(5, 60),
                    allow_redirects=True
                )
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Try to find course links or data
                    # Look for any links that contain '/course/'
                    course_links = soup.find_all('a', href=lambda x: x and '/course/' in x)
                    
                    if course_links:
                        print(f"    Found {len(course_links)} course links")
                        
                        # Extract course information from links
                        for link in course_links[:count]:
                            try:
                                course_url = link.get('href')
                                if not course_url.startswith('http'):
                                    course_url = self.base_url + course_url
                                
                                # Get course title from link text or parent elements
                                title = self._extract_title_from_link(link)
                                
                                if title and topic.lower() in title.lower():
                                    course_data = {
                                        'title': title,
                                        'provider': 'Udemy',
                                        'url': course_url,
                                        'description': '',
                                        'rating': None,
                                        'instructor': '',
                                        'level': 'unknown',
                                        'duration': '',
                                        'price': '',
                                        'format': 'self-paced',
                                        'language': 'en',
                                        'certificate': True,
                                    }
                                    
                                    standardized = self.standardize_course_data(course_data)
                                    courses.append(standardized)
                                    
                                    if len(courses) >= count:
                                        break
                                        
                            except Exception as e:
                                print(f"    Error processing course link: {e}")
                                continue
                        
                        if courses:
                            break  # Found courses, no need to try other approaches
                    
                    else:
                        print(f"    No course links found in this approach")
                
                else:
                    print(f"    Approach failed with status: {response.status_code}")
                    
        except requests.exceptions.Timeout:
            print("    Timeout occurred while searching Udemy")
        except requests.exceptions.RequestException as e:
            print(f"    Error searching Udemy: {e}")
        except Exception as e:
            print(f"    Unexpected error: {e}")
            
        return courses
    
    def _extract_title_from_link(self, link) -> str:
        """Extract course title from a course link element"""
        # Try different methods to get the title
        title = link.get_text(strip=True)
        if title:
            return title
            
        # Look in parent elements
        parent = link.parent
        while parent and not title:
            title_elem = parent.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if title_elem:
                title = title_elem.get_text(strip=True)
                break
            parent = parent.parent
            
        return title or "Unknown Course"
            
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
