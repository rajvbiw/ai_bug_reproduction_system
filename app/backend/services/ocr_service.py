import io
import logging

logger = logging.getLogger(__name__)

# Try importing PIL
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# Try importing pytesseract
try:
    import pytesseract
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False

class OCRService:
    def extract_text_from_image(self, image_bytes: bytes) -> str:
        """Extracts text from image bytes using pytesseract if available, else falls back gracefully."""
        if not HAS_PIL:
            logger.warning("Pillow library (PIL) not installed. OCR fallback activated.")
            return self._get_fallback_text()

        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            if HAS_TESSERACT:
                try:
                    text = pytesseract.image_to_string(image)
                    if text.strip():
                        return text
                except Exception as ex:
                    logger.warning(f"pytesseract failed to run (is Tesseract binary installed?): {ex}")
            else:
                logger.warning("pytesseract package not installed. Using text simulation.")
                
            # If tesseract is not installed or fails, return simulated OCR text based on image size/format
            return self._get_fallback_text(image.format, image.size)
        except Exception as e:
            logger.error(f"Failed to open image in OCR: {e}")
            return self._get_fallback_text()

    def _get_fallback_text(self, img_format="PNG", size=(800, 600)) -> str:
        """Simulate screenshot text extraction when OCR is unavailable."""
        return (
            f"--- [OCR DEMO FALLBACK] ---\n"
            f"Image detected: Format={img_format}, Size={size[0]}x{size[1]}\n"
            f"Traceback (most recent call last):\n"
            f"  File \"/app/backend/main.py\", line 15, in create_all\n"
            f"    Base.metadata.create_all(bind=engine)\n"
            f"  File \"/usr/local/lib/python3.11/site-packages/sqlalchemy/sql/schema.py\", line 5792, in create_all\n"
            f"    bind._run_ddl_visitor(ddl.SchemaGenerator, self, checkfirst=checkfirst)\n"
            f"sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError) (2003, \"Can't connect to MySQL server on 'db' ([Errno 111] Connection refused)\")\n"
            f"--- [END OCR DEMO FALLBACK] ---"
        )

ocr_service = OCRService()
