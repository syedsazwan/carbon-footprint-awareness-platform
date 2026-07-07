import cv2
import numpy as np
from PIL import Image
import io
import base64
import re
from datetime import datetime

# Sample receipts for mockup fallback
SAMPLE_RECEIPTS = {
    "organic_market": {
        "store_name": "Organica Green Market",
        "date": "2026-06-15",
        "total": 25.87,
        "items": [
            {"name": "organic tofu 400g", "qty": 2, "price": 2.49},
            {"name": "fresh spinach bunch", "qty": 1, "price": 1.99},
            {"name": "almond milk 1l", "qty": 2, "price": 3.29},
            {"name": "oatmeal oats 1kg", "qty": 1, "price": 4.50},
            {"name": "avocado", "qty": 3, "price": 1.20},
            {"name": "local apples 1kg", "qty": 1, "price": 2.99}
        ],
        "raw_text": """ORGANICA GREEN MARKET
123 Sustainability Way, Eco City
DATE: 2026-06-15

ITEMS:
ORGANIC TOFU 400G      2 @ 2.49     4.98
FRESH SPINACH BUNCH    1 @ 1.99     1.99
ALMOND MILK 1L         2 @ 3.29     6.58
OATMEAL OATS 1KG       1 @ 4.50     4.50
AVOCADO                3 @ 1.20     3.60
LOCAL APPLES 1KG       1 @ 2.99     2.99

SUBTOTAL:                          24.64
TAX (5%):                           1.23
TOTAL:                             25.87
*** THANK YOU FOR SHOPPING GREEN! ***"""
    },
    "mega_mart": {
        "store_name": "Mega Mart Supercenter",
        "date": "2026-06-16",
        "total": 68.00,
        "items": [
            {"name": "premium ribeye steak 500g", "qty": 1, "price": 24.99},
            {"name": "cheddar cheese 500g", "qty": 1, "price": 7.50},
            {"name": "whole dairy milk 2l", "qty": 2, "price": 3.99},
            {"name": "chicken breast 1kg", "qty": 1, "price": 12.99},
            {"name": "white rice 5kg", "qty": 1, "price": 9.00},
            {"name": "plastic carry bag", "qty": 2, "price": 0.25}
        ],
        "raw_text": """MEGA MART SUPERCENTER
456 Commercial Blvd, Metroville
DATE: 2026-06-16

ITEMS:
PREMIUM RIBEYE STEAK   1 @ 24.99   24.99
CHEDDAR CHEESE 500G    1 @ 7.50     7.50
WHOLE DAIRY MILK 2L    2 @ 3.99     7.98
CHICKEN BREAST 1KG     1 @ 12.99   12.99
WHITE RICE 5KG         1 @ 9.00     9.00
PLASTIC CARRY BAG      2 @ 0.25     0.50

SUBTOTAL:                          62.96
TAX (8%):                           5.04
TOTAL:                             68.00
*** SAVE BIG AT MEGA MART! ***"""
    }
}

def to_base64(img_np):
    """Convert numpy BGR/Grayscale image to base64 JPEG string."""
    _, buffer = cv2.imencode('.jpg', img_np)
    io_buf = io.BytesIO(buffer)
    encoded = base64.b64encode(io_buf.getvalue()).decode('utf-8')
    return f"data:image/jpeg;base64,{encoded}"

def preprocess_receipt_image(image_bytes: bytes):
    """
    Execute OpenCV scan enhancement: grayscale, filter, edge detection, perspective warping.
    Returns:
        dict: Preprocessed steps as base64 strings and the best-warped or gray fallback image
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return None
        
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    filtered = cv2.bilateralFilter(gray, 9, 75, 75)
    edges = cv2.Canny(filtered, 75, 200)
    
    # Simple threshold
    _, thresh = cv2.threshold(filtered, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Try finding 4-corner document borders
    contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
    
    corners = None
    contour_img = img.copy()
    
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            corners = approx.reshape(4, 2)
            cv2.drawContours(contour_img, [approx], -1, (0, 255, 0), 3)
            break
            
    warped = None
    if corners is not None:
        try:
            # Sort corners
            rect = np.zeros((4, 2), dtype="float32")
            s = corners.sum(axis=1)
            rect[0] = corners[np.argmin(s)] # top-left
            rect[2] = corners[np.argmax(s)] # bottom-right
            
            diff = np.diff(corners, axis=1)
            rect[1] = corners[np.argmin(diff)] # top-right
            rect[3] = corners[np.argmax(diff)] # bottom-left
            
            (tl, tr, br, bl) = rect
            wA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
            wB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
            maxWidth = max(int(wA), int(wB))
            
            hA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
            hB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
            maxHeight = max(int(hA), int(hB))
            
            dst = np.array([[0, 0], [maxWidth - 1, 0], [maxWidth - 1, maxHeight - 1], [0, maxHeight - 1]], dtype="float32")
            M = cv2.getPerspectiveTransform(rect, dst)
            warped = cv2.warpPerspective(img, M, (maxWidth, maxHeight))
        except Exception:
            pass
            
    output_image = warped if warped is not None else img
    
    return {
        "steps": {
            "original": to_base64(img),
            "grayscale": to_base64(gray),
            "edges": to_base64(edges),
            "processed": to_base64(cv2.cvtColor(output_image, cv2.COLOR_BGR2GRAY))
        },
        "contour_found": corners is not None
    }

def parse_receipt_text(text: str):
    """Parse receipt text using regex to extract item details, store, and date."""
    lines = text.strip().split("\n")
    store_name = "Unknown Store"
    date = datetime.now().strftime("%Y-%m-%d")
    items = []
    
    if len(lines) > 0:
        store_candidate = lines[0].strip()
        if len(store_candidate) > 3:
            store_name = store_candidate
            
    date_pattern = re.compile(r'\b\d{4}[-/.]\d{2}[-/.]\d{2}\b')
    price_pattern = re.compile(r'(\d+\.\d{2})')
    
    for line in lines:
        date_match = date_pattern.search(line)
        if date_match:
            date = date_match.group(0)
            break
            
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
            
        if any(kw in line_clean.upper() for kw in ["TOTAL", "SUBTOTAL", "TAX", "ITEMS", "TEL:", "ADDRESS", "WELCOME", "THANK"]):
            continue
            
        prices = price_pattern.findall(line_clean)
        if prices:
            line_total = float(prices[-1])
            item_name = line_clean
            for p in prices:
                item_name = item_name.replace(p, "")
            
            item_name = re.sub(r'[\d@\$#\-\*]', '', item_name).strip()
            item_name = re.sub(r'\s+', ' ', item_name)
            
            qty = 1
            qty_match = re.search(r'\b(\d+)\s*@', line_clean)
            if qty_match:
                qty = int(qty_match.group(1))
            else:
                qty_x_match = re.search(r'\b(\d+)\s*[xX]\s*', line_clean)
                if qty_x_match:
                    qty = int(qty_x_match.group(1))
                    
            unit_price = round(line_total / qty, 2) if qty > 0 else line_total
            
            if len(item_name) > 2:
                items.append({
                    "name": item_name.lower(),
                    "qty": qty,
                    "price": unit_price
                })
                
    return {
        "store_name": store_name,
        "date": date,
        "items": items
    }

def run_hybrid_ocr(image_bytes: bytes, file_name: str = None):
    """
    Run Tesseract OCR if available, else fall back to parsing file text (if PDF)
    or matching mockup receipt structures based on file tags.
    """
    # 1. Check if Tesseract is installed for real OCR
    try:
        import pytesseract
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ocr_text = pytesseract.image_to_string(gray)
        if len(ocr_text.strip()) > 15:
            res = parse_receipt_text(ocr_text)
            return ocr_text, res["store_name"], res["date"], res["items"]
    except Exception:
        pass
        
    # 2. Check PDF text parsing
    if file_name and file_name.lower().endswith(".pdf"):
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(image_bytes))
            pdf_text = ""
            for page in reader.pages:
                pdf_text += page.extract_text() + "\n"
            if len(pdf_text.strip()) > 15:
                res = parse_receipt_text(pdf_text)
                return pdf_text, res["store_name"], res["date"], res["items"]
        except Exception:
            pass

    # 3. Dynamic Mockup Matching
    # Check if image name implies low/high carbon profile for demonstration fidelity
    sample_key = "organic_market"
    if file_name:
        fn_lower = file_name.lower()
        if "meat" in fn_lower or "high" in fn_lower or "mega" in fn_lower or "steak" in fn_lower:
            sample_key = "mega_mart"
            
    sample = SAMPLE_RECEIPTS[sample_key]
    # Update date to today to keep charts relevant
    today_str = datetime.now().strftime("%Y-%m-%d")
    raw_text = sample["raw_text"].replace(sample["date"], today_str)
    return raw_text, sample["store_name"], today_str, sample["items"]
