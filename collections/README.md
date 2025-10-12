# Postman Collections

This directory contains the Postman collection and environment for testing the ANB Rising Stars API.

## Files

- `anb_api.postman_collection.json` - Complete collection with all 9 API endpoints
- `postman_environment.json` - Environment variables for local development

## How to Use

### Import Collection

1. Open Postman
2. Click "Import" button
3. Select `anb_api.postman_collection.json`
4. Click "Import"

### Import Environment

1. Click the gear icon (⚙️) in top right
2. Click "Import"
3. Select `postman_environment.json`
4. Close the modal
5. Select "ANB Development" from the environment dropdown

### Running Requests

The collection is organized into 3 folders:

1. **Authentication**
   - Signup - Creates a new user
   - Login - Authenticates and returns user_id

2. **Videos**
   - Upload Video - Uploads a video file
   - List My Videos - Gets all videos for a user
   - Get Video Detail - Gets details for a specific video
   - Delete Video - Deletes a video (if not public)

3. **Public**
   - List Public Videos - Gets all public videos
   - Vote for Video - Casts a vote for a video
   - Get Rankings - Gets video rankings by votes
   - Get Rankings by City - Filters rankings by city

### Environment Variables

The collection uses these variables:
- `base_url` - API base URL (default: http://localhost:8000/api)
- `user_id` - Automatically set after signup/login
- `video_id` - Automatically set after video upload

### Automated Tests

Each request includes automated tests that verify:
- Correct HTTP status codes
- Response structure
- Required fields presence
- Data validation

Tests run automatically after each request. Check the "Test Results" tab to see if they passed.

### Running the Collection

You can run the entire collection:

1. Click the three dots (...) next to the collection name
2. Select "Run collection"
3. Click "Run ANB Rising Stars API"
4. View test results

### Tips

1. **Start with Signup/Login**: Run these first to set the `user_id` variable
2. **Upload a Video**: You need a real MP4 video file (20-60s, min 1080p)
3. **Make Video Public**: To test voting, manually set `is_public=true` in the database
4. **Reset Data**: Clear database and run migrations again for a fresh start

## Newman CLI

You can also run the collection from command line using Newman:

```bash
# Install Newman
npm install -g newman

# Run collection
newman run anb_api.postman_collection.json -e postman_environment.json

# With detailed output
newman run anb_api.postman_collection.json -e postman_environment.json --reporters cli,json

# Generate HTML report
newman run anb_api.postman_collection.json -e postman_environment.json --reporters cli,html
```

## Troubleshooting

**Variables not being set**
- Check that tests are passing in the "Test Results" tab
- Verify the response structure matches what the test expects

**Connection errors**
- Ensure the API server is running: `uvicorn app.main:app --reload`
- Check the `base_url` in your environment

**File upload fails**
- Use a valid MP4 video file
- Ensure video meets requirements (20-60s, min 1080p)
- Check file size (max 100MB)

## Support

For issues or questions:
1. Check the main [README.md](../README.md)
2. Review the [SETUP_GUIDE.md](../SETUP_GUIDE.md)
3. Open an issue in the repository

