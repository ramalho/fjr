from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

def create_label_sheet():
    # Create a new PDF with A4 size
    c = canvas.Canvas("labels.pdf", pagesize=A4)
    
    # A4 size in mm: 210 x 297
    page_width, page_height = A4
    
    # Label dimensions
    label_width = 63.6 * mm
    label_height = 25.4 * mm
    
    # Margins
    left_margin = 7 * mm
    right_margin = 7 * mm
    top_margin = 8 * mm
    bottom_margin = 8 * mm
    
    # Gutter between columns
    column_gutter = 2.5 * mm
    
    # Calculate available width and height
    available_width = page_width - left_margin - right_margin
    available_height = page_height - top_margin - bottom_margin
    
    # Calculate number of columns and rows
    num_columns = 3
    num_rows = 11
    
    # Draw labels
    for row in range(num_rows):
        for col in range(num_columns):
            # Calculate position of the current label
            x = left_margin + col * (label_width + column_gutter)
            y = page_height - top_margin - (row + 1) * label_height
            
            # Draw rectangle for the label border
            c.rect(x, y, label_width, label_height)
            
            # Add text to the label
            c.setFont("Helvetica", 12)
            text = f"{col}, {row}"
            text_width = c.stringWidth(text, "Helvetica", 12)
            text_x = x + (label_width - text_width) / 2
            text_y = y + label_height / 2 - 6  # Adjust for vertical centering
            c.drawString(text_x, text_y, text)
    
    # Save the PDF
    c.save()
    
    print("Label sheet created as 'labels.pdf'")

if __name__ == "__main__":
    create_label_sheet()