import os
import google.generativeai as genai
import PIL.Image

img = PIL.Image.open('meat.jpg')
genai.configure(api_key='')
# myfile = genai.upload_file(media / "Cajun_instruments.jpg")
# print(f"{myfile=}")

model = genai.GenerativeModel("gemini-1.5-flash")
# Define the folder containing images
image_folder = 'LLM Check Data'  # Update this to the path of your folder
output_file = 'extracted_promotions.csv'

# Open the output file in write mode
with open(output_file, 'w') as f:
    # Write the CSV header
    f.write("Product Name,Price Before Promotion,Price After Promotion,Rate of Discount\n")

    # Loop over all image files in the folder
    for image_file in os.listdir(image_folder):
        if image_file.endswith(('.jpg', '.jpeg', '.png', '.bmp')):  # Check for valid image formats
            image_path = os.path.join(image_folder, image_file)
            print(image_path)

            # Open and process the image
            img = PIL.Image.open(image_path)
            
            # Generate content with the generative model
            result = model.generate_content(
                [img, "\n\n", "This is an image of promotion from a supermarket. For each product, extract the product name, price before promotion, price after promotion, and rate of discount, put them in lines in form of CSV."]
            )

            # Write the extracted text to the file
            f.write(result.text + "\n")  # Add a newline for each image result

print(f"Extraction completed. Results saved in {output_file}.")

