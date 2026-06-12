import os
import subprocess
import pytest
from pathlib import Path

def has_libreoffice():
    try:
        subprocess.run(["soffice", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        return True
    except FileNotFoundError:
        default_path = Path(r"C:\Program Files\LibreOffice\program\soffice.exe")
        if default_path.exists():
            return True
        return False

def get_soffice_cmd():
    try:
        subprocess.run(["soffice", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        return "soffice"
    except FileNotFoundError:
        return r"C:\Program Files\LibreOffice\program\soffice.exe"

@pytest.mark.skipif(not has_libreoffice(), reason="LibreOffice (soffice) not available in PATH")
def test_visual_export_pdf():
    # First build a PPTX
    from deck2pptx.__main__ import build_cmd
    from argparse import Namespace
    
    base_dir = Path("examples")
    out_dir = Path("outputs")
    out_dir.mkdir(exist_ok=True)
    
    pptx_path = out_dir / "test_export.pptx"
    md_pptx_path = out_dir / "test_export_md.pptx"
    
    args_yaml = Namespace(input_file=str(base_dir / "sample.deck.yaml"), output_file=str(pptx_path), format=None)
    args_md = Namespace(input_file=str(base_dir / "sample.md"), output_file=str(md_pptx_path), format=None)
    
    build_cmd(args_yaml)
    build_cmd(args_md)
    
    assert pptx_path.exists()
    assert md_pptx_path.exists()
    
    # Run soffice conversion
    import time
    soffice_cmd = get_soffice_cmd()
    subprocess.run([soffice_cmd, "--headless", "--convert-to", "pdf", "--outdir", str(out_dir), str(pptx_path)], check=True)
    time.sleep(3) # Wait for previous soffice.bin to fully terminate to avoid IPC lock issues
    subprocess.run([soffice_cmd, "--headless", "--convert-to", "pdf", "--outdir", str(out_dir), str(md_pptx_path)], check=True)
    
    pdf_path = out_dir / "test_export.pdf"
    md_pdf_path = out_dir / "test_export_md.pdf"
    
    assert pdf_path.exists()
    assert md_pdf_path.exists()
    assert pdf_path.stat().st_size > 0
    assert md_pdf_path.stat().st_size > 0
