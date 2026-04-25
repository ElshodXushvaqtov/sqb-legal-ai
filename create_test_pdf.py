from reportlab.pdfgen import canvas

c = canvas.Canvas("test_murojaat.pdf")
c.setFont("Helvetica", 12)
c.drawString(100, 750, "O'zbekiston Respublikasi Bosh prokuraturasi")
c.drawString(100, 720, "SQB Bank bosh direktoriga")
c.drawString(100, 680, "TALAB")
c.drawString(100, 650, "Mijoz Karimov Jasur (JSHSHIR: 12345678901234)")
c.drawString(100, 620, "2024-yil 1-yanvardan 2024-yil 31-dekabrgacha")
c.drawString(100, 590, "bank hisobvaraqlari bo'yicha ma'lumot taqdim eting.")
c.drawString(100, 560, "Javob muddati: 10 ish kuni")
c.drawString(100, 530, "Bosh prokuror o'rinbosari: Rahimov A.A.")
c.save()
print("PDF yaratildi: test_murojaat.pdf")