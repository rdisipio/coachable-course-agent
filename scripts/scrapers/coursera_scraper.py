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
            
            # Find course cards - updated selector based on current Coursera HTML
            course_cards = soup.find_all('div', class_='cds-CommonCard-clickArea')[:count]
            
            if not course_cards:
                # Fallback to broader selector
                course_cards = soup.select('div[class*="cds-CommonCard"]')[:count]
            
            print(f"    Found {len(course_cards)} course cards")
            
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
        
        # Return whatever we found (might be empty)
        if courses:
            print(f"    Successfully scraped {len(courses)} real courses")
        else:
            print(f"    No courses found")
            
        return courses
    
    def extract_course_data(self, course_element) -> Dict:
        """Extract course data from Coursera course card"""
        try:
            # Extract title - try multiple selectors
            title_elem = (course_element.find('h3') or 
                         course_element.find('h2') or 
                         course_element.find('h4') or
                         course_element.find(string=True, class_=lambda x: x and 'title' in x.lower()))
            title = title_elem.get_text(strip=True) if hasattr(title_elem, 'get_text') else str(title_elem).strip() if title_elem else ''
            
            # Extract URL - look for any link
            link_elem = course_element.find('a', href=True)
            if not link_elem:
                # Look in parent elements
                parent = course_element.parent
                while parent and not link_elem:
                    link_elem = parent.find('a', href=True)
                    parent = parent.parent
                    
            url = ''
            if link_elem:
                href = link_elem['href']
                url = self.base_url + href if href.startswith('/') else href
            
            # Improved description extraction - try multiple approaches
            description = ''
            
            # First, try to find specific description elements
            desc_selectors = [
                'p[class*="description"]',
                'div[class*="description"]',
                'p[class*="summary"]',
                'div[class*="summary"]',
                'div[data-track-component="description"]',
                '[class*="body"]',  # Look for body text
                'p',  # Fallback to any paragraph
            ]
            
            for selector in desc_selectors:
                desc_elem = course_element.select_one(selector)
                if desc_elem and desc_elem.get_text(strip=True):
                    desc_text = desc_elem.get_text(strip=True)
                    # Only use if it's a reasonable description (not just metadata)
                    if (len(desc_text) > 30 and 
                        not desc_text.lower().startswith(('status:', 'skills:', 'duration:', 'rating:')) and
                        not desc_text.isdigit()):
                        description = desc_text
                        break
            
            # If no good description found, try to build one from multiple elements
            if not description or len(description) < 30:
                # Look for multiple text elements that might form a description
                text_elements = []
                
                # Try different text-containing elements
                for elem in course_element.find_all(['p', 'div', 'span'], string=True):
                    text = elem.get_text(strip=True)
                    if (text and len(text) > 10 and len(text) < 200 and
                        not text.lower().startswith(('status:', 'skills:', 'duration:', 'rating:', 'enroll', 'free trial')) and
                        not text.isdigit() and
                        not text.endswith('|')):
                        text_elements.append(text)
                
                if text_elements:
                    # Take the longest meaningful text as description
                    text_elements.sort(key=len, reverse=True)
                    description = text_elements[0]
                    
            # If still no good description, get contextual information from the whole card
            if not description or len(description) < 30:
                # Get all text but clean it up more carefully
                all_text_parts = []
                for text_node in course_element.find_all(string=True):
                    text = text_node.strip()
                    if (text and len(text) > 5 and 
                        not any(skip in text.lower() for skip in ['status:', 'free trial', 'enroll now', 'rating', '|']) and
                        not text.isdigit()):
                        all_text_parts.append(text)
                
                if all_text_parts and len(all_text_parts) > 1:
                    # Create a meaningful description from the parts
                    meaningful_parts = [part for part in all_text_parts if len(part) > 15]
                    if meaningful_parts:
                        description = '. '.join(meaningful_parts[:2])
                        if not description.endswith('.'):
                            description += '.'
                    else:
                        # Fallback to joining shorter parts
                        description = ' '.join(all_text_parts[:5])
                        if len(description) > 300:
                            description = description[:300] + '...'
            
            # Try to find provider/university name
            provider = 'Coursera'
            provider_indicators = ['university', 'college', 'institute', 'school']
            all_text = course_element.get_text(separator=' ', strip=True)
            words = all_text.lower().split()
            for i, word in enumerate(words):
                if any(indicator in word for indicator in provider_indicators):
                    # Take surrounding words as potential provider name
                    start = max(0, i-2)
                    end = min(len(words), i+3)
                    potential_provider = ' '.join(words[start:end])
                    if len(potential_provider) < 50:  # Reasonable length
                        provider = potential_provider.title()
                        break
            
            print(f"      Extracted: '{title[:50]}...' from {provider}")
            
            return {
                'title': title,
                'provider': provider,
                'url': url,
                'description': description,  # Use the improved description
                'rating': None,
                'enrollment_count': None,
                'level': 'unknown',
                'duration': '',
                'price': '',
                'format': 'online',
                'language': 'en',
                'certificate': True,  # Most Coursera courses offer certificates
                'source_platform': 'coursera',  # Add source platform for standardization
            }
            
        except Exception as e:
            print(f"      Error extracting course data: {e}")
            return {}
