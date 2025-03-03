from google import genai

import asyncio
import os
import json
import time  # Add time import for sleep
from dotenv import load_dotenv
from gemini.geminihandler import geminiHandler
from profile_fetcher import ProfileFetcher
from updaters.profile_updater import ProfileUpdater
from datetime import datetime

def clean_gemini_response(response):
    """Clean the Gemini response by removing markdown formatting"""
    cleaned = response.strip()
    if cleaned.startswith('```json'):
        cleaned = cleaned[7:]
    if cleaned.endswith('```'):
        cleaned = cleaned[:-3]
    return cleaned.strip()

def process_profiles_in_batches(fetcher, updater, api_key, batch_size=35, process_size=35, max_retries=1, retry_delay=60):
    """Process profiles in batches with Gemini analysis"""
    while True:
        # Fetch unprocessed profiles
        profiles = fetcher.get_unprocessed_profiles(batch_size)
        
        if not profiles:
            print("No more unprocessed profiles found.")
            break
            
        print(f"Processing batch of {len(profiles)} profiles...")
        
        # Process profiles in smaller chunks
        for i in range(0, len(profiles), process_size):
            chunk = profiles[i:i + process_size]
            retries = 0
            
            while retries < max_retries:
                try:
                    # Initialize Gemini handler
                    model = 'gemini-2.0-flash'
                    base_prompt = '''Analyze the following profiles and respond with a JSON array where each object has:
                    - "username": the profile's username
                    - "is_car_profile": boolean indicating if the profile is car-related
                    - "profile_type": either "Individual", "Company", "Car Page", or "unknown"
                    Format the response as a JSON array without any markdown formatting.'''
                    
                    gemini_handler = geminiHandler(model, base_prompt, api_key)
                    
                    # Analyze profiles
                    gemini_handler.update_data("profiles", json.dumps(chunk, indent=2))
                    response = clean_gemini_response(gemini_handler.send_prompt())
                    
                    if "quota exceeded" in response.lower() or "rate limit" in response.lower():
                        print(f"API limit reached. Waiting {retry_delay} seconds before retry...")
                        time.sleep(retry_delay)
                        retries += 1
                        continue
                    
                    # Parse and process results
                    profiles_array = json.loads(response)
                    if not isinstance(profiles_array, list):
                        print(f"Unexpected response format: {response}")
                        break
                    
                    # Update profiles with analysis results
                    updater.update_profiles_analysis(profiles_array)
                    print(f"Processed {len(chunk)} profiles successfully")
                    
                    # Add a small delay to avoid rate limiting
                    time.sleep(1)
                    break  # Success, exit retry loop
                    
                except Exception as e:
                    print(f"Error processing chunk: {str(e)}")
                    print(f"Response was: {response}")
                    retries += 1
                    if retries < max_retries:
                        print(f"Retrying in {retry_delay} seconds... (Attempt {retries + 1}/{max_retries})")
                        time.sleep(retry_delay)
                    else:
                        print("Max retries reached for this chunk, moving to next chunk")
                        continue

def main():
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')
    
    # Initialize components
    fetcher = ProfileFetcher()
    updater = ProfileUpdater(fetcher.supabase)
    
    # Process profiles in batches
    process_profiles_in_batches(fetcher, updater, api_key)
    
    print("Analysis completed and database updated")

if __name__ == "__main__":
    main()
