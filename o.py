from PIL import Image, ImageDraw, ImageFont

# Set the image size and background color (RGBA)
width, height = 400, 200
background_color = (0, 0, 0, 0)  # Transparent background (RGBA)

# Create a new image with a transparent background
img = Image.new("RGBA", (width, height), background_color)

# Create a drawing context
draw = ImageDraw.Draw(img)

# Choose a font and font size
#font = ImageFont.truetype("arial.ttf", 36)

# Text color (RGBA)
text_color = (255, 0, 0, 255)  # Red text (RGBA)

# Text position
text_position = (50, 50)

# Text to be added
text = "Select campaign picture or video"

# Add the text to the image
draw.text(text_position, text, fill=text_color)

# Save the image with transparency
img.save("ad.png", "PNG")

# Display the image (optional)
img.show()
