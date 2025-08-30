"""
Harvard Online Learning Scraper
Scrapes course data from Harvard's Professional and Lifelong Learning platform
"""

import requests
from bs4 import BeautifulSoup
import time
import random
import uuid
from urllib.parse import urljoin, urlparse
import json
import re
from typing import List, Dict

from .base_scraper import BaseScraper


class HarvardScraper(BaseScraper):
    """Scraper for Harvard Professional and Lifelong Learning"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://pll.harvard.edu"
        self.catalog_url = "https://pll.harvard.edu/catalog"
        
    def search_courses(self, topic: str, count: int) -> List[Dict]:
        """Search for courses on Harvard PLL"""
        courses = []
        
        print(f"🏫 Searching Harvard PLL for '{topic}'...")
        
        try:
            # Search through catalog pages
            page = 0
            courses_found = 0
            
            while courses_found < count and page < 10:  # Limit to 10 pages
                params = {
                    'page': page,
                    'search': topic
                }
                
                response = requests.get(self.catalog_url, params=params, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find course cards
                course_cards = soup.find_all('div', class_='course-card') or \
                              soup.find_all('a', href=re.compile(r'/course/'))
                
                if not course_cards:
                    print(f"   No more courses found on page {page}")
                    break
                
                print(f"   Processing page {page}, found {len(course_cards)} course cards")
                
                # Extract course data from each card
                for card in course_cards:
                    if courses_found >= count:
                        break
                        
                    try:
                        course_data = self.extract_course_data(card)
                        if course_data and self.is_relevant_course(course_data, topic):
                            courses.append(course_data)
                            courses_found += 1
                            print(f"   ✅ Added: {course_data['title']}")
                        
                    except Exception as e:
                        print(f"   ⚠️ Error extracting course: {e}")
                        continue
                
                page += 1
                time.sleep(random.uniform(*self.delay_range))
                
        except Exception as e:
            print(f"❌ Error searching Harvard PLL: {e}")
            
        print(f"✅ Successfully scraped {len(courses)} courses from Harvard")
        return courses
    
    def extract_course_data(self, course_element) -> Dict:
        """Extract course data from a course card element"""
        
        # Extract title and URL
        title_link = course_element.find('a') or course_element
        title = ""
        url = ""
        
        if title_link:
            title = title_link.get_text(strip=True)
            href = title_link.get('href')
            if href:
                url = urljoin(self.base_url, href)
        
        # Clean up title
        title = re.sub(r'^###\\s*', '', title)  # Remove markdown headers
        
        # Extract description
        description = ""
        desc_elem = course_element.find_next('p') or \
                   course_element.find('div', class_='description')
        if desc_elem:
            description = desc_elem.get_text(strip=True)
        
        # Extract price
        price_text = ""
        price_elem = course_element.find(string=re.compile(r'PRICE'))
        if price_elem:
            price_parent = price_elem.find_parent()
            if price_parent:
                price_text = price_parent.get_text(strip=True)
        
        # Extract duration
        duration_text = ""
        duration_hours = 0
        duration_elem = course_element.find(string=re.compile(r'DURATION'))
        if duration_elem:
            duration_parent = duration_elem.find_parent()
            if duration_parent:
                duration_text = duration_parent.get_text(strip=True)
                # Extract hours from duration
                weeks_match = re.search(r'(\\d+)\\s*WEEKS?', duration_text, re.IGNORECASE)
                if weeks_match:
                    weeks = int(weeks_match.group(1))
                    duration_hours = weeks * 10  # Estimate 10 hours per week
        
        # Determine level
        level = "Intermediate"
        title_lower = title.lower()
        if any(word in title_lower for word in ['introduction', 'intro', 'beginner', 'basics']):
            level = "Beginner"
        elif any(word in title_lower for word in ['advanced', 'expert', 'master']):
            level = "Advanced"
        
        # Extract subject area
        subject = ""
        subject_elem = course_element.find('span', string=re.compile(r'COMPUTER SCIENCE|PROGRAMMING|HEALTH|MEDICINE|HUMANITIES|SOCIAL SCIENCES'))
        if subject_elem:
            subject = subject_elem.get_text(strip=True)
        
        # Extract skills from title and description
        skills = self.extract_skills_from_text(f"{title} {description}")
        
        # Determine if free or paid
        is_free = "FREE" in price_text
        
        course_data = {
            "id": str(uuid.uuid4()),
            "title": title,
            "provider": "Harvard University",
            "url": url,
            "description": description,
            "duration_hours": duration_hours or 20,  # Default estimate
            "level": level,
            "format": "Online",
            "skills": skills,
            "subject": subject,
            "rating": 4.7,  # Harvard is generally high quality
            "enrollment_count": 0,  # Not available
            "price": "Free" if is_free else "Paid",
            "source_platform": "harvard_pll"
        }
        
        return course_data
    
    def extract_skills_from_text(self, text: str) -> List[str]:
        """Extract potential skills from course text"""
        skills = []
        text_lower = text.lower()
        
        # Common skills for Harvard courses
        skill_keywords = [
            'programming', 'computer science', 'python', 'javascript', 'web development',
            'data science', 'statistics', 'machine learning', 'artificial intelligence',
            'business', 'management', 'leadership', 'finance', 'economics',
            'marketing', 'strategy', 'health', 'medicine', 'psychology',
            'philosophy', 'ethics', 'law', 'writing', 'communication',
            'project management', 'research', 'analysis'
        ]
        
        for skill in skill_keywords:
            if skill in text_lower:
                skills.append(skill.title())
        
        return skills
    
    def is_relevant_course(self, course_data: Dict, topic: str) -> bool:
        """Check if course is relevant to the search topic"""
        topic_lower = topic.lower()
        searchable_text = f"{course_data['title']} {course_data['description']} {' '.join(course_data['skills'])}".lower()
        
        # Simple relevance check
        return topic_lower in searchable_text or any(word in searchable_text for word in topic_lower.split())
