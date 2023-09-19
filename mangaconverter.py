from PIL import Image
from fpdf import FPDF
import os


# target folder
folder = "./YOUR TARGET FOLDER/"

fname = input("What name should be used for saving the pdf-files(s): ").replace(" ", "_")
subfolders = [directory for directory in os.listdir(folder) if os.path.isdir(folder+directory)]
for f in subfolders:
    pdf = FPDF()
    folder_x = folder + f
    filenames = os.listdir(folder_x)

    filenames.sort()

    for filename in filenames:
        image_path = os.path.join(folder_x, filename)
        image = Image.open(image_path)

        width, height = image.size

        width_mm = width / 3.779527559
        height_mm = height / 3.779527559

        pdf.add_page(orientation="P", format=(width_mm, height_mm))

        pdf.image(image_path, x=0, y=0, w=width_mm, h=height_mm)

    pdf.output(f"{fname}_{f}.pdf", "F")
