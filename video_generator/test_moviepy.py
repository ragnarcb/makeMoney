#!/usr/bin/env python3

print("Testing moviepy imports and methods...")

# Test basic imports
try:
    from moviepy.video.io.VideoFileClip import VideoFileClip
    print("✅ VideoFileClip import successful")
except ImportError as e:
    print(f"❌ VideoFileClip import failed: {e}")

try:
    from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
    print("✅ ImageSequenceClip import successful")
except ImportError as e:
    print(f"❌ ImageSequenceClip import failed: {e}")

try:
    from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
    print("✅ CompositeVideoClip import successful")
except ImportError as e:
    print(f"❌ CompositeVideoClip import failed: {e}")

# Test AudioFileClip import
try:
    from moviepy.audio.io.AudioFileClip import AudioFileClip
    print("✅ AudioFileClip import successful")
except ImportError as e:
    print(f"❌ AudioFileClip import failed: {e}")

try:
    import moviepy
    print(f"✅ moviepy version: {moviepy.__version__}")
except ImportError as e:
    print(f"❌ moviepy import failed: {e}")

# Test for concatenation methods
print("\n=== Testing concatenation methods ===")
try:
    # Check if concatenate_videoclips exists
    try:
        from moviepy.video.compositing.concatenate import concatenate_videoclips
        print("✅ concatenate_videoclips import successful")
    except ImportError:
        print("❌ concatenate_videoclips not found in moviepy.video.compositing.concatenate")
    
    # Check if it's in the main moviepy module
    try:
        import moviepy
        if hasattr(moviepy, 'concatenate_videoclips'):
            print("✅ concatenate_videoclips found in moviepy module")
        else:
            print("❌ concatenate_videoclips not found in moviepy module")
    except Exception as e:
        print(f"❌ Error checking moviepy module: {e}")
    
    # Check what's available in the compositing module
    try:
        import moviepy.video.compositing
        print(f"Available in moviepy.video.compositing: {dir(moviepy.video.compositing)}")
    except Exception as e:
        print(f"❌ Error checking compositing module: {e}")
except Exception as e:
    print(f"❌ Concatenation test failed: {e}")

print("\n=== Testing VideoFileClip methods ===")
try:
    # Create a dummy VideoFileClip to test methods
    clip = VideoFileClip("test.mp4") if VideoFileClip in locals() else None
    if clip:
        print("VideoFileClip methods:")
        methods = dir(clip)
        print(f"  - subclip: {'subclip' in methods}")
        print(f"  - duration: {'duration' in methods}")
        print(f"  - w (width): {'w' in methods}")
        print(f"  - h (height): {'h' in methods}")
        print(f"  - size: {'size' in methods}")
        
        # Look for slicing methods
        print(f"  - __getitem__ (for slicing): {'__getitem__' in methods}")
        
        # Look for duration-related methods
        duration_methods = [m for m in methods if 'duration' in m.lower()]
        print(f"  - Duration-related methods: {duration_methods}")
        
        clip.close()
except Exception as e:
    print(f"❌ VideoFileClip method test failed: {e}")

print("\n=== Testing ImageSequenceClip methods ===")
try:
    if ImageSequenceClip in locals():
        print("ImageSequenceClip class methods:")
        methods = dir(ImageSequenceClip)
        
        # Check for resize methods
        resize_methods = [m for m in methods if 'resize' in m.lower()]
        print(f"  - Resize methods: {resize_methods}")
        
        # Check for position methods
        position_methods = [m for m in methods if 'position' in m.lower()]
        print(f"  - Position methods: {position_methods}")
        
        # Check for duration methods
        duration_methods = [m for m in methods if 'duration' in m.lower()]
        print(f"  - Duration methods: {duration_methods}")
        
        # Check for size methods
        size_methods = [m for m in methods if 'size' in m.lower()]
        print(f"  - Size methods: {size_methods}")
        
        # Show all methods
        print(f"  - All methods: {methods}")
except Exception as e:
    print(f"❌ ImageSequenceClip method test failed: {e}")

print("\n=== Testing CompositeVideoClip methods ===")
try:
    if 'CompositeVideoClip' in locals():
        print("CompositeVideoClip class methods:")
        methods = dir(CompositeVideoClip)
        
        # Check for duration methods
        duration_methods = [m for m in methods if 'duration' in m.lower()]
        print(f"  - Duration methods: {duration_methods}")
        
        # Check for write methods
        write_methods = [m for m in methods if 'write' in m.lower()]
        print(f"  - Write methods: {write_methods}")
        
        # Check for size methods
        size_methods = [m for m in methods if 'size' in m.lower()]
        print(f"  - Size methods: {size_methods}")
        
        # Show all methods
        print(f"  - All methods: {methods}")
except Exception as e:
    print(f"❌ CompositeVideoClip method test failed: {e}")

print("\n=== Testing VideoClip base class methods ===")
try:
    from moviepy.video.VideoClip import VideoClip
    print("VideoClip base class methods:")
    methods = dir(VideoClip)
    
    # Check for common methods
    common_methods = ['resize', 'set_position', 'set_duration', 'write_videofile', 'duration', 'e']
    for method in common_methods:
        print(f"  - {method}: {'method' in methods}")   
    # Show all methods
    print(f"  - All methods: {methods}")
except Exception as e:
    print(f"❌ VideoClip method test failed: {e}")

print("\n=== Testing actual clip creation ===")
try:
    # Create a simple test clip to see what methods are available
    import numpy as np
    from PIL import Image
    
    # Create a simple test image
    test_img = Image.new('RGB', (100, 10), color='red')
    test_img.save('test_frame.png')
    
    # Try to create an ImageSequenceClip
    if ImageSequenceClip in locals():
        test_clip = ImageSequenceClip([test_frame.png], fps=1)
        print("✅ ImageSequenceClip creation successful")
        print(f"  - Available methods: {dir(test_clip)}")
        
        # Test specific methods
        print(f"  - duration: {hasattr(test_clip, 'duration')}")
        print(f"  - size: {hasattr(test_clip, 'size')}")
        print(f"  - w: {hasattr(test_clip, 'w')}")
        print(f"  - h: {hasattr(test_clip, 'h')}")
        
        # Clean up
        import os
        if os.path.exists('test_frame.png'):         os.remove('test_frame.png')
            
except Exception as e:
    print(f"❌ Clip creation test failed: {e}")

print("\nTest completed!") 