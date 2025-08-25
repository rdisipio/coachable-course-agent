"""
LLM processor for standardizing and enhancing scraped course data
Uses Groq/Llama for data processing
"""

import os
import json
from typing import List, Dict
from groq import Groq


class LLMProcessor:
    """Process scraped course data with LLM for standardization"""
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        self.model = "llama-3.1-70b-versatile"  # Adjust model as needed
    
    def standardize_courses(self, courses: List[Dict]) -> List[Dict]:
        """
        Process a batch of courses with LLM for standardization
        
        Args:
            courses: List of raw course dictionaries
            
        Returns:
            List of processed/standardized course dictionaries
        """
        processed_courses = []
        
        # Process in batches to avoid token limits
        batch_size = 5
        for i in range(0, len(courses), batch_size):
            batch = courses[i:i + batch_size]
            try:
                processed_batch = self._process_batch(batch)
                processed_courses.extend(processed_batch)
            except Exception as e:
                print(f"      Warning: LLM processing failed for batch {i//batch_size + 1}: {e}")
                # Fall back to original data if LLM fails
                processed_courses.extend(batch)
        
        return processed_courses
    
    def _process_batch(self, courses: List[Dict]) -> List[Dict]:
        """Process a small batch of courses with LLM"""
        
        # Prepare prompt for LLM
        prompt = self._create_standardization_prompt(courses)
        
        # Call LLM
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a data processing expert specializing in online course metadata standardization."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,  # Low temperature for consistent output
            max_tokens=4000
        )
        
        # Parse LLM response
        try:
            result = json.loads(response.choices[0].message.content)
            return result.get('courses', courses)  # Fallback to original if parsing fails
        except json.JSONDecodeError:
            print("      Warning: Failed to parse LLM response as JSON")
            return courses
    
    def _create_standardization_prompt(self, courses: List[Dict]) -> str:
        """Create prompt for LLM course standardization"""
        
        courses_json = json.dumps(courses, indent=2)
        
        prompt = f"""
Please standardize and enhance the following course data. For each course:

1. **Clean and standardize fields:**
   - duration_hours: Convert any duration text to hours (integer)
   - level: Standardize to "beginner", "intermediate", "advanced", or "unknown"
   - format: Standardize to "self-paced", "instructor-led", or "online"
   - price: Convert to numeric value (0.0 for free)

2. **Enhance descriptions:**
   - If description is empty, create a brief, professional description based on title
   - Keep descriptions concise (2-3 sentences max)

3. **Extract learning objectives:**
   - Add a "learning_objectives" field with 3-5 key skills/topics covered
   - Base this on the title and any available description

4. **Validate data:**
   - Ensure URLs are properly formatted
   - Clean up any malformed text
   - Set reasonable defaults for missing data

Input courses:
{courses_json}

Return the processed data as a JSON object with this structure:
{{
  "courses": [
    {{
      "title": "cleaned title",
      "provider": "provider name", 
      "url": "full URL",
      "description": "enhanced description",
      "duration_hours": 25,
      "level": "beginner|intermediate|advanced|unknown",
      "format": "self-paced|instructor-led|online",
      "price": 0.0,
      "rating": 4.5,
      "enrollment_count": 10000,
      "language": "en",
      "certificate": true,
      "instructor": "instructor name",
      "learning_objectives": ["objective 1", "objective 2", "objective 3"],
      "skills": [],
      "source_platform": "original platform",
      "scraped_at": "original timestamp"
    }}
  ]
}}

Only return valid JSON. Do not include any explanatory text.
"""
        return prompt
