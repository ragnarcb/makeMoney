# WhatsApp Screenshot Service (Node.js)

A microservice for generating WhatsApp-style chat images from JSON messages, using Puppeteer and a React frontend. Designed to be called by other services (e.g., Python orchestrator) via HTTP API.

---

## Features
- Renders WhatsApp chat images from JSON messages
- Crops output to the chat area (no extra whitespace)
- Two modes:
  - **Local Save** (default): saves images to disk
  - **Upload**: uploads images to a remote service (e.g., S3, Imgur) if enabled
- Handles multiple requests concurrently (async)
- Designed for use as a background service

---

## Usage

### Start the Service
```sh
cd whatsapp-clone
npm install
npm run build
npm start
```

The service will run on `http://localhost:3001` by default.

---

## API

### `POST /api/generate-screenshots`
Generate a WhatsApp chat image from messages.

**Request JSON:**
```json
{
  "messages": [ ... ],      // Array of message objects (see below)
  "participants": ["Ana", "Bruno"],
  "outputDir": "output_folder", // Where to save images (if local mode)
  "img_size": [1920, 1080] // (optional) [height, width]
}
```

**Message format:**
```json
{
  "from": "Ana",
  "to": "Bruno",
  "text": "Oi!"
}
```

**Response:**
```json
{
  "success": true,
  "imagePaths": ["/absolute/path/to/whatsapp_full.png"],
  "message": "Generated 1 screenshots successfully"
}
```

---

### Batch Mode (Multiple Chats)
You can POST an array of message sets:
```json
{
  "batch": [
    { "messages": [...], "participants": ["Ana", "Bruno"] },
    { "messages": [...], "participants": ["João", "Maria"] }
  ],
  "outputDir": "output_folder"
}
```
Response will be an array of image paths.

---

## Modes

### Local Save (default)
- Images are saved to the specified `outputDir` on disk.

### Upload Mode
- Set `UPLOAD_MODE=on` in your environment or `.env` file.
- Set `UPLOAD_SERVICE_URL` and any required credentials.
- Images will be uploaded after generation; response will include remote URLs.
- (You must implement/upload logic in `server.js` for your chosen service.)

---

## Environment Variables
- `PORT` - Port to run the service (default: 3001)
- `UPLOAD_MODE` - Set to `on` to enable upload mode (default: off)
- `UPLOAD_SERVICE_URL` - URL of the upload service (if using upload mode)
- `UPLOAD_API_KEY` - API key/token for upload service (if needed)

---

## Concurrency/Async
- The service handles multiple requests in parallel.
- Each screenshot job is independent and does not block others.
- (You may set a concurrency limit in `server.js` if needed for resource control.)

---

## Example: Python Client
```python
import requests
payload = {
    "messages": [...],
    "participants": ["Ana", "Bruno"],
    "outputDir": "test_output"
}
resp = requests.post("http://localhost:3001/api/generate-screenshots", json=payload)
print(resp.json())
```

---

## Health Check
- `GET /api/health` returns status JSON.

---

## Notes
- The React app must be built (`npm run build`) before starting the service.
- The `.whatsapp-container` selector is used for cropping; adjust if your UI changes.
- For upload mode, you must implement the upload logic in `server.js` (see comments in code).

```json
{
  "from": "Ana",
  "to": "Bruno",
  "text": "Oi!"
}
```

**Response:**
```json
{
  "success": true,
  "imagePaths": ["/absolute/path/to/whatsapp_full.png"],
  "message": "Generated 1 screenshots successfully"
}
```

---

### Batch Mode (Multiple Chats)
You can POST an array of message sets:
```json
{
  "batch": [
    { "messages": [...], "participants": ["Ana", "Bruno"] },
    { "messages": [...], "participants": ["João", "Maria"] }
  ],
  "outputDir": "output_folder"
}
```
Response will be an array of image paths.

---

## Modes

### Local Save (default)
- Images are saved to the specified `outputDir` on disk.

### Upload Mode
- Set `UPLOAD_MODE=on` in your environment or `.env` file.
- Set `UPLOAD_SERVICE_URL` and any required credentials.
- Images will be uploaded after generation; response will include remote URLs.
- (You must implement/upload logic in `server.js` for your chosen service.)

---

## Environment Variables
- `PORT` - Port to run the service (default: 3001)
- `UPLOAD_MODE` - Set to `on` to enable upload mode (default: off)
- `UPLOAD_SERVICE_URL` - URL of the upload service (if using upload mode)
- `UPLOAD_API_KEY` - API key/token for upload service (if needed)

---

## Concurrency/Async
- The service handles multiple requests in parallel.
- Each screenshot job is independent and does not block others.
- (You may set a concurrency limit in `server.js` if needed for resource control.)

---

## Example: Python Client
```python
import requests
payload = {
    "messages": [...],
    "participants": ["Ana", "Bruno"],
    "outputDir": "test_output"
}
resp = requests.post("http://localhost:3001/api/generate-screenshots", json=payload)
print(resp.json())
```

---

## Health Check
- `GET /api/health` returns status JSON.

---

## Notes
- The React app must be built (`npm run build`) before starting the service.
- The `.whatsapp-container` selector is used for cropping; adjust if your UI changes.
- For upload mode, you must implement the upload logic in `server.js` (see comments in code).
