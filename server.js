const express = require('express');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');
const cors = require('cors');

const app = express();

// Middleware
app.use(bodyParser.json({ limit: '10mb' })); // Parse JSON with large payloads (Base64 images)
app.use(cors()); // Enable Cross-Origin Resource Sharing

// Directory to store uploaded images
const uploadsDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadsDir)) {
    fs.mkdirSync(uploadsDir);
}

// Endpoint to handle image uploads
app.post('/upload-image', (req, res) => {
    const base64Image = req.body.image; // Get the Base64 string
    if (!base64Image) {
        return res.status(400).json({ error: 'No image provided' });
    }

    const base64Data = base64Image.split(';base64,').pop(); // Remove metadata
    const fileName = `slide8-${Date.now()}.png`; // Unique filename
    const filePath = path.join(uploadsDir, fileName);

    // Save the Base64 image as a PNG file
    fs.writeFile(filePath, base64Data, { encoding: 'base64' }, (err) => {
        if (err) {
            console.error('Error saving the image:', err);
            return res.status(500).json({ error: 'Failed to save the image' });
        }

        const imageUrl = `http://localhost:3000/uploads/${fileName}`;
        res.json({ imageUrl }); // Respond with the hosted image URL
    });
});

// Serve uploaded images as static files
app.use('/uploads', express.static(uploadsDir));

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running at http://localhost:${PORT}`);
});

