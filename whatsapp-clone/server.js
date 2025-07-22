const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const path = require('path');
const fs = require('fs-extra');
require('dotenv').config();
const { chromium } = require('playwright');

const app = express();
const PORT = process.env.PORT || 3001;

// Configuration
const config = {
    uploadMode: process.env.UPLOAD_MODE === 'on',
    uploadService: process.env.UPLOAD_SERVICE || 's3',
    maxConcurrentRequests: parseInt(process.env.MAX_CONCURRENT_REQUESTS) || 5,
    browserTimeout: parseInt(process.env.BROWSER_TIMEOUT) || 30000,
    defaultImageSize: process.env.DEFAULT_IMAGE_SIZE ?
        process.env.DEFAULT_IMAGE_SIZE.split(',').map(Number) : [1920, 1080],
    outputDir: process.env.OUTPUT_DIR || './output',
    // If true, use local S3-like HTTP API for storage
    useLocalS3: process.env.LOCAL_S3_EMULATOR === 'true',
    localS3BaseUrl: process.env.LOCAL_S3_BASE_URL || 'http://192.168.1.218:30880',
    localS3Bucket: process.env.LOCAL_S3_BUCKET || 'test',
};

// Queue for managing concurrent requests
class RequestQueue {
    constructor(maxConcurrent) {
        this.maxConcurrent = maxConcurrent;
        this.running = 0;
        this.queue = [];
    }

    async add(task) {
        return new Promise((resolve, reject) => {
            this.queue.push({ task, resolve, reject });
            this.process();
        });
    }

    async process() {
        if (this.running >= this.maxConcurrent || this.queue.length === 0) {
            return;
        }

        this.running++;
        const { task, resolve, reject } = this.queue.shift();

        try {
            const result = await task();
            resolve(result);
        } catch (error) {
            reject(error);
        } finally {
            this.running--;
            this.process();
        }
    }

    getStatus() {
        return {
            running: this.running,
            queued: this.queue.length,
            maxConcurrent: this.maxConcurrent
        };
    }
}

const requestQueue = new RequestQueue(config.maxConcurrentRequests);

// Browser pool for efficient resource management
class BrowserPool {
    constructor() {
        this.browsers = [];
        this.maxBrowsers = 3;
    }

    async getBrowser() {
        if (this.browsers.length > 0) {
            return this.browsers.pop();
        }
        return await chromium.launch({
            headless: true,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu'
            ]
        });
    }

    async releaseBrowser(browser) {
        if (this.browsers.length < this.maxBrowsers) {
            this.browsers.push(browser);
        } else {
            await browser.close();
        }
    }

    async cleanup() {
        for (const browser of this.browsers) {
            await browser.close();
        }
        this.browsers = [];
    }
}

const browserPool = new BrowserPool();

// Upload service (placeholder - implement your own)
const uploadService = {
    async uploadToS3(filePath, options = {}) {
        if (config.useLocalS3) {
            // Use local S3-like HTTP API
            const axios = require('axios');
            const FormData = require('form-data');
            const fs = require('fs');
            const path = require('path');
            const fileName = path.basename(filePath);
            const form = new FormData();
            form.append('file', fs.createReadStream(filePath), fileName);
            try {
                const url = `${config.localS3BaseUrl}/buckets/${config.localS3Bucket}/files`;
                const response = await axios.post(url, form, {
                    headers: form.getHeaders(),
                    maxContentLength: Infinity,
                    maxBodyLength: Infinity
                });
                if (response.status === 200 || response.status === 201) {
                    return {
                        url: `${config.localS3BaseUrl}/buckets/${config.localS3Bucket}/files/${fileName}`,
                        success: true
                    };
                } else {
                    throw new Error(`Local S3 upload failed: ${response.status} ${response.statusText}`);
                }
            } catch (err) {
                console.error('[UPLOAD] Local S3 upload error:', err);
                throw err;
            }
        } else {
            // Placeholder for real S3 upload
            console.log(`[UPLOAD] Would upload ${filePath} to S3`);
            return {
                url: `https://your-bucket.s3.amazonaws.com/${path.basename(filePath)}`,
                success: true
            };
        }
    },

    async uploadToImgur(filePath, options = {}) {
        // Placeholder for Imgur upload
        // You would implement Imgur API here
        console.log(`[UPLOAD] Would upload ${filePath} to Imgur`);
        return {
            url: `https://i.imgur.com/${path.basename(filePath)}`,
            success: true
        };
    },

    async upload(filePath, service = config.uploadService) {
        switch (service) {
            case 's3':
                return await this.uploadToS3(filePath);
            case 'imgur':
                return await this.uploadToImgur(filePath);
            default:
                throw new Error(`Unsupported upload service: ${service}`);
        }
    }
};

// Middleware
app.use(cors());
app.use(bodyParser.json({ limit: '10mb' }));
app.use(express.static(path.join(__dirname, 'build')));

// Store the current messages for the React app
let currentMessages = [];
let currentParticipants = ['Ana', 'Bruno'];

// Convert Python message format to React app format
function convertMessages(pythonMessages, participants) {
    const [sender, receiver] = participants;
    return pythonMessages.map((msg, index) => ({
        id: (index + 1).toString(),
        texto: msg.text,
        usuario: {
            id: msg.from === sender ? 'user1' : 'user2',
            nome: msg.from
        },
        timestamp: new Date(Date.now() + index * 60000).toISOString(),
        isMine: msg.from === receiver
    }));
}

// Generate screenshot function
async function generateScreenshot(messages, participants, outputDir, imgSize = config.defaultImageSize) {
    const browser = await browserPool.getBrowser();
    let page;
    try {
        page = await browser.newPage();
        // Start with a large enough height to render all messages
        await page.setViewportSize({
            width: imgSize[1],
            height: 3000 // Large initial height to ensure all messages render
        });
        await page.goto(`http://localhost:${PORT}`, {
            waitUntil: 'networkidle',
            timeout: config.browserTimeout
        });
        await page.waitForSelector('.whatsapp-container', { timeout: 10000 });
        // Convert and inject messages
        const convertedMessages = convertMessages(messages, participants);
        await page.evaluate(({msgs, participants}) => {
            window.currentMessages = msgs;
            window.currentParticipants = participants;
            window.dispatchEvent(new CustomEvent('updateMessages', {
                detail: { messages: msgs, participants }
            }));
        }, {msgs: convertedMessages, participants});
        await page.waitForTimeout(2000);
        // Get the bounding box of the chat container
        const chatBox = await page.$('.whatsapp-container');
        const boundingBox = await chatBox.boundingBox();
        // Set viewport height to fit the chat container exactly
        await page.setViewportSize({
            width: imgSize[1],
            height: Math.ceil(boundingBox.y + boundingBox.height)
        });
        const messageCoordinates = await page.evaluate(() => {
            const container = document.querySelector('.whatsapp-container');
            const containerRect = container.getBoundingClientRect();
            const messageBubbles = document.querySelectorAll('.message-bubble');
            const coordinates = [];
            messageBubbles.forEach((bubble, index) => {
                const rect = bubble.getBoundingClientRect();
                const messageText = bubble.querySelector('.message-text');
                const senderName = bubble.querySelector('.sender-name');
                coordinates.push({
                    index: index,
                    y: Math.round(rect.top - containerRect.top),
                    height: Math.round(rect.height),
                    width: Math.round(rect.width),
                    from: senderName ? senderName.textContent.trim() : 'Unknown',
                    text: messageText ? messageText.textContent.trim() : '',
                    isMine: bubble.classList.contains('my-message')
                });
            });
            return coordinates;
        });
        await fs.ensureDir(outputDir);
        const filename = `whatsapp_${Date.now()}.png`;
        const screenshotPath = path.resolve(path.join(outputDir, filename));
        await page.screenshot({
            path: screenshotPath,
            fullPage: false,
            clip: {
                x: Math.round(boundingBox.x),
                y: Math.round(boundingBox.y),
                width: Math.round(boundingBox.width),
                height: Math.round(boundingBox.height)
            }
        });
        console.log(`[SCREENSHOT] Saved: ${screenshotPath}`);
        console.log(`[COORDINATES] Found ${messageCoordinates.length} message coordinates`);
        if (config.uploadMode) {
            try {
                const uploadResult = await uploadService.upload(screenshotPath);
                await fs.remove(screenshotPath);
                return {
                    type: 'upload',
                    url: uploadResult.url,
                    success: uploadResult.success,
                    messageCoordinates: messageCoordinates
                };
            } catch (uploadError) {
                console.error('[UPLOAD] Error:', uploadError);
                return {
                    type: 'local',
                    path: screenshotPath,
                    success: true,
                    messageCoordinates: messageCoordinates
                };
            }
        } else {
            return {
                type: 'local',
                path: screenshotPath,
                success: true,
                messageCoordinates: messageCoordinates
            };
        }
    } finally {
        if (page) await page.close();
        await browserPool.releaseBrowser(browser);
    }
}

// API endpoint for single screenshot generation
/**
 * @api {post} /api/generate-screenshots Generate WhatsApp chat screenshot
 * @apiName GenerateScreenshot
 * @apiGroup Screenshot
 *
 * @apiParam {Array} messages      Array of message objects
 * @apiParam {Array} participants  Array of two participant names
 * @apiParam {String} outputDir    Output directory for local save
 * @apiParam {Array} img_size      [height, width] (optional)
 *
 * @apiSuccess {Boolean} success
 * @apiSuccess {Array}   imagePaths (if local mode)
 * @apiSuccess {Array}   imageUrls  (if upload mode)
 * @apiSuccess {Array}   messageCoordinates Array of message positions and metadata
 * @apiSuccess {String}  message
 */
app.post('/api/generate-screenshots', async (req, res) => {
    try {
        const { messages, participants, outputDir, img_size } = req.body;

        // Validation
        if (!messages || !Array.isArray(messages) || messages.length === 0) {
            return res.status(400).json({
                success: false,
                error: 'Messages array is required and must not be empty',
                code: 'INVALID_MESSAGES'
            });
        }

        if (!participants || !Array.isArray(participants) || participants.length !== 2) {
            return res.status(400).json({
                success: false,
                error: 'Participants array must contain exactly 2 names',
                code: 'INVALID_PARTICIPANTS'
            });
        }

        console.log(`[REQUEST] Single screenshot: ${messages.length} messages, participants: ${participants.join(', ')}`);

        // Add to queue
        const result = await requestQueue.add(async () => {
            return await generateScreenshot(
                messages,
                participants,
                outputDir || config.outputDir,
                img_size
            );
        });

        // Format response based on mode
        if (result.type === 'upload') {
            res.json({
                success: true,
                imageUrls: [result.url],
                messageCoordinates: result.messageCoordinates,
                message: 'Generated and uploaded 1 screenshot successfully'
            });
        } else {
            res.json({
                success: true,
                imagePaths: [result.path],
                messageCoordinates: result.messageCoordinates,
                message: 'Generated 1 screenshot successfully'
            });
        }

    } catch (error) {
        console.error('[ERROR] Single screenshot generation:', error);
        res.status(500).json({
            success: false,
            error: error.message,
            code: 'GENERATION_ERROR'
        });
    }
});

// API endpoint to get current messages (for the React app)
app.get('/api/messages', (req, res) => {
    res.json({
        messages: currentMessages,
        participants: currentParticipants
    });
});

// Health check endpoint with queue status
app.get('/api/health', (req, res) => {
    res.json({
        status: 'ok',
        timestamp: new Date().toISOString(),
        message: 'WhatsApp screenshot server is running',
        config: {
            uploadMode: config.uploadMode,
            uploadService: config.uploadService,
            maxConcurrentRequests: config.maxConcurrentRequests,
            useLocalS3: config.useLocalS3,
            localS3BaseUrl: config.localS3BaseUrl,
            localS3Bucket: config.localS3Bucket
        },
        queue: requestQueue.getStatus()
    });
});

// Queue status endpoint
app.get('/api/queue/status', (req, res) => {
    res.json({
        queue: requestQueue.getStatus(),
        timestamp: new Date().toISOString()
    });
});

// Serve the React app
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'build', 'index.html'));
});

// Graceful shutdown
process.on('SIGTERM', async () => {
    console.log('[SHUTDOWN] Received SIGTERM, cleaning up...');
    await browserPool.cleanup();
    process.exit(0);
});

process.on('SIGINT', async () => {
    console.log('[SHUTDOWN] Received SIGINT, cleaning up...');
    await browserPool.cleanup();
    process.exit(0);
});

app.listen(PORT, () => {
    console.log(`[SERVER] WhatsApp screenshot server running on port ${PORT}`);
    console.log(`[SERVER] React app will be served on http://localhost:${PORT}`);
    console.log(`[CONFIG] Upload mode: ${config.uploadMode ? 'ON' : 'OFF'}`);
    console.log(`[CONFIG] Upload service: ${config.uploadService}`);
    console.log(`[CONFIG] Max concurrent requests: ${config.maxConcurrentRequests}`);
    console.log(`[CONFIG] Use Local S3 Emulator: ${config.useLocalS3 ? 'ON' : 'OFF'}`);
    console.log(`[CONFIG] Local S3 Base URL: ${config.localS3BaseUrl}`);
    console.log(`[CONFIG] Local S3 Bucket: ${config.localS3Bucket}`);
    console.log(`[API] Available endpoints:`);
    console.log(`  POST /api/generate-screenshots - Generate single screenshot`);
    console.log(`  GET  /api/messages - Get current messages`);
    console.log(`  GET  /api/health - Health check`);
    console.log(`  GET  /api/queue/status - Queue status`);
}); 