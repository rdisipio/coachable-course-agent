"""
MIT OpenCourseWare Scraper
Scrapes course data from MIT's OpenCourseWare platform
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


class MITScraper(BaseScraper):
    """Scraper for MIT OpenCourseWare"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://ocw.mit.edu"
        self.search_url = "https://ocw.mit.edu/search/"
        
    def search_courses(self, topic: str, count: int) -> List[Dict]:
        """Search for courses on MIT OCW using predefined popular courses"""
        courses = []
        
        print(f"🏫 Searching MIT OpenCourseWare for '{topic}'...")
        
        # Popular MIT OCW courses organized by topic
        mit_courses = {
            'computer science': [
                'https://ocw.mit.edu/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/',
                'https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/',
                'https://ocw.mit.edu/courses/6-046j-design-and-analysis-of-algorithms-spring-2015/',
                'https://ocw.mit.edu/courses/6-034-artificial-intelligence-fall-2010/',
                'https://ocw.mit.edu/courses/6-00sc-introduction-to-computer-science-and-programming-spring-2011/'
            ],
            'programming': [
                'https://ocw.mit.edu/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/',
                'https://ocw.mit.edu/courses/6-00sc-introduction-to-computer-science-and-programming-spring-2011/',
                'https://ocw.mit.edu/courses/6-189-a-gentle-introduction-to-programming-using-python-january-iap-2011/'
            ],
            'machine learning': [
                'https://ocw.mit.edu/courses/6-034-artificial-intelligence-fall-2010/',
                'https://ocw.mit.edu/courses/6-867-machine-learning-fall-2006/',
                'https://ocw.mit.edu/courses/9-520-statistical-learning-theory-and-applications-spring-2003/'
            ],
            'artificial intelligence': [
                'https://ocw.mit.edu/courses/6-034-artificial-intelligence-fall-2010/',
                'https://ocw.mit.edu/courses/6-825-techniques-in-artificial-intelligence-sma-5504-fall-2002/'
            ],
            'mathematics': [
                'https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010/',
                'https://ocw.mit.edu/courses/18-02sc-multivariable-calculus-fall-2010/',
                'https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/',
                'https://ocw.mit.edu/courses/18-05-introduction-to-probability-and-statistics-spring-2014/'
            ],
            'physics': [
                'https://ocw.mit.edu/courses/8-01sc-classical-mechanics-fall-2016/',
                'https://ocw.mit.edu/courses/8-02-physics-ii-electricity-and-magnetism-spring-2007/',
                'https://ocw.mit.edu/courses/8-04-quantum-physics-i-spring-2013/'
            ],
            'economics': [
                'https://ocw.mit.edu/courses/14-01-principles-of-microeconomics-fall-2018/',
                'https://ocw.mit.edu/courses/14-02-principles-of-macroeconomics-spring-2014/',
                'https://ocw.mit.edu/courses/15-501-introduction-to-financial-and-managerial-accounting-spring-2004/'
            ]
        }
        
        # Find relevant courses based on topic
        topic_lower = topic.lower()
        relevant_urls = []
        
        for category, urls in mit_courses.items():
            if any(word in topic_lower for word in category.split()) or category in topic_lower:
                relevant_urls.extend(urls)
        
        # If no specific match, use computer science as default
        if not relevant_urls:
            relevant_urls = mit_courses.get('computer science', [])
        
        # Remove duplicates and limit count
        relevant_urls = list(set(relevant_urls))[:count]
        
        print(f"   Found {len(relevant_urls)} relevant course URLs")
        
        # Extract course data from each URL
        for i, url in enumerate(relevant_urls):
            try:
                print(f"   Processing course {i+1}/{len(relevant_urls)}")
                course_data = self.extract_course_from_url(url)
                if course_data:
                    courses.append(course_data)
                
                # Rate limiting
                time.sleep(random.uniform(*self.delay_range))
                
            except Exception as e:
                print(f"   ⚠️ Error extracting course from {url}: {e}")
                continue
                
        print(f"✅ Successfully scraped {len(courses)} courses from MIT")
        return courses
    
    def extract_course_from_url(self, url: str) -> Dict:
        """Extract course data from a course URL"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            return self.extract_course_data(soup, url)
            
        except Exception as e:
            print(f"   Error fetching course page {url}: {e}")
            return None
    
    def extract_course_data(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extract course data from course page soup"""
        
        # Extract title
        title = ""
        title_elem = soup.find('h1') or soup.find('title')
        if title_elem:
            title = title_elem.get_text(strip=True)
            # Clean up title
            title = re.sub(r'\\s*\\|\\s*MIT OpenCourseWare', '', title)
            title = re.sub(r'^[\\d\\.]+\\s*\\|\\s*', '', title)  # Remove course number prefix
        
        # Extract description
        description = ""
        desc_selectors = [
            '.course-description',
            '.description', 
            'meta[name="description"]',
            '.course-intro',
            'p'
        ]
        
        for selector in desc_selectors:
            desc_elem = soup.select_one(selector)
            if desc_elem:
                if desc_elem.name == 'meta':
                    description = desc_elem.get('content', '')
                else:
                    description = desc_elem.get_text(strip=True)
                if description and len(description) > 50:
                    break
        
        # Extract course number/level info
        level = "Unknown"
        course_num = ""
        
        # Look for course number in URL or title
        course_num_match = re.search(r'(\\d+[\\w\\.]*)', url)
        if course_num_match:
            course_num = course_num_match.group(1)
            
        # Determine level based on course number
        if course_num:
            if course_num.startswith(('1', '2', '3', '6.00')):
                level = "Undergraduate"
            elif course_num.startswith(('6.', '15.', '18.')):
                level = "Advanced"
            else:
                level = "Intermediate"
        
        # Extract department/subject
        subject = ""
        dept_match = re.search(r'/courses/([^/]+)', url)
        if dept_match:
            subject = dept_match.group(1).replace('-', ' ').title()
        
        # Extract duration (estimate from MIT OCW structure)
        duration_hours = 0
        # MIT courses are typically semester-long
        if "laboratory" in title.lower():
            duration_hours = 60  # Lab courses
        elif "seminar" in title.lower():
            duration_hours = 30  # Seminars
        else:
            duration_hours = 45  # Regular courses
        
        # Extract skills from title and description
        skills = self.extract_skills_from_text(f"{title} {description}")
        
        course_data = {
            "id": str(uuid.uuid4()),
            "title": title,
            "provider": "MIT OpenCourseWare",
            "url": url,
            "description": description,
            "duration_hours": duration_hours,
            "level": level,
            "format": "Online",
            "skills": skills,
            "subject": subject,
            "course_number": course_num,
            "rating": 4.8,  # MIT OCW is generally high quality
            "enrollment_count": 0,  # Not available for OCW
            "source_platform": "mit_ocw"
        }
        
        return course_data
    
    def extract_skills_from_text(self, text: str) -> List[str]:
        """Extract potential skills from course text"""
        skills = []
        text_lower = text.lower()
        
        # Common technical skills
        tech_skills = [
            'python', 'java', 'javascript', 'c++', 'c programming', 'sql',
            'machine learning', 'artificial intelligence', 'data analysis',
            'statistics', 'calculus', 'linear algebra', 'probability',
            'algorithms', 'programming', 'software engineering',
            'computer science', 'mathematics', 'physics', 'chemistry',
            'biology', 'economics', 'finance', 'management'
        ]
        
        for skill in tech_skills:
            if skill in text_lower:
                skills.append(skill.title())
        
        return skills
