from reportlab.pdfgen import canvas

def create_dummy_pdf(filename):
    c = canvas.Canvas(filename)
    c.drawString(100, 750, "John Doe")
    c.drawString(100, 730, "Software Engineer")
    c.drawString(100, 710, "Skills: Python, React, AI")
    c.save()

if __name__ == "__main__":
    create_dummy_pdf("dummy_resume.pdf")
    print("Created dummy_resume.pdf")
