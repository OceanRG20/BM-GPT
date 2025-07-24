import pygetwindow as gw
import pyautogui
import pytesseract
from PIL import Image

# Optional: Set this if Tesseract is not in PATH
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_bookmap_text():
    try:
        print("🔍 Searching for window with title containing 'Bookmap'...")
        for w in gw.getAllWindows():
            try:
                if "bookmap" in w.title.lower() and w.visible:
                    print(f"✅ Found window: '{w.title}' (visible)")
                    x, y, w_, h = w.left, w.top, w.width, w.height
                    region = (x + 100, y + 100, w_ - 200, h - 200)  # Customize as needed
                    screenshot = pyautogui.screenshot(region=region)
                    # Optional: save for debugging
                    screenshot.save("bookmap_debug_capture.png")
                    text = pytesseract.image_to_string(screenshot)
                    return text.strip()
            except Exception as e:
                print(f"⚠️ Skipping window due to error: {e}")
                continue

        print("❌ No visible window with 'Bookmap' in title found.")
        return None

    except Exception as e:
        print(f"❌ OCR error: {e}")
        return None
