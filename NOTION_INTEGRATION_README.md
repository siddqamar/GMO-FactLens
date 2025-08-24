# Notion Integration Setup

This document explains how to set up and use the Notion integration for automatically publishing analysis results.

## Environment Variables

Add these variables to your `.env` file:

```bash
# Required for Notion integration
NOTION_TOKEN=your_notion_integration_token_here
NOTION_PARENT_PAGE_ID=your_parent_page_id_here

# Optional configuration
PUBLISH_TO_NOTION=ture                    # Set to 'true' to enable Notion publishing
NOTION_CREATE_DB_EACH_RUN=true           # Set to 'true' to create new DB each run
NOTION_DATABASE_ID=existing_db_id_here    # Use existing DB if not creating new ones
```

## Getting Notion Credentials

### 1. Create a Notion Integration

1. Go to [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Click "New integration"
3. Give it a name (e.g., "Analysis Tool")
4. Select the workspace where your parent page is located
5. Copy the "Internal Integration Token"

### 2. Get Parent Page ID

1. Open the Notion page where you want to create databases
2. Copy the page ID from the URL:
   - URL format: `https://www.notion.so/Page-Title-1234567890abcdef1234567890abcdef`
   - Page ID: `1234567890abcdef1234567890abcdef`

### 3. Share Page with Integration

1. Open your parent page
2. Click "Share" in the top right
3. Click "Invite" and search for your integration name
4. Select it and give it "Edit" permissions

## Configuration Options

### PUBLISH_TO_NOTION
- `true`: Enable Notion publishing
- `false`: Disable Notion publishing (default)

### NOTION_CREATE_DB_EACH_RUN
- `true`: Create a new database for each analysis run
- `false`: Use existing database specified in `NOTION_DATABASE_ID`

### NOTION_DATABASE_ID
- Only needed when `NOTION_CREATE_DB_EACH_RUN=false`
- Copy from an existing database URL

## Database Schema

Each Notion database will have these properties:

- **Title**: Article title
- **URL**: Article URL
- **Content**: Full article content (truncated to 2000 chars)
- **Summary**: AI-generated summary
- **Claims**: Key claims extracted from article
- **Fact Status**: Fact/Myth/Unclear
- **Classification**: Health, Environmental, Social economics, etc.
- **Confidence**: High/Medium/Low
- **Analysis Date**: When analysis was performed

## Usage

1. Set environment variables
2. Run your Streamlit app
3. When `PUBLISH_TO_NOTION=true`, results will automatically be published
4. View the Notion database URL in the success message
5. Click the link to view results in Notion

## Error Handling

- **Rate Limiting**: Automatically retries once on 429 errors
- **Missing Credentials**: Shows warning if Notion integration is disabled
- **Publishing Failures**: Shows warnings for individual items that fail to publish

## Troubleshooting

### "Missing NOTION_TOKEN or NOTION_PARENT_PAGE_ID"
- Check your `.env` file has the correct values
- Ensure the integration token is valid
- Verify the parent page ID is correct

### "Rate limited by Notion API"
- The app automatically retries once
- If persistent, wait a few minutes before running again

### "Failed to create Notion database"
- Check integration has edit permissions on parent page
- Verify parent page ID is accessible
- Ensure integration is in the correct workspace
