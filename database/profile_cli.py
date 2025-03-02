#!/usr/bin/env python3
from profile_fetcher import ProfileFetcher
from datetime import datetime
import argparse
import json
from typing import Dict, Any

def format_profile_data(profile: Dict[str, Any]) -> str:
    """Format profile data in a readable way."""
    output = []
    output.append("=" * 60)
    output.append(f"Username: {profile.get('username', 'N/A')}")
    output.append(f"Full Name: {profile.get('full_name', 'N/A')}")
    output.append(f"Biography: {profile.get('biography', 'N/A')}")
    output.append(f"Followers: {profile.get('followers_count', 0):,}")
    output.append(f"Following: {profile.get('following_count', 0):,}")
    output.append(f"Verified: {'✓' if profile.get('is_verified') else '✗'}")
    
    # Format profile_data if it exists
    if profile.get('profile_data'):
        output.append("\nProfile Data:")
        try:
            # Try to format as JSON if it's a dictionary
            if isinstance(profile['profile_data'], dict):
                formatted_data = json.dumps(profile['profile_data'], indent=2)
            else:
                formatted_data = str(profile['profile_data'])
            output.append(formatted_data)
        except Exception:
            output.append(str(profile['profile_data']))
    
    output.append("=" * 60)
    return "\n".join(output)

def main():
    parser = argparse.ArgumentParser(description='Query Instagram profiles from the database')
    parser.add_argument('--username', help='Specific username to look up')
    parser.add_argument('--after-date', help='Get profiles created after this date (YYYY-MM-DD)')
    parser.add_argument('--before-date', help='Get profiles created before this date (YYYY-MM-DD)')
    parser.add_argument('--verified-only', action='store_true', help='Show only verified profiles')
    parser.add_argument('--min-followers', type=int, help='Minimum number of followers')
    parser.add_argument('--limit', type=int, default=10, help='Maximum number of profiles to return')
    
    args = parser.parse_args()
    
    # Initialize the profile fetcher
    fetcher = ProfileFetcher()
    
    try:
        # Define columns we want to fetch
        columns = [
            "username",
            "full_name",
            "biography",
            "profile_data",
            "followers_count",
            "following_count",
            "is_verified",
            "created_at"
        ]
        
        # Build filters
        filters = {}
        if args.username:
            filters["username"] = args.username
        if args.verified_only:
            filters["is_verified"] = True
            
        # Get profiles
        profiles = fetcher.get_profiles(
            select_columns=columns,
            filters=filters,
            date_column="created_at" if args.after_date or args.before_date else None,
            after_date=args.after_date,
            before_date=args.before_date,
            limit=args.limit
        )
        
        # Filter by minimum followers if specified
        if args.min_followers:
            profiles = [p for p in profiles if p.get('followers_count', 0) >= args.min_followers]
        
        # Display results
        if not profiles:
            print("No profiles found matching the criteria.")
            return
        
        print(f"\nFound {len(profiles)} matching profiles:")
        for profile in profiles:
            print(format_profile_data(profile))
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
