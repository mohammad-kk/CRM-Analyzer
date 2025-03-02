from google import genai

import asyncio
import os
import json
from dotenv import load_dotenv
from gemini.geminihandler import geminiHandler
from profile_fetcher import ProfileFetcher
from updaters.profile_updater import ProfileUpdater
from datetime import datetime

def main():
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')
    
    # Initialize components
    fetcher = ProfileFetcher()
    updater = ProfileUpdater(fetcher.supabase)
    
    # Get profiles and analyze them
    profiles = get_and_analyze_profiles(fetcher, api_key)
    
    # Update profiles with analysis results
    updater.update_profiles_analysis(profiles['profiles'])
    
    # Verify updates
    usernames = [p['username'] for p in profiles['profiles']]
    updater.verify_updates(usernames)
    
    print("Analysis completed and database updated")

def get_and_analyze_profiles(fetcher, api_key):
    """Fetch and analyze profiles using Gemini"""
    # Get profiles
    target_date = datetime(2025, 2, 22)
    profiles = fetcher.get_profiles(
        date_column="created_at",
        after_date=target_date,
        limit=5
    )
    
    # Initialize Gemini handler
    model = 'gemini-2.0-flash'
    base_prompt = '''Respond with a structured json output (without any markdown formatting or ```json prefix), listing out username, 
    whether the profile can be determined to be a car profile or car centric, 
    whether the profile is an individual or a business profile, amount of followers'''
    
    gemini_handler = geminiHandler(model, base_prompt, api_key)
    
    # Analyze profiles
    gemini_handler.update_data("profiles", json.dumps(profiles, indent=2))
    response = clean_gemini_response(gemini_handler.send_prompt())
    
    # Save and return analysis
    save_analysis(response)
    return json.loads(response)

def clean_gemini_response(response):
    """Clean the Gemini response"""
    cleaned = response.strip()
    if cleaned.startswith('```json'):
        cleaned = cleaned[7:]
    if cleaned.endswith('```'):
        cleaned = cleaned[:-3]
    return cleaned.strip()

def save_analysis(response, output_file="gemini_analysis.json"):
    """Save the analysis to a file"""
    with open(output_file, 'w') as f:
        f.write(response)

if __name__ == "__main__":
    main()
