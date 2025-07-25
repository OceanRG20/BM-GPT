import pygetwindow as gw
import pyautogui
import pytesseract
from PIL import Image

# Optional: Set this if Tesseract is not in PATH
from config import TESSERACT_CMD

pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

def extract_bookmap_text():
    try:
        print("🔍 Searching for window with title containing 'Bookmap'...")
        for w in gw.getAllWindows():
            try:
                if "bookmap" in w.title.lower() and w.visible:
                    print(f"✅ Found window: '{w.title}' (visible)")
                    x, y, w_, h = w.left, w.top, w.width, w.height
                    region = (x, y, w_, h)  # Capture full window
                    screenshot = pyautogui.screenshot(region=region)
                    # Optional: save for debugging
                    screenshot.save("bookmap_debug_capture.png")
                    text = pytesseract.image_to_string(screenshot)
                    return text
            except Exception as e:
                print(f"⚠️ Skipping window due to error: {e}")
                continue

        print("❌ No visible window with 'Bookmap' in title found.")
        return None

    except Exception as e:
        print(f"❌ OCR error: {e}")
        return None
