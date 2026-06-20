import shutil
import subprocess
import tempfile
import os

def has_mermaid_cli() -> bool:
    """Return True if mmdc is available on PATH."""
    return shutil.which("mmdc") is not None

def render_to_temp_image(code: str) -> str:
    """
    Write code to a temp .mmd file, call mmdc, return path to output .png.
    Raises subprocess.CalledProcessError on mmdc failure.
    The caller is responsible for cleaning up the returned file.
    """
    with tempfile.NamedTemporaryFile(suffix=".mmd", mode="w",
                                     encoding="utf-8", delete=False) as f:
        f.write(code)
        mmd_path = f.name

    mmdc_path = shutil.which("mmdc") or "mmdc"
    png_path = mmd_path.replace(".mmd", ".png")
    try:
        subprocess.run(
            [mmdc_path, "-i", mmd_path, "-o", png_path],
            check=True,
            capture_output=True,
        )
    finally:
        os.unlink(mmd_path)

    return png_path
