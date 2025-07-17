# WhatsApp Screenshot Service

A Node.js service for generating WhatsApp chat screenshots using Puppeteer and React. This service supports both local file saving and cloud upload modes, with full async support for handling multiple concurrent individual requests.

## Features

- 🚀 **Async Processing**: Handles many individual requests concurrently (configurable concurrency)
- 📁 **Dual Output Modes**: Local save (default) or cloud upload
- 🎨 **Customizable**: Configurable image sizes and output formats
- 🔧 **Production Ready**: Health checks, error handling, and logging

## Quick Start

### Prerequisites

- Node.js 16+
- npm or yarn

### Installation

```bash
cd whatsapp-clone
npm install
```

### Environment Variables

Create a `.env` file in the project root:

```env
# Server Configuration
PORT=3001
NODE_ENV=production

# Output Mode (local/upload)
UPLOAD_MODE=off

# Upload Service Configuration (when UPLOAD_MODE=on)
UPLOAD_SERVICE=s3
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
AWS_BUCKET=your-bucket-name

# Concurrency Settings
MAX_CONCURRENT_REQUESTS=5
BROWSER_TIMEOUT=30000

# Output Settings
DEFAULT_IMAGE_SIZE=1920,1080
OUTPUT_DIR=./output
```

### Running the Service

```bash
# Development mode
npm run dev

# Production mode
npm start
```

The service will be available at `http://localhost:3001`

## API Reference

### Health Check

```http
GET /api/health
```

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2024-01-01T00:00:00Z",
  "message": "WhatsApp screenshot server is running"
}
```

### Generate Screenshot (Single Request)

```http
POST /api/generate-screenshots
Content-Type: application/json
```

**Request Body:**
```json
{
  "messages": [
    { "text": "Hello!", "from": "Alice" },
    { "text": "Hi there!", "from": "Bob" }
  ],
  "participants": ["Alice", "Bob"],
  "outputDir": "./output",
  "img_size": [1920, 1080]
}
```

**Response (Local Save Mode):**
```json
{
  "success": true,
  "imagePaths": ["/path/to/screenshot.png"],
  "messageCoordinates": [
    {
      "index": 0,
      "y": 120,
      "height": 45,
      "width": 200,
      "from": "Alice",
      "text": "Hello!",
      "isMine": false
    },
    {
      "index": 1,
      "y": 180,
      "height": 52,
      "width": 180,
      "from": "Bob",
      "text": "Hi there!",
      "isMine": true
    }
  ],
  "message": "Generated 1 screenshot successfully"
}
```

**Response (Upload Mode):**
```json
{
  "success": true,
  "imageUrls": ["https://your-bucket.s3.amazonaws.com/screenshot.png"],
  "messageCoordinates": [
    {
      "index": 0,
      "y": 120,
      "height": 45,
      "width": 200,
      "from": "Alice",
      "text": "Hello!",
      "isMine": false
    }
  ],
  "message": "Generated and uploaded 1 screenshot successfully"
}
```

## Output Modes

### Local Save Mode (Default)

When `UPLOAD_MODE=off`, screenshots are saved locally to the specified `outputDir`.

### Upload Mode

When `UPLOAD_MODE=on`, screenshots are uploaded to a cloud service after generation.

**Supported Services:**
- **AWS S3**: Upload to S3 bucket
- **Imgur**: Upload to Imgur (requires API key)
- **Custom**: Implement your own upload service

## Message Format

Messages should follow this structure:

```typescript
interface Message {
  text: string;        // Message content
  from: string;        // Sender name
  timestamp?: string;  // Optional timestamp
}
```

## Error Handling

The service returns appropriate HTTP status codes:

- `200`: Success
- `400`: Bad request (invalid input)
- `429`: Too many requests (rate limited)
- `500`: Internal server error

**Error Response Format:**
```json
{
  "success": false,
  "error": "Error description",
  "code": "ERROR_CODE"
}
```

## Performance & Concurrency

### Concurrent Request Handling

The service uses a queue system to handle multiple individual requests:

- **Default**: 5 concurrent requests
- **Configurable**: Set via `MAX_CONCURRENT_REQUESTS`
- **Queue Management**: Automatic request queuing when at capacity

### Browser Management

- **Browser Pool**: Reuses browser instances for efficiency
- **Timeout Handling**: Configurable timeouts per request
- **Resource Cleanup**: Automatic cleanup of browser resources

## Development

### Project Structure

```
whatsapp-clone/
├── server.js              # Main server file
├── package.json           # Dependencies and scripts
├── public/                # Static files
├── src/                   # React app source
│   ├── components/        # React components
│   └── types/             # TypeScript types
├── output/                # Generated screenshots (local mode)
└── README.md              # This file
```

### Adding Custom Upload Services

To add a custom upload service, modify the `uploadService.js` file:

```javascript
// Example custom upload service
async function uploadToCustomService(filePath, options) {
  // Your upload logic here
  return {
    url: 'https://your-service.com/file.png',
    success: true
  };
}

module.exports = {
  uploadToCustomService
};
```

### Testing

```bash
# Run tests
npm test

# Test with sample data
curl -X POST http://localhost:3001/api/generate-screenshots \
  -H "Content-Type: application/json" \
  -d @test_messages.json
```

## Troubleshooting

### Common Issues

1. **Browser Launch Failures**
   - Ensure you have Chrome/Chromium installed
   - Check system resources (memory, disk space)

2. **Timeout Errors**
   - Increase `BROWSER_TIMEOUT` in environment variables
   - Check network connectivity
3. **Upload Failures**
   - Verify API keys and credentials
   - Check service-specific error logs

### Logs

The service provides detailed logging:

```bash
# View logs
tail -f logs/app.log

# Debug mode
DEBUG=* npm start
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the API documentation
