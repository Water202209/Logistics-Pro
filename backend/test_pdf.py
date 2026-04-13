# test_pdf.py - 纯测试用，确认环境是否正常
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import io
from fastapi.responses import Response

def generate_test_pdf():
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # 第1页
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height/2, "Page 1: Order Info")
    c.showPage()
    print("✅ Page 1 done")
    
    # 第2页
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height/2, "Page 2: Map")
    c.showPage()
    print("✅ Page 2 done")
    
    # 第3页
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height/2, "Page 3: Layout")
    c.save()
    print("✅ Page 3 done, PDF saved")
    
    buffer.seek(0)
    return buffer.getvalue()

if __name__ == "__main__":
    pdf_bytes = generate_test_pdf()
    with open("test_3pages.pdf", "wb") as f:
        f.write(pdf_bytes)
    print("📄 test_3pages.pdf 已生成，请用 PDF 阅读器打开确认页数")