import sys
import os
# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.profile_fetcher import ProfileFetcher
from datetime import datetime
import json

def main():
    try:
        # Configuration
        TOTAL_PROFILES = 100
        BATCH_SIZE = 15
        
        # Initialize the ProfileFetcher
        fetcher = ProfileFetcher()
        
        all_profiles = []
        last_timestamp = "2025-02-27T10:08:38.952694+00:00"  # Start from the most recent date
        seen_usernames = set()  # Track unique usernames
        
        while len(all_profiles) < TOTAL_PROFILES:
            # Fetch next batch
            batch = fetcher.get_profiles(
                date_column="created_at",
                before_date=last_timestamp,  # Changed to before_date to get older profiles
                limit=BATCH_SIZE
            )
            
            if not batch:
                print("No more profiles available")
                break
            
            # Filter out duplicates and add new profiles
            for profile in batch:
                if profile["username"] not in seen_usernames:
                    seen_usernames.add(profile["username"])
                    all_profiles.append(profile)
                    
            # Update the timestamp for the next iteration using the oldest profile in the batch
            last_timestamp = batch[-1]["created_at"]
            
            print(f"Fetched batch. Total unique profiles so far: {len(all_profiles)}")
            
            # Break if we've collected enough unique profiles
            if len(all_profiles) >= TOTAL_PROFILES:
                break
        
        # Trim to exact number if we got more than we needed
        all_profiles = all_profiles[:TOTAL_PROFILES]
        
        # Save all profiles to a JSON file
        output_file = "all_profiles.json"
        with open(output_file, 'w') as f:
            json.dump(all_profiles, f, indent=2)
            
        print(f"Successfully fetched {len(all_profiles)} unique profiles")
        print(f"Results saved to {output_file}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()