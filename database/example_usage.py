from profile_fetcher import ProfileFetcher
from datetime import datetime

def main():
    # Initialize the profile fetcher
    fetcher = ProfileFetcher()
    
    try:
        # Get profiles created after February 25, 2025
        selected_columns = ["username", "full_name", "followers_count", "following_count", "created_at"]
        after_date = "2025-02-22T00:00:00"
        
        profiles = fetcher.get_profiles(
            select_columns=selected_columns,
            date_column="created_at",
            after_date=after_date,
            limit=10
        )
        
        print(f"\nProfiles created after {after_date}:")
        for profile in profiles:
            print(f"Username: {profile['username']}")
            print(f"Full Name: {profile['full_name']}")
            print(f"Followers: {profile['followers_count']}")
            print(f"Following: {profile['following_count']}")
            print(f"Created At: {profile['created_at']}")
            print("-" * 50)
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()


