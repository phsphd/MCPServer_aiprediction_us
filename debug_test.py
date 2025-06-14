#!/usr/bin/env python3
"""
Debug script to test the AI Prediction API directly
"""

import asyncio
import json
import os
from datetime import datetime
import aiohttp

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("📁 .env file loaded")
except ImportError:
    print("⚠️  python-dotenv not installed")

# API configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'https://aiprediction.us')
API_USERNAME = os.getenv('API_USERNAME', '')
API_PASSWORD = os.getenv('API_PASSWORD', '')

async def test_api():
    """Test the API step by step"""
    
    print(f"🔧 Testing API: {API_BASE_URL}")
    print(f"🔧 Username: {API_USERNAME}")
    print(f"🔧 Password: {'*' * len(API_PASSWORD) if API_PASSWORD else 'NOT SET'}")
    print()
    
    async with aiohttp.ClientSession() as session:
        
        # Step 1: Test authentication
        print("🔐 Step 1: Testing Authentication")
        auth_url = f"{API_BASE_URL}/api-token-auth/"
        auth_data = {
            'username': API_USERNAME,
            'password': API_PASSWORD
        }
        
        try:
            async with session.post(auth_url, json=auth_data) as response:
                auth_response_text = await response.text()
                print(f"   Status: {response.status}")
                print(f"   Response: {auth_response_text}")
                
                if response.status == 200:
                    auth_data = json.loads(auth_response_text)
                    token = auth_data.get('token')
                    print(f"   ✅ Token: {token[:20]}..." if token else "   ❌ No token")
                else:
                    print(f"   ❌ Authentication failed")
                    return
        except Exception as e:
            print(f"   ❌ Auth error: {e}")
            return
        
        print()
        
        # Step 2: Test data retrieval with different dates
        print("📊 Step 2: Testing Data Retrieval")
        headers = {'Authorization': f'Token {token}'}
        
        # Try today's date
        current_date = datetime.now().strftime('%y%m%d')
        print(f"   Testing current date: {current_date}")
        
        data_url = f"{API_BASE_URL}/api/v53a/{current_date}/last-elements/"
        print(f"   URL: {data_url}")
        
        try:
            async with session.get(data_url, headers=headers) as response:
                data_response_text = await response.text()
                print(f"   Status: {response.status}")
                
                if response.status == 200:
                    try:
                        data = json.loads(data_response_text)
                        print(f"   ✅ Data retrieved successfully")
                        print(f"   📋 Full response structure:")
                        print(json.dumps(data, indent=4, default=str))
                        
                        # Analyze the last_elements
                        last_elements = data.get('last_elements', {})
                        if last_elements:
                            print(f"\n   🔍 Last Elements Analysis:")
                            non_null_count = 0
                            null_count = 0
                            
                            for field, value in last_elements.items():
                                if value is not None:
                                    non_null_count += 1
                                    print(f"     {field}: {value} ✅")
                                else:
                                    null_count += 1
                                    print(f"     {field}: None ❌")
                            
                            print(f"\n   📈 Summary:")
                            print(f"     Non-null fields: {non_null_count}")
                            print(f"     Null fields: {null_count}")
                            print(f"     Total fields: {len(last_elements)}")
                        
                    except json.JSONDecodeError as e:
                        print(f"   ❌ Could not parse JSON: {e}")
                        print(f"   Raw response: {data_response_text}")
                else:
                    print(f"   ❌ Data request failed: {data_response_text}")
        except Exception as e:
            print(f"   ❌ Data request error: {e}")
        
        print()
        
        # Step 3: Try a few different dates
        print("📅 Step 3: Testing Different Dates")
        test_dates = [
            '250612',  # Yesterday
            '250611',  # Day before
            '250610',  # 3 days ago
            '250609',  # 4 days ago (Monday)
            '250606',  # Last Friday
        ]
        
        for test_date in test_dates:
            print(f"   Testing date: {test_date}")
            test_url = f"{API_BASE_URL}/api/v53a/{test_date}/last-elements/"
            
            try:
                async with session.get(test_url, headers=headers) as response:
                    if response.status == 200:
                        test_data = await response.json()
                        last_elements = test_data.get('last_elements', {})
                        non_null = sum(1 for v in last_elements.values() if v is not None)
                        total = len(last_elements)
                        print(f"     ✅ {non_null}/{total} fields have data")
                        
                        # Show first non-null field as example
                        for field, value in last_elements.items():
                            if value is not None:
                                print(f"     Example: {field} = {value}")
                                break
                    else:
                        response_text = await response.text()
                        print(f"     ❌ Status {response.status}: {response_text}")
            except Exception as e:
                print(f"     ❌ Error: {e}")
        
        print()
        
        # Step 4: Test debug endpoint
        print("🐛 Step 4: Testing Debug Endpoint")
        debug_url = f"{API_BASE_URL}/api/debug/v53a/general/"
        
        try:
            async with session.get(debug_url, headers=headers) as response:
                if response.status == 200:
                    debug_data = await response.json()
                    print(f"   ✅ Debug info retrieved")
                    print(json.dumps(debug_data, indent=4, default=str))
                else:
                    debug_text = await response.text()
                    print(f"   ❌ Debug failed: {debug_text}")
        except Exception as e:
            print(f"   ❌ Debug error: {e}")

if __name__ == "__main__":
    asyncio.run(test_api())