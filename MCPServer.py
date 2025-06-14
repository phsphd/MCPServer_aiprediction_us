#!/usr/bin/env python3
"""
MCP Server for AI Prediction API with authentication and date handling
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
)

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("📁 .env file loaded successfully")
except ImportError:
    print("⚠️  python-dotenv not installed, using system environment variables only")
except Exception as e:
    print(f"⚠️  Could not load .env file: {e}")

# API configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'https://aiprediction.us')
API_USERNAME = os.getenv('API_USERNAME', '')
API_PASSWORD = os.getenv('API_PASSWORD', '')

class AIPredictionMCPServer:
    def __init__(self):
        self.server = Server("aiprediction-mcp-server")
        self.session = None
        self.auth_token = None
        
    async def init_session(self):
        """Initialize HTTP session and test authentication"""
        self.session = aiohttp.ClientSession()
        
        # Test authentication on startup
        print(f"🚀 Starting AI Prediction MCP Server", flush=True)
        print(f"🌐 API Base URL: {API_BASE_URL}", flush=True)
        
        if not API_USERNAME or not API_PASSWORD:
            print(f"❌ Missing credentials!", flush=True)
            print(f"❌ API_USERNAME: {'SET' if API_USERNAME else 'NOT SET'}", flush=True)
            print(f"❌ API_PASSWORD: {'SET' if API_PASSWORD else 'NOT SET'}", flush=True)
            return
        
        # Test authentication
        auth_success = await self.authenticate()
        
        if auth_success:
            # Test getting today's data
            print(f"\n📊 Testing data retrieval...", flush=True)
            try:
                current_date = self.get_current_date_yymmdd()
                print(f"📅 Today's date in YYMMDD format: {current_date}", flush=True)
                
                data = await self.get_last_elements(current_date)
                print(f"✅ Successfully retrieved data for {current_date}", flush=True)
                
                print(f"🔍 Sample data structure:", flush=True)
                print(f"   - DID: {data.get('DID')}", flush=True)
                print(f"   - ID: {data.get('ID')}", flush=True)
                print(f"   - Last update time: {data.get('last_ctime')}", flush=True)
                print(f"   - Lookup method: {data.get('lookup_method')}", flush=True)
                
                # Show sample of last elements
                last_elements = data.get('last_elements', {})
                if last_elements:
                    print(f"📈 Last elements sample:", flush=True)
                    sample_count = 0
                    for field, value in last_elements.items():
                        if sample_count < 3:
                            print(f"   - {field}: {value}", flush=True)
                            sample_count += 1
                        else:
                            break
                    
                    remaining = len(last_elements) - sample_count
                    if remaining > 0:
                        print(f"   ... and {remaining} more fields", flush=True)
                else:
                    print(f"⚠️  No last_elements data found", flush=True)
                    
            except Exception as e:
                print(f"⚠️  Could not retrieve today's data: {str(e)}", flush=True)
                print(f"   This might be normal if no data exists for {current_date}", flush=True)
        else:
            print(f"❌ Authentication failed - MCP server will not work properly", flush=True)
            
        print(f"\n🎯 MCP Server ready for connections", flush=True)
        
    async def close_session(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()

    async def authenticate(self) -> bool:
        """Authenticate and get token"""
        auth_url = f"{API_BASE_URL}/api-token-auth/"
        
        auth_data = {
            'username': API_USERNAME,
            'password': API_PASSWORD
        }
        
        print(f"🔐 Attempting authentication with URL: {auth_url}")
        print(f"🔐 Username: {API_USERNAME}")
        print(f"🔐 Password: {'*' * len(API_PASSWORD) if API_PASSWORD else 'NOT SET'}")
        
        try:
            async with self.session.post(auth_url, json=auth_data) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    try:
                        data = json.loads(response_text)
                        self.auth_token = data.get('token')
                        
                        print(f"✅ Authentication successful!")
                        print(f"✅ Token received: {self.auth_token[:20]}..." if self.auth_token else "❌ No token in response")
                        print(f"✅ User ID: {data.get('user_id')}")
                        print(f"✅ Username: {data.get('username')}")
                        print(f"✅ Is Member: {data.get('is_member')}")
                        print(f"✅ Token expires: {data.get('expires_at')}")
                        
                        return True
                    except json.JSONDecodeError as e:
                        print(f"❌ Authentication failed: Could not parse JSON response")
                        print(f"❌ Response text: {response_text}")
                        return False
                else:
                    print(f"❌ Authentication failed with status {response.status}")
                    print(f"❌ Response headers: {dict(response.headers)}")
                    print(f"❌ Response text: {response_text}")
                    
                    # Try to parse error details if JSON
                    try:
                        error_data = json.loads(response_text)
                        print(f"❌ Error details: {error_data}")
                    except json.JSONDecodeError:
                        print(f"❌ Raw error response: {response_text}")
                    
                    return False
                    
        except aiohttp.ClientError as e:
            print(f"❌ Network error during authentication: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ Unexpected authentication error: {str(e)}")
            print(f"❌ Error type: {type(e).__name__}")
            return False

    async def call_api(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make authenticated API call"""
        # Ensure we have a valid token
        if not self.auth_token:
            print(f"🔑 No auth token, attempting authentication...")
            if not await self.authenticate():
                raise Exception("Failed to authenticate")
        
        url = f"{API_BASE_URL.rstrip('/')}{endpoint}"
        headers = {'Authorization': f'Token {self.auth_token}'}
        
        print(f"🌐 Making API call to: {url}")
        
        async with self.session.get(url, headers=headers, params=params) as response:
            response_text = await response.text()
            
            if response.status == 401:
                print(f"🔄 Token expired (401), attempting re-authentication...")
                # Token might be expired, try to re-authenticate
                if await self.authenticate():
                    headers = {'Authorization': f'Token {self.auth_token}'}
                    async with self.session.get(url, headers=headers, params=params) as retry_response:
                        if retry_response.status == 200:
                            result = await retry_response.json()
                            print(f"✅ API call successful after re-authentication")
                            return result
                        else:
                            error_text = await retry_response.text()
                            print(f"❌ API call failed even after re-auth: {retry_response.status} - {error_text}")
                            raise Exception(f"API call failed after re-auth: {retry_response.status} - {error_text}")
                else:
                    print(f"❌ Re-authentication failed")
                    raise Exception("Re-authentication failed")
            elif response.status == 200:
                try:
                    result = await response.json()
                    print(f"✅ API call successful")
                    return result
                except json.JSONDecodeError as e:
                    print(f"❌ Could not parse JSON response: {e}")
                    print(f"❌ Raw response: {response_text}")
                    raise Exception(f"Invalid JSON response: {e}")
            else:
                print(f"❌ API call failed with status {response.status}")
                print(f"❌ Response: {response_text}")
                raise Exception(f"API call failed: {response.status} - {response_text}")

    def get_current_date_yymmdd(self) -> str:
        """Get current date in YYMMDD format"""
        return datetime.now().strftime('%y%m%d')
    
    def get_date_yymmdd(self, year: int = None, month: int = None, day: int = None) -> str:
        """Get specific date in YYMMDD format"""
        if year is None or month is None or day is None:
            return self.get_current_date_yymmdd()
        
        # Handle 2-digit or 4-digit year
        if year > 50 and year < 100:
            # Assume 19xx for years 51-99
            full_year = 1900 + year
        elif year < 50:
            # Assume 20xx for years 00-49
            full_year = 2000 + year
        elif year > 2000:
            # Already a full year
            full_year = year
        else:
            full_year = year
            
        date_obj = datetime(full_year, month, day)
        return date_obj.strftime('%y%m%d')

    async def get_last_elements(self, did: str) -> Dict[str, Any]:
        """Get last elements for a specific DID"""
        endpoint = f"/api/v53a/{did}/last-elements/"
        return await self.call_api(endpoint)

    async def get_debug_info(self) -> Dict[str, Any]:
        """Get debug information about the V53a model"""
        endpoint = "/api/debug/v53a/general/"
        return await self.call_api(endpoint)

    def setup_handlers(self):
        """Set up MCP handlers"""
        
        @self.server.list_resources()
        async def handle_list_resources() -> List[Resource]:
            """List available resources"""
            current_date = self.get_current_date_yymmdd()
            return [
                Resource(
                    uri=f"aiprediction://current-date",
                    name="Current Date Data",
                    description=f"Last elements for current date ({current_date})",
                    mimeType="application/json",
                ),
                Resource(
                    uri=f"aiprediction://debug-info",
                    name="API Debug Info",
                    description="Debug information about the V53a model",
                    mimeType="application/json",
                ),
            ]

        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Read resource content"""
            if uri == "aiprediction://current-date":
                current_date = self.get_current_date_yymmdd()
                try:
                    data = await self.get_last_elements(current_date)
                    return json.dumps(data, indent=2, default=str)
                except Exception as e:
                    return json.dumps({"error": f"Failed to get current date data: {str(e)}"}, indent=2)
            elif uri == "aiprediction://debug-info":
                try:
                    data = await self.get_debug_info()
                    return json.dumps(data, indent=2, default=str)
                except Exception as e:
                    return json.dumps({"error": f"Failed to get debug info: {str(e)}"}, indent=2)
            else:
                raise ValueError(f"Unknown resource: {uri}")

        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools"""
            return [
                Tool(
                    name="get_last_elements_by_date",
                    description="Get last elements for a specific date (YYMMDD format)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "date": {
                                "type": "string",
                                "description": "Date in YYMMDD format (e.g., '241213' for Dec 13, 2024). Leave empty for current date.",
                                "pattern": "^[0-9]{6}$"
                            },
                            "year": {
                                "type": "integer",
                                "description": "Year (2024, 24, etc.) - alternative to date parameter"
                            },
                            "month": {
                                "type": "integer",
                                "description": "Month (1-12) - use with year and day"
                            },
                            "day": {
                                "type": "integer", 
                                "description": "Day (1-31) - use with year and month"
                            }
                        }
                    }
                ),
                Tool(
                    name="get_current_date_data",
                    description="Get last elements for today's date",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="get_api_debug_info",
                    description="Get debug information about the API and V53a model",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="format_date_yymmdd",
                    description="Convert a date to YYMMDD format",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "year": {
                                "type": "integer",
                                "description": "Year (e.g., 2024, 24)"
                            },
                            "month": {
                                "type": "integer",
                                "description": "Month (1-12)"
                            },
                            "day": {
                                "type": "integer",
                                "description": "Day (1-31)"
                            }
                        },
                        "required": ["year", "month", "day"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls"""
            try:
                if name == "get_last_elements_by_date":
                    date_str = arguments.get("date")
                    year = arguments.get("year")
                    month = arguments.get("month")
                    day = arguments.get("day")
                    
                    if date_str:
                        # Use provided date string
                        did = date_str
                    elif year is not None and month is not None and day is not None:
                        # Convert year/month/day to YYMMDD
                        did = self.get_date_yymmdd(year, month, day)
                    else:
                        # Use current date
                        did = self.get_current_date_yymmdd()
                    
                    data = await self.get_last_elements(did)
                    result = {
                        "requested_date": did,
                        "data": data
                    }
                    
                    return [TextContent(
                        type="text",
                        text=json.dumps(result, indent=2, default=str)
                    )]
                    
                elif name == "get_current_date_data":
                    current_date = self.get_current_date_yymmdd()
                    data = await self.get_last_elements(current_date)
                    result = {
                        "current_date": current_date,
                        "data": data
                    }
                    
                    return [TextContent(
                        type="text",
                        text=json.dumps(result, indent=2, default=str)
                    )]
                    
                elif name == "get_api_debug_info":
                    data = await self.get_debug_info()
                    
                    return [TextContent(
                        type="text",
                        text=json.dumps(data, indent=2, default=str)
                    )]
                    
                elif name == "format_date_yymmdd":
                    year = arguments.get("year")
                    month = arguments.get("month") 
                    day = arguments.get("day")
                    
                    formatted_date = self.get_date_yymmdd(year, month, day)
                    result = {
                        "input": {"year": year, "month": month, "day": day},
                        "formatted_date": formatted_date
                    }
                    
                    return [TextContent(
                        type="text",
                        text=json.dumps(result, indent=2)
                    )]
                    
                else:
                    raise ValueError(f"Unknown tool: {name}")
                    
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]

async def main():
    """Main entry point"""
    mcp_server = AIPredictionMCPServer()
    
    # Initialize HTTP session
    await mcp_server.init_session()
    
    # Set up handlers
    mcp_server.setup_handlers()
    
    try:
        # Run the server
        async with stdio_server() as (read_stream, write_stream):
            await mcp_server.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="aiprediction-mcp-server",
                    server_version="1.0.0",
                    capabilities=mcp_server.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
    finally:
        await mcp_server.close_session()

if __name__ == "__main__":
    asyncio.run(main())