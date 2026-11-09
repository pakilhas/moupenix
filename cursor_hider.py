import ctypes
import atexit

user32 = ctypes.windll.user32

# IDs dos cursores do Windows
OCR_NORMAL = 32512
OCR_IBEAM = 32513
OCR_WAIT = 32514
OCR_CROSS = 32515
OCR_UP = 32516
OCR_SIZE = 32640
OCR_ICON = 32641
OCR_SIZENWSE = 32642
OCR_SIZENESW = 32643
OCR_SIZEWE = 32644
OCR_SIZENS = 32645
OCR_SIZEALL = 32646
OCR_NO = 32648
OCR_HAND = 32649
OCR_APPSTARTING = 32650

ALL_CURSORS = [
    OCR_NORMAL, OCR_IBEAM, OCR_HAND, OCR_CROSS, OCR_NO,
    OCR_SIZEALL, OCR_SIZENWSE, OCR_SIZENESW, OCR_SIZEWE, OCR_SIZENS
]

SPI_SETCURSORS = 0x0057
SPIF_SENDCHANGE = 0x02

class CursorHider:
    def __init__(self):
        self.is_hidden = False
        atexit.register(self.restore)

    def create_blank_cursor(self):
        # Cria um cursor 1x1 100% transparente
        and_mask = bytes([0xFF])
        xor_mask = bytes([0x00])
        return user32.CreateCursor(0, 0, 0, 1, 1, and_mask, xor_mask)

    def hide(self):
        if self.is_hidden:
            return True
        try:
            for cursor_id in ALL_CURSORS:
                blank = self.create_blank_cursor()
                if blank:
                    # SetSystemCursor destrói o handle, então usamos CopyIcon
                    copy_cur = user32.CopyIcon(blank)
                    user32.SetSystemCursor(copy_cur, cursor_id)
                    user32.DestroyCursor(blank)
            self.is_hidden = True
            return True
        except Exception:
            return False

    def restore(self):
        if not self.is_hidden:
            return
        try:
            # SPI_SETCURSORS restaura todos os cursores para os originais do sistema
            user32.SystemParametersInfoW(SPI_SETCURSORS, 0, None, SPIF_SENDCHANGE)
        except Exception:
            pass
        finally:
            self.is_hidden = False

