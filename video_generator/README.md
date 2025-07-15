# Video Generator Project

This project is modularized into two main components:

## 1. WhatsApp Chat Generator (`whatsapp_gen`)
- Generates funny WhatsApp-style chat conversations using the OpenAI API.
- Outputs paginated JSON with the full conversation.
- Requirements: see `whatsapp_gen/requirements.txt`.

### Usage
```bash
cd whatsapp_gen
pip install -r requirements.txt
python generate_funny_whatsapp.py
```

## 2. Video Overlay (`video_overlay`)
- Overlays a WhatsApp chat image onto a video, gradually revealing more of the image over time.
- Requirements: see `video_overlay/requirements.txt`.

### Usage
```bash
cd video_overlay
pip install -r requirements.txt
python overlay_whatsapp_on_video.py
```
- Place your video as `../../videoplayback.mp4` or adjust the path in the script.
- Place your WhatsApp chat image as `whatsapp_chat.png` in the same folder (or adjust the path).

---

You can extend this project to automatically generate chat images from the JSON output and feed them into the video overlay module. 