# AI Prediction MCP Server

A Model Context Protocol (MCP) server that provides Claude with access to AI prediction data from the aiprediction.us API. This server handles authentication, date formatting, and data retrieval to give Claude seamless access to trading predictions and analysis.

## 🚀 Features

- **Automatic Authentication**: Handles token-based authentication with the AI Prediction API
- **Date Management**: Converts dates to YYMMDD format and gets current date automatically
- **Real-time Data**: Retrieves last elements data for any date
- **Error Handling**: Comprehensive logging and error recovery
- **Token Management**: Automatic token refresh when expired

## 📋 Prerequisites

- Python 3.8 or higher
- Active account on aiprediction.us
- Claude Desktop (or another MCP-compatible client)

## 🛠️ Installation

### 1. Clone or Download Files

Download these files to your project directory:
- `MCPServer.py` (the main MCP server)
- `requirements.txt` (Python dependencies)
- `.env.example` (environment configuration template)

### 2. Set Up Python Environment

#### Option A: Using venv (Recommended)
```bash
# Create virtual environment
python -m venv aiprediction-mcp
cd aiprediction-mcp

# Activate virtual environment
# On Windows:
Scripts\activate
# On macOS/Linux:
source bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Option B: Using conda
```bash
# Create conda environment
conda create -n aiprediction-mcp python=3.9
conda activate aiprediction-mcp

# Install dependencies
pip install -r requirements.txt
```

#### Option C: Global Installation
```bash
# Install directly (not recommended for production)
pip install mcp aiohttp python-dotenv
```

### 3. Configure Environment Variables

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your credentials:**
   ```bash
   # AI Prediction API Configuration
   API_BASE_URL=https://aiprediction.us
   API_USERNAME=your_username_here
   API_PASSWORD=your_password_here
   ```

   Replace `your_username_here` and `your_password_here` with your actual aiprediction.us credentials.

## 🎯 Running the MCP Server

### Test the Server
```bash
python aiprediction-mcp-server.py
```

You should see output like:
```
📁 .env file loaded successfully
🚀 Starting AI Prediction MCP Server
🌐 API Base URL: https://aiprediction.us
🔐 Attempting authentication...
✅ Authentication successful!
✅ Token received: 190a0687f8db55f3640c...
📊 Testing data retrieval...
✅ Successfully retrieved data for 250613
🎯 MCP Server ready for connections
```

If you see errors:
- **Missing credentials**: Check your `.env` file
- **Authentication failed**: Verify your username/password
- **API errors**: Check your network connection

### Keep Server Running
The MCP server needs to stay running while you use Claude. You can:
- Run it in a terminal and keep it open
- Use screen/tmux for persistent sessions
- Run as a background service

## 🔧 Configure Claude Desktop

### 1. Find Claude's Configuration File

**macOS:**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```bash
%APPDATA%/Claude/claude_desktop_config.json
```

### 2. Add MCP Server Configuration

Edit the configuration file and add your MCP server:

```json
{
  "mcpServers": {
    "aiprediction": {
      "command": "python",
      "args": ["/full/path/to/your/MCPerver.py"],
      "env": {
        "API_BASE_URL": "https://aiprediction.us",
        "API_USERNAME": "your_username",
        "API_PASSWORD": "your_password"
      }
    }
  }
}
```

**Important:** Replace `/full/path/to/your/aiprediction-mcp-server.py` with the actual full path to your script.

### 3. Restart Claude Desktop

Close and reopen Claude Desktop to load the new configuration.

## 💬 Using Claude with AI Prediction Data

Once configured, you can ask Claude to access your AI prediction data:

### Example Queries

**Get Today's Data:**
```
Get today's AI prediction data
```

**Get Specific Date:**
```
Get the prediction data for December 15, 2024
```
```
What's the data for 250612?
```

**Date Conversion:**
```
Convert March 15, 2025 to YYMMDD format
```

**Historical Analysis:**
```
Compare prediction data between 241201 and 241215
```

### Available Tools

Claude will have access to these tools:

1. **`get_current_date_data`** - Gets prediction data for today
2. **`get_last_elements_by_date`** - Gets data for any specific date
3. **`format_date_yymmdd`** - Converts dates to YYMMDD format
4. **`get_api_debug_info`** - Gets API status and debug information

### Data Structure

The API returns data with this structure:
```json
{
  "DID": "250613",
  "ID": 421,
  "ctime": ["09:30 AM", "09:31 AM", ...],
  "lookup_method": "did",
  "last_elements": {
    "sp": 5970.62,
    "es": 5972.75,
    "p1": 5970.0,
    "c1": 5975.0,
    // ... more prediction fields
  }
}
```

## 🔍 Troubleshooting

### Common Issues

**1. "Missing credentials" Error**
- Check your `.env` file exists and has correct format
- Ensure no extra spaces around the `=` signs
- Verify file is in same directory as the script

**2. "Authentication failed" Error**
- Verify your username and password are correct
- Check if your aiprediction.us account is active
- Try logging in via the website first

**3. "MCP Server not found" in Claude**
- Check the full path in `claude_desktop_config.json`
- Ensure Python is in your system PATH
- Try using absolute path to Python executable

**4. "No data found" for specific dates**
- Some dates may not have prediction data
- Try recent trading days (weekdays)
- Check if the date format is correct (YYMMDD)

### Debug Mode

To see detailed logging, you can modify the server to show more information:

```bash
# Run with Python's verbose output
python -v aiprediction-mcp-server.py
```

### Check Configuration

Verify Claude can see your MCP server:
1. Open Claude Desktop
2. Look for MCP server indicators in the interface
3. Try asking: "What MCP tools do you have access to?"

## 📚 API Reference

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `API_BASE_URL` | Yes | Base URL for the API (https://aiprediction.us) |
| `API_USERNAME` | Yes | Your aiprediction.us username |
| `API_PASSWORD` | Yes | Your aiprediction.us password |

### Date Format

The API uses **YYMMDD** format:
- `250613` = June 13, 2025
- `241225` = December 25, 2024
- `240101` = January 1, 2024

### Available Endpoints

The MCP server accesses these API endpoints:
- `POST /api-token-auth/` - Authentication
- `GET /api/v53a/{did}/last-elements/` - Get prediction data
- `GET /api/debug/v53a/general/` - Debug information

## 🤝 Contributing

To improve this MCP server:

1. Fork the repository
2. Make your changes
3. Test with your AI Prediction account
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues:
1. Check the troubleshooting section above
2. Verify your aiprediction.us account works via their website
3. Test the MCP server output for detailed error messages
4. Check Claude Desktop's MCP configuration

---

**Happy Trading with AI Predictions! 📈**# aiprediction_us_MCP_Server
# MCPServer_aiprediction_us
