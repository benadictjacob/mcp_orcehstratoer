"""
Job Scraper - Scrape career pages and find matching jobs
Commands: scrape, match, help
"""

import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re

# Store user profile and scraped jobs
USER_PROFILE = {}
SCRAPED_JOBS = []

def run(input_text: str) -> str:
    """Main entry point for job scraper"""
    parts = input_text.strip().split(maxsplit=1)
    command = parts[0].lower() if parts else "help"
    args = parts[1] if len(parts) > 1 else ""
    
    commands = {
        "scrape": scrape_jobs,
        "match": match_jobs,
        "profile": set_profile,
        "list": list_jobs,
        "help": show_help
    }
    
    if command in commands:
        return commands[command](args)
    else:
        return f"Unknown command: {command}\n\n" + show_help("")

def show_help(args: str) -> str:
    """Show help information"""
    return """Job Scraper - Find jobs that match your profile

Commands:
  profile <JSON>     - Set your profile (skills, experience, preferences)
                      Example: profile {"skills": ["Python", "AI"], "experience": "3 years", "role": "ML Engineer"}
  
  scrape <URL>       - Scrape career page and extract job listings
                      Example: scrape https://company.com/careers
  
  match              - Match scraped jobs against your profile
                      Returns jobs ranked by relevance
  
  list               - List all scraped jobs
  
  help               - Show this help message

Workflow:
1. Set your profile with 'profile' command
2. Scrape one or more career pages with 'scrape' command
3. Get matched jobs with 'match' command
"""

def set_profile(args: str) -> str:
    """Set user profile"""
    global USER_PROFILE
    
    if not args:
        return "Error: Please provide profile data in JSON format"
    
    try:
        USER_PROFILE = json.loads(args)
        return f"[SUCCESS] Profile set successfully!\n\nYour profile:\n{json.dumps(USER_PROFILE, indent=2)}"
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON format - {str(e)}"

def scrape_jobs(args: str) -> str:
    """Scrape jobs from a career page"""
    global SCRAPED_JOBS
    
    if not args:
        return "Error: Please provide a URL to scrape"
    
    url = args.strip()
    
    try:
        # Validate URL
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return "Error: Invalid URL format. Please include http:// or https://"
        
        # Fetch the page
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract jobs (generic approach - looks for common patterns)
        jobs = extract_job_listings(soup, url)
        
        if not jobs:
            return f"No jobs found at {url}\n\nThe page might use JavaScript to load content or have a different structure.\nTry providing the careers page URL or a job listings page."
        
        # Add to scraped jobs
        for job in jobs:
            job['source_url'] = url
        
        SCRAPED_JOBS.extend(jobs)
        
        return f"[SUCCESS] Found {len(jobs)} jobs at {url}\n\n" + \
               f"Total scraped jobs: {len(SCRAPED_JOBS)}\n\n" + \
               "Use 'match' command to find jobs matching your profile, or 'list' to see all jobs."
        
    except requests.RequestException as e:
        return f"Error fetching URL: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

def extract_job_listings(soup, base_url):
    """Extract job listings from HTML"""
    jobs = []
    
    # Common job listing selectors
    selectors = [
        {'container': 'div.job-listing', 'title': 'h3', 'location': '.location', 'description': '.description'},
        {'container': 'div.job-item', 'title': 'h2', 'location': '.job-location', 'description': '.job-description'},
        {'container': 'li.job', 'title': 'a', 'location': 'span.location', 'description': 'p'},
        {'container': 'article', 'title': 'h2,h3', 'location': '.location,.office', 'description': 'p,.summary'},
        {'container': 'div[class*="job"]', 'title': 'h2,h3,h4', 'location': None, 'description': 'p'},
    ]
    
    # Try each selector pattern
    for selector in selectors:
        containers = soup.select(selector['container'])
        
        for container in containers:
            title_elem = container.select_one(selector['title'])
            if not title_elem:
                continue
            
            title = title_elem.get_text(strip=True)
            
            # Extract link
            link = None
            link_elem = container.find('a', href=True)
            if link_elem:
                link = urljoin(base_url, link_elem['href'])
            
            # Extract location
            location = ""
            if selector['location']:
                loc_elem = container.select_one(selector['location'])
                if loc_elem:
                    location = loc_elem.get_text(strip=True)
            
            # Extract description
            description = ""
            if selector['description']:
                desc_elem = container.select_one(selector['description'])
                if desc_elem:
                    description = desc_elem.get_text(strip=True)[:500]  # Limit length
            
            if title:  # Only add if we have at least a title
                jobs.append({
                    'title': title,
                    'location': location,
                    'description': description,
                    'link': link
                })
        
        if jobs:  # If we found jobs with this pattern, stop trying
            break
    
    # If no jobs found with selectors, try a more aggressive approach
    if not jobs:
        # Look for headings that might be job titles
        headings = soup.find_all(['h2', 'h3', 'h4'])
        for heading in headings[:20]:  # Limit to avoid too many false positives
            text = heading.get_text(strip=True)
            # Filter out navigation/generic headings
            if len(text) > 10 and not any(word in text.lower() for word in ['about', 'contact', 'home', 'search', 'filter']):
                link = None
                link_elem = heading.find('a', href=True) or heading.find_parent('a', href=True)
                if link_elem:
                    link = urljoin(base_url, link_elem['href'])
                
                jobs.append({
                    'title': text,
                    'location': '',
                    'description': '',
                    'link': link
                })
    
    return jobs

def match_jobs(args: str) -> str:
    """Match jobs against user profile"""
    global USER_PROFILE, SCRAPED_JOBS
    
    if not USER_PROFILE:
        return "[WARNING] No profile set. Use 'profile' command first to set your skills and preferences."
    
    if not SCRAPED_JOBS:
        return "[WARNING] No jobs scraped yet. Use 'scrape' command to scrape career pages first."
    
    # Score each job
    scored_jobs = []
    for job in SCRAPED_JOBS:
        score = calculate_match_score(job, USER_PROFILE)
        scored_jobs.append((score, job))
    
    # Sort by score
    scored_jobs.sort(reverse=True, key=lambda x: x[0])
    
    # Format results
    result = f"Job Matches (found {len(scored_jobs)} jobs)\n\n"
    
    profile_summary = f"Your profile: {', '.join(USER_PROFILE.get('skills', []))}"
    if 'role' in USER_PROFILE:
        profile_summary += f" | Role: {USER_PROFILE['role']}"
    result += profile_summary + "\n\n"
    
    result += "=" * 60 + "\n\n"
    
    # Show top matches
    for i, (score, job) in enumerate(scored_jobs[:10], 1):
        match_level = "[EXCELLENT]" if score >= 70 else "[GOOD]" if score >= 50 else "[POSSIBLE]"
        
        result += f"{i}. {match_level} Match ({score}%)\n"
        result += f"   Title: {job['title']}\n"
        if job.get('location'):
            result += f"   Location: {job['location']}\n"
        if job.get('link'):
            result += f"   Link: {job['link']}\n"
        if job.get('description') and len(job['description']) > 20:
            result += f"   Description: {job['description'][:150]}...\n"
        result += "\n"
    
    if len(scored_jobs) > 10:
        result += f"\n... and {len(scored_jobs) - 10} more jobs\n"
    
    return result

def calculate_match_score(job, profile):
    """Calculate how well a job matches the profile"""
    score = 0
    max_score = 100
    
    # Combine job text for matching
    job_text = f"{job.get('title', '')} {job.get('description', '')} {job.get('location', '')}".lower()
    
    # Match skills (60% of score)
    skills = profile.get('skills', [])
    if skills:
        skill_score = 0
        for skill in skills:
            if skill.lower() in job_text:
                skill_score += 60 / len(skills)
        score += min(skill_score, 60)
    
    # Match role/title (30% of score)
    if 'role' in profile:
        role_keywords = profile['role'].lower().split()
        role_score = 0
        for keyword in role_keywords:
            if keyword in job_text:
                role_score += 30 / len(role_keywords)
        score += min(role_score, 30)
    
    # Match location preference (10% of score)
    if 'location' in profile and 'location' in job:
        if profile['location'].lower() in job['location'].lower():
            score += 10
    
    return int(score)

def list_jobs(args: str) -> str:
    """List all scraped jobs"""
    global SCRAPED_JOBS
    
    if not SCRAPED_JOBS:
        return "No jobs scraped yet. Use 'scrape <URL>' to scrape career pages."
    
    result = f"All Scraped Jobs ({len(SCRAPED_JOBS)} total)\n\n"
    
    for i, job in enumerate(SCRAPED_JOBS, 1):
        result += f"{i}. {job['title']}\n"
        if job.get('location'):
            result += f"   Location: {job['location']}\n"
        if job.get('link'):
            result += f"   Link: {job['link']}\n"
        result += "\n"
    
    return result
