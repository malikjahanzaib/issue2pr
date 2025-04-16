#!/usr/bin/env python3
"""
GitHub Issue Analysis Script

This script analyzes GitHub issues and generates reports about:
- Issue distribution by label
- Average time to resolution
- Issue types and patterns
- Open vs. closed issue ratio
"""

import os
import json
import requests
from datetime import datetime
from collections import Counter
from typing import Dict, List, Tuple
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
REPO_OWNER = os.getenv('REPOSITORY').split('/')[0]
REPO_NAME = os.getenv('REPOSITORY').split('/')[1]
API_URL = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues'
HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

def get_issues() -> List[Dict]:
    """Fetch all issues from the repository."""
    try:
        response = requests.get(API_URL, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching issues: {str(e)}")
        raise

def analyze_issues(issues: List[Dict]) -> Tuple[Dict, float, Dict, float]:
    """
    Analyze GitHub issues and return statistics.
    
    Returns:
        Tuple containing:
        - Label counts
        - Average resolve time
        - Issue type distribution
        - Open vs. closed ratio
    """
    label_counts = Counter()
    resolve_times = []
    issue_types = Counter()
    open_count = 0
    closed_count = 0
    
    for issue in issues:
        # Count labels
        for label in issue['labels']:
            label_counts[label['name']] += 1
        
        # Determine issue type
        if 'bug' in [label['name'].lower() for label in issue['labels']]:
            issue_types['bug'] += 1
        elif 'enhancement' in [label['name'].lower() for label in issue['labels']]:
            issue_types['enhancement'] += 1
        elif 'question' in [label['name'].lower() for label in issue['labels']]:
            issue_types['question'] += 1
        else:
            issue_types['other'] += 1
        
        # Calculate resolution time
        if issue['closed_at']:
            closed_count += 1
            open_time = datetime.strptime(issue['created_at'], "%Y-%m-%dT%H:%M:%SZ")
            close_time = datetime.strptime(issue['closed_at'], "%Y-%m-%dT%H:%M:%SZ")
            resolve_times.append((close_time - open_time).days)
        else:
            open_count += 1
    
    avg_resolve_time = sum(resolve_times) / len(resolve_times) if resolve_times else 0
    total_issues = open_count + closed_count
    open_ratio = (open_count / total_issues) if total_issues > 0 else 0
    
    return label_counts, avg_resolve_time, issue_types, open_ratio

def generate_report() -> None:
    """Generate and save the analysis report."""
    try:
        issues = get_issues()
        label_counts, avg_resolve_time, issue_types, open_ratio = analyze_issues(issues)
        
        # Create report
        report = {
            'label_counts': dict(label_counts),
            'average_resolve_time': avg_resolve_time,
            'issue_types': dict(issue_types),
            'open_ratio': open_ratio,
            'total_issues': len(issues),
            'generated_at': datetime.now().isoformat()
        }
        
        # Print report
        print('\nGitHub Issue Analysis Report')
        print('=' * 30)
        print(f'Total Issues: {len(issues)}')
        print(f'Open Issues Ratio: {open_ratio:.2%}')
        print(f'Average Resolution Time: {avg_resolve_time:.1f} days')
        
        print('\nLabel Distribution:')
        for label, count in label_counts.most_common():
            print(f'  - {label}: {count}')
        
        print('\nIssue Types:')
        for issue_type, count in issue_types.most_common():
            print(f'  - {issue_type}: {count}')
        
        # Save report
        with open('issue_analysis_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info('Report generated successfully')
        
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise

if __name__ == "__main__":
    generate_report() 