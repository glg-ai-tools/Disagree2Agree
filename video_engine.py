import os
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS

# Asset paths
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
SKITS_DIR = os.path.join(ASSETS_DIR, "skits")
WIDTH, HEIGHT = 1280, 720

def default_color():
    """Muted engineering slate as RGB tuple"""
    return (46, 46, 46)

def generate_skit_media(persona_name, script_text, base_filename):
    """
    Generates a static image and audio file for the skit.
    Returns paths to the generated image and audio files.
    
    Parameters:
        persona_name: Name of the speaking persona
        script_text: What they will say
        base_filename: Base name for output files (without extension)
    
    Returns:
        tuple: (image_path, audio_path)
    """
    os.makedirs(SKITS_DIR, exist_ok=True)
    
    # Generate image
    img = Image.new('RGB', (WIDTH, HEIGHT), default_color())
    draw = ImageDraw.Draw(img)
    
    # Try to use Arial, fall back to default font
    try:
        font = ImageFont.truetype("arial.ttf", 60)
    except Exception:
        font = ImageFont.load_default()
    
    # Center text (persona name)
    text = persona_name.title()
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    x = (WIDTH - text_width) // 2
    y = (HEIGHT - text_height) // 2
    
    draw.text((x, y), text, fill='white', font=font)
    
    # Save image and generate audio
    image_path = os.path.join(SKITS_DIR, f"{base_filename}.png")
    audio_path = os.path.join(SKITS_DIR, f"{base_filename}.mp3")
    
    img.save(image_path)
    
    # Generate speech audio from the provided script_text
    tts = gTTS(text=script_text)
    tts.save(audio_path)
    
    return image_path, audio_path

def generate_skit_slides_and_audio(persona_name, exec_summary, base_filename):
    """
    Generates multi-slide presentation images and an audio file for a skit.
    Splits the exec_summary into slides (using periods as delimiters).
    
    Returns:
        tuple: (list of image_paths, audio_path)
    """
    os.makedirs(SKITS_DIR, exist_ok=True)
    
    # Split exec_summary into sentences for slides.
    # This split can be refined (or use a library) for better results.
    slides_text = [s.strip() for s in exec_summary.split('. ') if s.strip()]
    
    slides_paths = []
    
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except Exception:
        font = ImageFont.load_default()
    
    for idx, slide_text in enumerate(slides_text, start=1):
        img = Image.new('RGB', (WIDTH, HEIGHT), default_color())
        draw = ImageDraw.Draw(img)
        # Center the slide text on the image
        text_bbox = draw.textbbox((0, 0), slide_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x = (WIDTH - text_width) // 2
        y = (HEIGHT - text_height) // 2
        draw.text((x, y), slide_text, fill='white', font=font)
        slide_path = os.path.join(SKITS_DIR, f"{base_filename}_slide_{idx}.png")
        img.save(slide_path)
        slides_paths.append(slide_path)
    
    # Generate audio from the full exec_summary
    audio_path = os.path.join(SKITS_DIR, f"{base_filename}.mp3")
    tts = gTTS(text=exec_summary)
    tts.save(audio_path)
    
    return slides_paths, audio_path

if __name__ == "__main__":
    # For testing purposes
    demo_img, demo_audio = generate_skit_media("demo", "This is a sample skit.", "demo_skit")
    print("Static skit image:", demo_img)
    print("Static skit audio:", demo_audio)
    
    slides, multi_audio = generate_skit_slides_and_audio("demo", "This is a sample executive summary. It is split into two slides.", "demo_multi")
    print("Multi-slide paths:", slides)
    print("Multi-slide audio:", multi_audio)
