import os
import json
import argparse
import requests  # For future use

def render_chat_images(messages, participants, out_dir, img_size=(1920, 1080)):
    """
    Call Node.js API to generate WhatsApp images from messages
    """
    os.makedirs(out_dir, exist_ok=True)
    
    # Call Node.js API
    api_url = "http://localhost:3001/generate-images"
    payload = {
        "messages": messages,
        "participants": participants,
        "outputDir": out_dir
    }
    
    try:
        response = requests.post(api_url, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        if result.get('success'):
            return result['imagePaths']
        else:
            raise Exception(f"API error: {result.get('error', 'Unknown error')}")
            
    except requests.exceptions.ConnectionError:
        raise Exception("Could not connect to Node.js server. Make sure it's running on port 3001")
    except requests.exceptions.Timeout:
        raise Exception("Request timed out. The image generation took too long")
    except Exception as e:
        raise Exception(f"Failed to generate images: {str(e)}")

def get_chat_images(messages, participants, out_dir, use_external=False, api_url=None, img_size=(1920, 1080)):
    """
    Abstraction for chat image generation.
    If use_external is True and api_url is provided, call the external API.
    Otherwise, use the local Node.js API.
    """
    if use_external and api_url:
        # Call external API
        payload = {
            "messages": messages,
            "participants": participants,
            "outputDir": out_dir,
            "img_size": img_size
        }
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        return response.json()["imagePaths"]
    else:
        # Call local Node.js API
        return render_chat_images(messages, participants, out_dir, img_size)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process WhatsApp chat images from JSON messages.")
    parser.add_argument("--json", required=True, help="Path to JSON file with messages list.")
    parser.add_argument("--out_dir", required=True, help="Directory to save output images.")
    parser.add_argument("--participants", nargs=2, default=["Ana", "Bruno"], help="Participant names.")
    args = parser.parse_args()

    with open(args.json, "r", encoding="utf-8") as f:
        messages = json.load(f)
    img_paths = render_chat_images(messages, args.participants, args.out_dir)
    print(json.dumps(img_paths, ensure_ascii=False, indent=2)) 