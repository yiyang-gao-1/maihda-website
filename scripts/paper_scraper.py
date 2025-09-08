#!/usr/bin/env python
"""
MAIHDA Paper Scraper
Automatically fetches papers from Google Scholar and other sources
"""

import json
import time
import pandas as pd
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, List
import hashlib

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from scholarly import scholarly
    SCHOLARLY_AVAILABLE = True
except ImportError:
    SCHOLARLY_AVAILABLE = False
    logger.warning("Scholarly not available. Google Scholar scraping disabled.")

class MAIDHAPaperScraper:
    def __init__(self, data_dir="content/data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.papers_file = self.data_dir / "papers.json"
        self.categories_file = self.data_dir / "categories.json"
        self.papers = self.load_existing_papers()
        
    def load_existing_papers(self) -> Dict:
        """Load existing papers from JSON file"""
        if self.papers_file.exists():
            with open(self.papers_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_papers(self):
        """Save papers to JSON file"""
        with open(self.papers_file, 'w', encoding='utf-8') as f:
            json.dump(self.papers, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(self.papers)} papers to {self.papers_file}")
    
    def generate_paper_id(self, title: str, authors: str) -> str:
        """Generate unique ID for paper"""
        content = f"{title}_{authors}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def scrape_google_scholar(self, query: str = "MAIHDA", max_results: int = 100):
        """Scrape papers from Google Scholar"""
        if not SCHOLARLY_AVAILABLE:
            logger.error("Scholarly library not available")
            return
        
        logger.info(f"Searching Google Scholar for: {query}")
        
        try:
            search_query = scholarly.search_pubs(query)
            
            for i, result in enumerate(search_query):
                if i >= max_results:
                    break
                
                # Extract paper information
                paper_info = {
                    'title': result.get('bib', {}).get('title', ''),
                    'authors': ', '.join(result.get('bib', {}).get('author', [])),
                    'year': result.get('bib', {}).get('pub_year', ''),
                    'journal': result.get('bib', {}).get('venue', ''),
                    'abstract': result.get('bib', {}).get('abstract', ''),
                    'citations': result.get('num_citations', 0),
                    'url': result.get('pub_url', ''),
                    'eprint_url': result.get('eprint_url', ''),
                    'scraped_date': datetime.now().isoformat(),
                    'source': 'google_scholar',
                    'categories': [],
                    'verified': False
                }
                
                # Generate unique ID
                paper_id = self.generate_paper_id(paper_info['title'], paper_info['authors'])
                
                # Check if paper already exists
                if paper_id not in self.papers:
                    self.papers[paper_id] = paper_info
                    logger.info(f"Added new paper: {paper_info['title'][:50]}...")
                
                # Be respectful to Google Scholar
                time.sleep(2)
                
        except Exception as e:
            logger.error(f"Error scraping Google Scholar: {e}")
    
    def categorize_papers(self):
        """Auto-categorize papers based on keywords"""
        categories = {
            'introduction': ['introduction', 'tutorial', 'methodology', 'framework', 'review'],
            'public_health': ['health', 'disease', 'mortality', 'morbidity', 'epidemiology'],
            'education': ['education', 'school', 'achievement', 'student', 'learning'],
            'spatial': ['spatial', 'geographic', 'neighborhood', 'area', 'region'],
            'longitudinal': ['longitudinal', 'temporal', 'time', 'trajectory', 'panel'],
            'bayesian': ['bayesian', 'MCMC', 'prior', 'posterior'],
        }
        
        for paper_id, paper in self.papers.items():
            if not paper['categories']:  # Only categorize if not already done
                paper_text = (paper['title'] + ' ' + paper['abstract']).lower()
                
                for category, keywords in categories.items():
                    if any(keyword in paper_text for keyword in keywords):
                        paper['categories'].append(category)
                
                # If no category matched, mark as uncategorized
                if not paper['categories']:
                    paper['categories'].append('uncategorized')
    
    def export_to_markdown(self):
        """Export papers to Markdown files for Pelican"""
        papers_dir = Path("content/papers")
        papers_dir.mkdir(exist_ok=True)
        
        # Group papers by category
        papers_by_category = {}
        for paper_id, paper in self.papers.items():
            for category in paper.get('categories', ['uncategorized']):
                if category not in papers_by_category:
                    papers_by_category[category] = []
                papers_by_category[category].append(paper)
        
        # Create markdown file for each category
        for category, papers in papers_by_category.items():
            md_content = f"""Title: {category.replace('_', ' ').title()} Papers
Date: {datetime.now().strftime('%Y-%m-%d')}
Category: Papers
Tags: maihda, {category}
Slug: {category}-papers

## {category.replace('_', ' ').title()} MAIHDA Papers

"""
            # Sort papers by year (newest first)
            papers.sort(key=lambda x: x.get('year', '0'), reverse=True)
            
            for paper in papers:
                md_content += f"""
### {paper['title']}

**Authors:** {paper['authors']}  
**Year:** {paper['year']}  
**Journal:** {paper['journal']}  
**Citations:** {paper['citations']}  

{paper['abstract'][:300]}...

[Read more]({paper['url']})

---
"""
            
            # Save markdown file
            md_file = papers_dir / f"{category}.md"
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            logger.info(f"Created {md_file} with {len(papers)} papers")
    
    def create_statistics(self):
        """Generate statistics about the papers"""
        stats = {
            'total_papers': len(self.papers),
            'papers_by_year': {},
            'papers_by_category': {},
            'top_cited': [],
            'last_updated': datetime.now().isoformat()
        }
        
        for paper in self.papers.values():
            # Count by year
            year = paper.get('year', 'Unknown')
            stats['papers_by_year'][year] = stats['papers_by_year'].get(year, 0) + 1
            
            # Count by category
            for category in paper.get('categories', ['uncategorized']):
                stats['papers_by_category'][category] = stats['papers_by_category'].get(category, 0) + 1
        
        # Get top 10 cited papers
        sorted_papers = sorted(self.papers.values(), 
                             key=lambda x: x.get('citations', 0), 
                             reverse=True)
        stats['top_cited'] = [
            {'title': p['title'], 'citations': p['citations']} 
            for p in sorted_papers[:10]
        ]
        
        # Save statistics
        stats_file = self.data_dir / "statistics.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)
        
        logger.info(f"Generated statistics: {stats['total_papers']} total papers")
        return stats

def main():
    """Main function to run the scraper"""
    scraper = MAIDHAPaperScraper()
    
    # Search for different MAIHDA-related terms
    search_terms = [
        "MAIHDA",
        "Multilevel Analysis Individual Heterogeneity Discriminatory Accuracy",
        "MAIHDA intersectionality",
        "MAIHDA health",
        "MAIHDA education"
    ]
    
    for term in search_terms:
        logger.info(f"Searching for: {term}")
        scraper.scrape_google_scholar(term, max_results=20)
        time.sleep(10)  # Be respectful between searches
    
    # Categorize papers
    scraper.categorize_papers()
    
    # Save data
    scraper.save_papers()
    
    # Export to markdown
    scraper.export_to_markdown()
    
    # Generate statistics
    scraper.create_statistics()
    
    logger.info("Scraping completed successfully!")

if __name__ == "__main__":
    main()

