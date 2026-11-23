import numpy as np
from PIL import Image
import pytesseract
import cv2
import pandas as pd
import glob
import os


def adjust_gamma(image, gamma=1.5):
    """
    Adjust the gamma of an input image to control its brightness.

    Parameters:
    - image: The input image to process (as a NumPy array).
    - gamma: The gamma correction value (default is 1.5).
             A value greater than 1 makes the image brighter,
             while a value less than 1 makes it darker.

    Returns:
    - The gamma-corrected image.
    """
    # Calculate the inverse of the gamma value
    invGamma = 1.0 / gamma

    # Create a lookup table mapping pixel values [0, 255] to their adjusted values
    # Each value in the table is adjusted using the formula:
    # new_value = (old_value / 255.0) ** invGamma * 255
    table = np.array(
        [(i / 255.0) ** invGamma * 255 for i in np.arange(0, 256)]
    ).astype("uint8")

    # Apply the lookup table to the image to adjust its pixel values
    # cv2.LUT is used to map the pixel intensities according to the lookup table
    return cv2.LUT(image, table)



def transform_homography(image, imgName):
    """
    Applies a homography transformation to an image, adjusting its perspective to a standard rectangular shape. This is useful for correcting distorted perspectives in images, 
    such as cards, documents, or planar surfaces.

    :param image: The input image in which the homography transformation will be applied.
    :param imgName: The base name of the image, used for saving intermediate and final results.
    :return: transformed image
    """



    # Convert the input image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect edges using the Canny edge detector
    edges = cv2.Canny(gray, 50, 150)

    # Find contours in the edge-detected image
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)

    # Select the largest contour based on area
    contour = max(contours, key=cv2.contourArea)

    # Approximate the contour to reduce the number of points
    epsilon = 0.02 * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)

    # Check if at least 4 corners (vertices) were found
    if len(approx) >= 4:
        # Extract corner points
        points = np.array([point[0] for point in approx], dtype="float32")

        # Calculate sums and differences of the points' coordinates
        # to determine their positions
        s = points.sum(axis=1)
        diff = np.diff(points, axis=1)

        # Identify the four corners of the contour
        top_left = points[np.argmin(s)]
        bottom_right = points[np.argmax(s)]
        top_right = points[np.argmin(diff)]
        bottom_left = points[np.argmax(diff)]

        # Arrange the corners in the correct order
        src_pts = np.array([top_left, top_right, bottom_right, bottom_left],
                           dtype="float32")

        # Draw the detected contour on the original image
        cv2.polylines(image, [src_pts.astype(int)], isClosed=True,
                      color=(0, 255, 0), thickness=3)

        # Save the image with the contour overlaid
        cv2.imwrite(f"output/{imgName}_original_with_contour.jpg", image)

        # Define the destination points for the homography transformation
        dst = np.array([
            [100, 100],  # Top-left corner
            [650, 100],  # Top-right corner
            [650, 650],  # Bottom-right corner
            [100, 650]   # Bottom-left corner
        ], dtype="float32")

        # Compute the homography matrix
        homography_matrix, _ = cv2.findHomography(src_pts, dst)

        # Warp the perspective of the original image using the homography matrix
        warped_image = cv2.warpPerspective(image, homography_matrix, (800, 800))

        # Save the transformed (warped) image
        cv2.imwrite(f"output/{imgName}_transformed_card.jpg", warped_image)

        return warped_image
    else:
        # Print a message if not enough corners were found
        print("Failed to find enough corners.")
        return image


def detect_face(img, imgName):
    """
    Detects and extracts the face from an image using a Haar Cascade classifier for frontal faces.

    :param img: Input image where faces are to be detected.
    :param imgName: Base name of the image, used for saving the detected face.
    :return:
    """
    # Convert the input image to grayscale
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Load the Haar cascade classifier for face detection
    face_classifier = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    # Detect faces in the grayscale image
    # - `scaleFactor`: Specifies how much the image size is reduced at each image scale.
    # - `minNeighbors`: Specifies how many neighbors each candidate rectangle should have to retain it.
    # - `minSize`: Minimum possible object size. Objects smaller than this are ignored.
    face = face_classifier.detectMultiScale(
        gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40)
    )

    # Get the coordinates and size of the first detected face
    (x, y, w, h) = face[0]

    # Crop the face from the original image
    cropped_face = img[y:y + h, x:x + w]

    # Save the cropped face image
    cv2.imwrite(f"output/{imgName}_onlyface_result.jpg", cropped_face)


def optical_character_recognition(image):
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    string = pytesseract.image_to_string(image)

    df = pd.read_excel(
        r"input\students\class_list.xlsx",
        engine="openpyxl",
        dtype={"Student number": str},
        keep_default_na=False
    )

    for index, row in df.iterrows():
        student_number = row["Student number"].strip()

        if student_number and student_number in string:
            print(
                f"Student NO: {student_number}, "
                f"Name: {row['Student name']} is attending"
            )
        elif student_number and student_number not in string:
            print(
                f"Student NO: {student_number}, "
                f"Name: {row['Student name']} is not attending"
            )

    #print(string)





# Pls specify here the folder of your pictures:
image_folder = "input"

# Check if the folder exists
if not os.path.exists(image_folder):
    print(f"Error: The specified folder '{image_folder}' does not exist. Please check the path and try again.")
else:
    # Get a list of all .jpg images in the folder
    image_files = glob.glob(f"{image_folder}/*.jpg")

    if not image_files:
        print(f"Error: No .jpg images found in the folder '{image_folder}'. Please ensure the folder contains .jpg files.")
    else:
      # Process all images (in jpg format) in the specified folder
      for imgpath in glob.glob(f"{image_folder}/*.jpg"):
          print(f"Processing of {imgpath} has started.")  # Log the start of processing
          imgname = os.path.splitext(os.path.basename(imgpath))[0]  # Extract the image name without extension

          # Read the image from the given path
          image = cv2.imread(imgpath)

          if image is None:
              print(f"Unable to read image: {imgpath}")
              continue

          image_text = image.copy()
          image = cv2.resize(image,
              (800, 800),
              interpolation=cv2.INTER_AREA,
          )

          # Apply gamma correction to enhance brightness
          image = adjust_gamma(image, gamma=1.5)

          optical_character_recognition(image_text)

          try:
              # Attempt to apply homography transformation
              transformed = transform_homography(image, imgname)
          except Exception as e:
              # Log the error if homography transformation fails
              print(f"Homography error for image {imgname}: {e}")
              continue  # Skip further processing for this image

          try:
              # Attempt to detect and crop the face in the transformed image
              detect_face(transformed, imgname)
          except Exception as e:
              # Log the error if face detection fails
              print(f"Face detection error for image {imgname}: {e}")
            

          # Log the completion of processing for the current image
          print(f"Processing of {imgname} has been completed.")