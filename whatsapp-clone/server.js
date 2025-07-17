const express = require('express');
const puppeteer = require('puppeteer');
const cors = require('cors');
const bodyParser = require('body-parser');
const path = require('path');
const fs = require('fs-extra');

const app = express();
const PORT = process.env.PORT || 3001;

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

// API endpoint to receive messages and generate screenshots
app.post('/api/generate-screenshots', async (req, res) => {
    try {
        const { messages, participants, outputDir, img_size } = req.body;
        
        console.log(`Received request to generate ${messages.length} message screenshots`);
        console.log(`Participants: ${participants.join(', ')}`);
        console.log(`Output directory: ${outputDir}`);
        
        // Ensure output directory exists
        await fs.ensureDir(outputDir);
        
        // Convert messages to React app format
        const convertedMessages = convertMessages(messages, participants);
        
        // Update the current messages for the React app
        currentMessages = convertedMessages;
        currentParticipants = participants;
        
        // Generate progressive screenshots
        const imagePaths = await generateProgressiveScreenshots(convertedMessages, outputDir, img_size);
        
        console.log(`Generated ${imagePaths.length} screenshots`);
        res.json({ 
            success: true, 
            imagePaths: imagePaths,
            message: `Generated ${imagePaths.length} screenshots successfully`
        });
        
    } catch (error) {
        console.error('Error generating screenshots:', error);
        res.status(500).json({ 
            success: false, 
            error: error.message 
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

// Serve the React app
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'build', 'index.html'));
});

async function generateProgressiveScreenshots(messages, outputDir, imgSize = [1920, 1080]) {
    const browser = await puppeteer.launch({
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
    
    try {
        const page = await browser.newPage();
        await page.setViewport({
            width: imgSize[1],
            height: imgSize[0],
            deviceScaleFactor: 1
        });
        await page.goto(`http://localhost:${PORT}`, { 
            waitUntil: 'networkidle2',
            timeout: 30000 
        });
        await page.waitForSelector('.whatsapp-container', { timeout: 10000 });

        // Inject all messages at once
        await page.evaluate((msgs, participants) => {
            window.currentMessages = msgs;
            window.currentParticipants = participants;
            window.dispatchEvent(new CustomEvent('updateMessages', {
                detail: { messages: msgs, participants }
            }));
        }, messages, currentParticipants);

        // Wait for the React app to update (simple timeout)
        await page.waitForTimeout(2000);

        // Take a single screenshot
        const filename = `whatsapp_full.png`;
        const screenshotPath = path.resolve(path.join(outputDir, filename));
        await page.screenshot({
            path: screenshotPath,
            fullPage: false,
            clip: {
                x: 0,
                y: 0,
                width: imgSize[1],
                height: imgSize[0]
            }
        });
        console.log(`Saved screenshot: ${screenshotPath}`);
        return [screenshotPath];
    } finally {
        await browser.close();
    }
}

// Health check endpoint
app.get('/api/health', (req, res) => {
    res.json({ 
        status: 'ok', 
        timestamp: new Date().toISOString(),
        message: 'WhatsApp screenshot server is running'
    });
});

app.listen(PORT, () => {
    console.log(`WhatsApp screenshot server running on port ${PORT}`);
    console.log(`React app will be served on http://localhost:${PORT}`);
    console.log(`API endpoints:`);
    console.log(`  POST /api/generate-screenshots - Generate screenshots`);
    console.log(`  GET  /api/messages - Get current messages`);
    console.log(`  GET  /api/health - Health check`);
}); 