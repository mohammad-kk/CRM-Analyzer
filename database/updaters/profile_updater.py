from datetime import datetime

class ProfileUpdater:
    def __init__(self, supabase_client):
        self.supabase = supabase_client

    def update_profiles_analysis(self, analyzed_profiles):
        """Update multiple profiles with analysis results"""
        results = []
        for profile in analyzed_profiles:
            result = self.update_single_profile(profile)
            results.append(result)
        return results

    def update_single_profile(self, profile_analysis):
        """Update a single profile with analysis results"""
        username = profile_analysis['username']
        
        try:
            profile = self._get_profile_by_username(username)
            if not profile:
                print(f"Profile not found for username: {username}")
                return False

            update_data = self._prepare_update_data(profile['id'], profile_analysis)
            success = self._execute_update(username, update_data)
            return success

        except Exception as e:
            print(f"Error processing profile {username}: {str(e)}")
            print(f"Full error details: {repr(e)}")
            return False

    def verify_updates(self, usernames):
        """Verify the update status of multiple profiles"""
        print("\nVerifying final state:")
        for username in usernames:
            try:
                result = self.supabase.table('profiles')\
                    .select('username, is_car_profile, profile_type')\
                    .eq('username', username)\
                    .execute()
                print(f"Current state for {username}:", result.data)
            except Exception as e:
                print(f"Error verifying {username}: {str(e)}")

    def _get_profile_by_username(self, username):
        """Get profile data by username"""
        result = self.supabase.table('profiles')\
            .select('id, username')\
            .eq('username', username)\
            .single()\
            .execute()
        return result.data

    def _prepare_update_data(self, profile_id, profile_analysis):
        """Prepare update data with proper type casting"""
        is_car = profile_analysis.get('is_car_profile', False)
        if isinstance(is_car, str):
            is_car = is_car.lower() == 'true'
            
        profile_type = profile_analysis.get('profile_type', 'unknown')
        if not profile_type:
            profile_type = 'unknown'
            
        return {
            'id': profile_id,
            'is_car_profile': bool(is_car),
            'profile_type': str(profile_type).lower(),
            'last_updated': datetime.now().isoformat()
        }

    def _execute_update(self, username, update_data):
        """Execute the update operation"""
        try:
            result = self.supabase.table('profiles')\
                .update(update_data)\
                .eq('id', update_data['id'])\
                .execute()
            
            if result.data:
                print(f"Successfully updated {username}")
                return True
            else:
                print(f"Update failed for {username} - Response: {result}")
                return False
                
        except Exception as update_error:
            print(f"Update error for {username}: {str(update_error)}")
            print(f"Error type: {type(update_error)}")
            return False