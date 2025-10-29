import os
import sys
import shutil
import zipfile
import tempfile
from typing import Tuple

import requests

from core.utils import get_data_dir


FFMPEG_RELEASE_ZIP_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"


def _safe_extract_zip(zip_path: str, dest_dir: str) -> None:
    abs_dest = os.path.abspath(dest_dir)
    with zipfile.ZipFile(zip_path, 'r') as zf:
        for member in zf.namelist():
            target_path = os.path.abspath(os.path.join(abs_dest, member))
            if not (target_path + os.sep).startswith(abs_dest + os.sep) and target_path != abs_dest:
                raise ValueError(f"Insecure path in zip entry: {member}")
        for info in zf.infolist():
            target = os.path.abspath(os.path.join(abs_dest, info.filename))
            if info.is_dir():
                os.makedirs(target, exist_ok=True)
            else:
                os.makedirs(os.path.dirname(target), exist_ok=True)
                with zf.open(info, 'r') as src, open(target, 'wb') as dst:
                    shutil.copyfileobj(src, dst)


def _find_bin_dir(root: str) -> str:
    for dirpath, dirnames, filenames in os.walk(root):
        for name in filenames:
            if name.lower() == ("ffmpeg.exe" if sys.platform.startswith("win") else "ffmpeg"):
                return os.path.dirname(os.path.join(dirpath, name))
    return ""


def install_ffmpeg() -> Tuple[bool, str]:
    """
    Download and install FFmpeg into app data directory.
    Returns (success, installed_bin_path_or_error_message)
    """
    if not sys.platform.startswith("win"):
        return False, "Auto-install is currently implemented for Windows only"

    data_dir = get_data_dir()
    install_root = os.path.join(data_dir, "ffmpeg")
    target_bin = os.path.join(install_root, "bin")
    os.makedirs(target_bin, exist_ok=True)

    tmp_dir = tempfile.mkdtemp(prefix="ffmpeg_dl_", dir=data_dir)
    zip_path = os.path.join(tmp_dir, "ffmpeg-release-essentials.zip")

    try:
        with requests.get(FFMPEG_RELEASE_ZIP_URL, stream=True, timeout=30) as r:
            r.raise_for_status()
            total = int(r.headers.get('Content-Length', 0))
            # Rough sanity limit (<= 500MB)
            if total and total > 500 * 1024 * 1024:
                return False, "Downloaded file too large"
            with open(zip_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1048576):  # 1MB chunks
                    if chunk:
                        f.write(chunk)

        extract_dir = os.path.join(tmp_dir, "extract")
        os.makedirs(extract_dir, exist_ok=True)
        _safe_extract_zip(zip_path, extract_dir)

        src_bin = _find_bin_dir(extract_dir)
        if not src_bin:
            return False, "Could not locate ffmpeg bin directory in archive"

        # Copy all files from src_bin to target_bin
        for name in os.listdir(src_bin):
            src = os.path.join(src_bin, name)
            dst = os.path.join(target_bin, name)
            if os.path.isdir(src):
                if os.path.exists(dst):
                    shutil.rmtree(dst, ignore_errors=True)
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)

        ffmpeg_exe = os.path.join(target_bin, "ffmpeg.exe")
        if not os.path.exists(ffmpeg_exe):
            return False, "ffmpeg.exe not found after installation"

        return True, target_bin
    except Exception as e:
        return False, str(e)
    finally:
        try:
            shutil.rmtree(tmp_dir, ignore_errors=True)
        except Exception:
            pass


