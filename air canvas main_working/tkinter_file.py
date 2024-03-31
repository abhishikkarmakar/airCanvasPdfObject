import os
import tkinter as tk
from tkinter import colorchooser, filedialog, ttk

import fitz  # PyMuPDF
from PIL import Image, ImageTk

# Global variables
selected_color = "black"
zoom_factor = 1.0
drawing_mode = "draw"
canvas = None  # Define canvas globally
current_page = 0  # Track current page number
pdf_document = None  # Store PDF document globally


# Function to open PDF file and display it in Tkinter window
def open_pdf():
    global pdf_document
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if file_path:
        try:
            # Open PDF using PyMuPDF
            pdf_document = fitz.open(file_path)

            # Display PDF using Tkinter
            display_pdf(pdf_document)
        except Exception as e:
            print("Error:", e)


# Function to display PDF in Tkinter window
def display_pdf(pdf_document):
    global canvas, current_page

    # Create a Tkinter window
    window = tk.Tk()
    window.title("PDF Viewer")

    # Create a frame to hold the toolbar
    toolbar_frame = tk.Frame(window)
    toolbar_frame.pack(side="left", fill="y")

    # Function to change the drawing color
    def change_color():
        global selected_color
        color = colorchooser.askcolor(title="Choose Color")
        if color[1] is not None:
            selected_color = color[1]

    # Function to handle zooming
    def zoom(value):
        global zoom_factor
        zoom_factor = float(value) / 100.0
        display_pdf_page(current_page)

    # Function to clear all annotations
    def clear_all():
        canvas.delete("all")
        display_pdf_page(current_page)

    # Function to switch between drawing and erasing mode
    def switch_mode():
        global drawing_mode
        if drawing_mode == "draw":
            drawing_mode = "erase"
            switch_mode_button.config(text="Drawing Mode (Erase)")
        else:
            drawing_mode = "draw"
            switch_mode_button.config(text="Drawing Mode (Draw)")

    # Function to save current screen as PDF
    def save_as_pdf():
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")]
        )
        if file_path:
            try:
                with fitz.open() as doc:
                    page = doc.new_page(
                        width=canvas.winfo_width(), height=canvas.winfo_height()
                    )
                    pdf_page = pdf_document.load_page(current_page)
                    pix = pdf_page.get_pixmap(
                        matrix=fitz.Matrix(zoom_factor, zoom_factor)
                    )
                    page.show_pixmap(xyz=pix)
                    doc.save(file_path)
            except Exception as e:
                print("Error saving as PDF:", e)

    # Button to change drawing color
    color_button = tk.Button(toolbar_frame, text="Select Color", command=change_color)
    color_button.pack(side="top")

    # Scale for zooming
    zoom_scale = ttk.Scale(
        toolbar_frame,
        from_=10,
        to=200,
        orient="vertical",
        length=200,
        command=zoom,
    )
    zoom_scale.pack(side="top")
    zoom_scale.set(100)  # Default zoom level

    # Button to clear all annotations
    clear_button = tk.Button(toolbar_frame, text="Clear All", command=clear_all)
    clear_button.pack(side="top")

    # Button to switch between drawing and erasing mode
    switch_mode_button = tk.Button(
        toolbar_frame, text="Drawing Mode (Erase)", command=switch_mode
    )
    switch_mode_button.pack(side="top")

    # Button to save current screen as PDF
    save_button = tk.Button(toolbar_frame, text="Save as PDF", command=save_as_pdf)
    save_button.pack(side="top")

    # Create a canvas to display PDF pages
    canvas = tk.Canvas(window, width=600, height=800)
    canvas.pack(side="left", fill="both", expand=True)

    # Function to handle drawing on canvas
    def draw(event):
        x, y = event.x, event.y
        if drawing_mode == "draw":
            canvas.create_oval(x, y, x + 5, y + 5, fill=selected_color)
        elif drawing_mode == "erase":
            canvas.delete("current")

    # Bind mouse motion event to canvas for drawing
    canvas.bind("<B1-Motion>", draw)

    # Function to display PDF page
    def display_pdf_page(page_number):
        global current_page
        current_page = page_number
        canvas.delete("all")
        try:
            pdf_page = pdf_document.load_page(page_number)
            page_image = pdf_page.get_pixmap(
                matrix=fitz.Matrix(zoom_factor, zoom_factor)
            )
            image = Image.frombytes(
                "RGB", (page_image.width, page_image.height), page_image.samples
            )
            tk_image = ImageTk.PhotoImage(image)
            canvas.create_image(0, 0, anchor="nw", image=tk_image)
            canvas.image = tk_image
        except Exception as e:
            print("Error displaying page:", e)

    # Display first page of the PDF
    display_pdf_page(0)

    # Navigation buttons
    def prev_page():
        if current_page > 0:
            display_pdf_page(current_page - 1)

    def next_page():
        if current_page < pdf_document.page_count - 1:
            display_pdf_page(current_page + 1)

    prev_button = tk.Button(toolbar_frame, text="Prev Page", command=prev_page)
    prev_button.pack(side="top")

    next_button = tk.Button(toolbar_frame, text="Next Page", command=next_page)
    next_button.pack(side="top")

    # Start the Tkinter event loop
    window.mainloop()


# Main function to open PDF and display in Tkinter window
def main():
    open_pdf()


if __name__ == "__main__":
    main()
