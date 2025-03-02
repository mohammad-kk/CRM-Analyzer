from typing import List, Optional, Dict, Any, Union
from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime

class ProfileFetcher:
    def __init__(self):
        """Initialize the ProfileFetcher with Supabase credentials."""
        load_dotenv()
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("Missing Supabase credentials in .env file")
        
        self.supabase = create_client(supabase_url, supabase_key)
    
    def get_profiles(self, 
                    select_columns: Optional[List[str]] = ["username", "full_name", "followers_count",'biography', "following_count", "created_at"],
                    filters: Optional[Dict[str, Any]] = None,
                    date_column: Optional[str] = None,
                    after_date: Optional[Union[str, datetime]] = None,
                    before_date: Optional[Union[str, datetime]] = None,
                    limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch profiles from Supabase with specified columns and filters.
        
        Args:
            select_columns (List[str], optional): List of columns to select. 
                                                If None, selects all columns.
            filters (Dict[str, Any], optional): Dictionary of filter conditions.
            date_column (str, optional): Name of the column to filter dates on (e.g., 'created_at').
            after_date (str or datetime, optional): Get records after this date.
            before_date (str or datetime, optional): Get records before this date.
            limit (int): Maximum number of records to return.
        
        Returns:
            List[Dict[str, Any]]: List of profile records.
        """
        query = self.supabase.table("profiles")
        
        # Select specific columns if provided
        if select_columns:
            columns = ",".join(select_columns)
            query = query.select(columns)
        else:
            query = query.select("*")
            
        # Apply regular filters if provided
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        
        # Apply date filters if provided
        if date_column:
            if after_date:
                if isinstance(after_date, datetime):
                    after_date = after_date.isoformat()
                query = query.gte(date_column, after_date)
            
            if before_date:
                if isinstance(before_date, datetime):
                    before_date = before_date.isoformat()
                query = query.lte(date_column, before_date)
                
        # Apply limit and order by date if date filtering is used
        if date_column:
            query = query.order(date_column, desc=True)
        query = query.limit(limit)
        
        response = query.execute()
        return response.data
    
    def get_profile_by_username(self, 
                              username: str,
                              select_columns: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """
        Fetch a specific profile by username.
        
        Args:
            username (str): Username to search for.
            select_columns (List[str], optional): List of columns to select.
        
        Returns:
            Optional[Dict[str, Any]]: Profile data if found, None otherwise.
        """
        profiles = self.get_profiles(
            select_columns=select_columns,
            filters={"username": username},
            limit=1
        )
        return profiles[0] if profiles else None
