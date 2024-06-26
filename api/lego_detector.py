import cv2
import os
import uuid
import numpy as np


# Calculate the average color of pixels darker than [50, 50, 50]
def average_dark_color(image):
  dark_pixels = []
  for row in image:
    for pixel in row:
      if all(pixel < [50, 50, 50]):  # Check if the pixel is darker than the threshold
        dark_pixels.append(pixel)
  if not dark_pixels:
    return [25, 25, 25]  # Fallback color if no dark pixels are found
  return np.mean(dark_pixels, axis=0)


def process_image(user_image_path):
  img_example = cv2.imread(user_image_path)
  img_bg = cv2.imread('input/background_backlit_B.jpg') # Size = 3024 x 4032

  # Adjust img_bg to the same size as img_example
  img_bg = cv2.resize(img_bg, (img_example.shape[1], img_example.shape[0]), interpolation=cv2.INTER_AREA)

  # Convert to grayscale
  img_bg_gray = cv2.cvtColor(img_bg, cv2.COLOR_BGR2GRAY)
  img_gray = cv2.cvtColor(img_example, cv2.COLOR_BGR2GRAY)

  # Calculate difference between background and example image
  diff_gray = cv2.absdiff(img_bg_gray, img_gray)

  # Gaussian blur to smooth out pixels
  diff_gray_blur = cv2.GaussianBlur(diff_gray, (5, 5), 0)

  # Find threshold to convert to binary image using Otsu's meth od
  ret, img_tresh = cv2.threshold(diff_gray_blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

  # Find contours
  arr_cnt, a2 = cv2.findContours(img_tresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

  # Copy image to avoid overwriting
  img_with_allcontours = img_example.copy()
  cv2.drawContours(img_with_allcontours, arr_cnt, -1, (0, 255, 0), 3)

  # DISCARD Lego blocks that are not considered to be a block (valid contours)

  # Dimensions de l'image
  height, width, channels = img_example.shape

  validcontours = []
  contour_index = -1

  # Iterer sur chaque contour
  for i in arr_cnt:

    contour_index = contour_index + 1
    ca = cv2.contourArea(i)

    # Calcul du ratio W/H
    x, y, w, h = cv2.boundingRect(i)
    aspect_ratio = float(w) / h

    # Flag en tant que bruit si le contour est sur le bord de l'image
    # Les contours qui sont sur le bord de l'image sont generalement du bruit
    edge_noise = False
    if x == 0:
      edge_noise = True
    if y == 0:
      edge_noise = True
    # Si l'objet est sur le bord de l'image, on le considere comme du bruit
    if (x + w) == width:
      edge_noise = True
    if (y + h) == height:
      edge_noise = True

    # SUPPRIMER si l'aire est trop petite
    if ca > 1300:
      if aspect_ratio <= 6:
        # SUPPRIMER si le contour est sur le bord de l'image
        if not edge_noise:
          validcontours.append(contour_index)

  # Copier l'image originale
  img_withcontours = img_example.copy()

  # Afficher le nombre de contours valides
  if len(validcontours) > 1:
    print("There is more than 1 object in the picture")
  else:
    if len(validcontours) == 1:
      print("One object detected")
    else:
      print("No objects detected")

  for i in validcontours:
    cv2.drawContours(img_withcontours, arr_cnt, i, (0, 255, 0), 3)

  # Afficher les bounding boxes
  img_withrectangle = img_example.copy()
  for i in validcontours:
    x, y, w, h = cv2.boundingRect(arr_cnt[i])
    cv2.rectangle(img_withrectangle, (x, y), (x + w, y + h), (0, 255, 0), 2)

  # Save each brick in a separate file
  img_withrectangle = img_example.copy()

  # Check output folder
  if not os.path.exists('output'):
    os.makedirs('output')

  # Iterer sur chaque contour
  bricks_data = []
  for i in validcontours:
    x, y, w, h = cv2.boundingRect(arr_cnt[i])
    unique_filename = f"brick_{i}_{uuid.uuid4()}.jpg"
    brick_info = {
      "id": i,
      "position": {"x": x, "y": y},
      "size": {"width": w, "height": h},
      "image_path": f"http://brick-ai.eu-4.evennode.com/output/{unique_filename}"
    }
    bricks_data.append(brick_info)
    cv2.rectangle(img_withrectangle, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Crop image
    crop_img = img_example[y:y + h, x:x + w]

    # Assuming 'img' is your image
    avg_color = average_dark_color(crop_img)

    # Force the image to be a square, fill the rest with 25, 25, 25
    if w > h:
      # Add padding to the top and bottom
      pad = int((w - h) / 2)
      crop_img = cv2.copyMakeBorder(crop_img, pad, pad, 0, 0, cv2.BORDER_CONSTANT, value=avg_color)
    else:
      # Add padding to the left and right
      pad = int((h - w) / 2)
      crop_img = cv2.copyMakeBorder(crop_img, 0, 0, pad, pad, cv2.BORDER_CONSTANT, value=avg_color)

    # Make the image grey
    crop_img = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)

    # Save the cropped image with the unique filename
    cv2.imwrite(f"output/{unique_filename}", crop_img)

  return bricks_data