import cv2
import numpy as np
import pytesseract
import re

# Brightness adjustment (Gamma correction)
def adjust_gamma(image, gamma=1.5):
    """
    Adjust the brightness of an image using gamma correction.

    Parameters:
    - image: Input BGR image as a NumPy array of pixel values from 0 to 255.
    - gamma: Brightness setting (default 1.5).
             Values above 1.0 brighten darker areas; values below 1.0 darken them.

    Returns:
    - A new brightened or darkened image array of the same size.
    """
    # Invert gamma so values > 1 brighten midtones (and < 1 darken them)
    invGamma = 1.0 / gamma

    # Precompute a 256 entry lookup table mapping every old pixel value (0..255) to its new value:
    # 1. Scale i from 0..255 down to 0.0..1.0
    # 2. Raise to invGamma
    # 3. Scale back up to 0..255 and store as integer

    table = np.array(
        [(i / 255.0) ** invGamma * 255 for i in np.arange(0, 256)]
    ).astype("uint8")

    # Replace every pixel channel value in the image at once using the fast lookup table
    return cv2.LUT(image, table)


# Card outline detection and perspective straightening (Homography)

def transform_homography(image, imgName):
    """
    Find the largest four corner shape (such as an ID card) and warp it flat
    into a straight view.

    Parameters:
    - image: Resized and gamma adjusted BGR image array.
    - imgName: Base filename (without .jpg) used when saving debug images to output/.

    Returns:
    - Straightened 800x800 card image if at least 4 corners are found;
      otherwise returns the unwarped input image.
    """
    # Convert the colour image (BGR) to a grayscale image for edge detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Find sharp brightness changes (edges) using lower threshold 50 and upper threshold 150
    edges = cv2.Canny(gray, 50, 150)

    # Trace outer boundaries (RETR_EXTERNAL) of connected edges and compress straight segments
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)

    # Pick the single contour covering the largest pixel area in the frame
    contour = max(contours, key=cv2.contourArea)

    # Simplify the jagged outline into straight lines 2% of perimeter controls corner sensitivity
    epsilon = 0.02 * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)

    # Proceed only if the simplified outline has at least 4 corner points
    if len(approx) >= 4:
        # Unwrap OpenCV's nested [[x, y]] shape into a clean (N, 2) table of [x, y] points
        points = np.array([point[0] for point in approx], dtype="float32")

        # Sum (x + y) and difference (y - x) let us spot the 4 extreme corners:
        # - Top left has the smallest (x + y)
        # - Bottom right has the largest (x + y)
        # - Top right has the smallest (y - x)
        # - Bottom left has the largest (y - x)
        s = points.sum(axis=1)
        diff = np.diff(points, axis=1)

        top_left = points[np.argmin(s)]
        bottom_right = points[np.argmax(s)]
        top_right = points[np.argmin(diff)]
        bottom_left = points[np.argmax(diff)]

        # Order the 4 detected corners clockwise starting at top left
        src_pts = np.array([top_left, top_right, bottom_right, bottom_left],
                           dtype="float32")

        # Draw a green 3 pixel border directly onto the image to show which outline was chosen
        cv2.polylines(image, [src_pts.astype(int)], isClosed=True,
                      color=(0, 255, 0), thickness=3)

        # Save a debug image showing the detected green border
        cv2.imwrite(f"output/{imgName}_original_with_contour.jpg", image)

        # Target corner positions (in pixels) inside an 800x800 output square, in the same clockwise order
        dst = np.array([
            [100, 100],  # Top left corner
            [650, 100],  # Top right corner
            [650, 650],  # Bottom right corner
            [100, 650]   # Bottom left corner
        ], dtype="float32")

        # Calculate the 3x3 perspective matrix mapping src_pts onto dst
        homography_matrix, _ = cv2.findHomography(src_pts, dst)

        # Stretch and straighten the angled card onto a flat 800x800 image
        warped_image = cv2.warpPerspective(image, homography_matrix, (800, 800))

        # Save the straightened card view to output/
        cv2.imwrite(f"output/{imgName}_transformed_card.jpg", warped_image)

        return warped_image
    else:
        # Fallback when the largest outline had fewer than 4 corners
        print("Failed to find enough corners.")
        return image


# card face cropper (Haar Cascade)

def detect_face(img, imgName):
    """
    Detect and crop the first frontal face found in an image using OpenCV's
    classic Haar Cascade XML model.

    Parameters:
    - img: BGR image to search for a face (such as the straightened card).
    - imgName: Base filename used to name the saved face crop in output/.
    """
    # Haar Cascades operate on single channel grayscale intensity values
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Load OpenCV's built in frontal face XML detector from cv2.data.haarcascades
    face_classifier = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    # Scan the image at multiple scales for face rectangles:
    # - scaleFactor=1.1 shrinks the search image by 10% per pass
    # - minNeighbors=5 requires 5 overlapping detections to reduce false alarms
    # - minSize=(40, 40) ignores candidates smaller than 40x40 pixels
    face = face_classifier.detectMultiScale(
        gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40)
    )

    # Unpack the first detected rectangle: top left (x, y), width (w) and height (h)
    # Note: raises IndexError if no face was found (caught by try/except in the main loop)
    (x, y, w, h) = face[0]

    # Slice rows (y to y+h) and columns (x to x+w) out of the colour image
    cropped_face = img[y:y + h, x:x + w]

    # Save the cropped face to output/
    cv2.imwrite(f"output/{imgName}_onlyface_result.jpg", cropped_face)



# Student number extraction (Tesseract OCR) and Excel class list check

def optical_character_recognition(image):
    """
    Read text from an image using Tesseract OCR and return all 8 digit numbers found.

    Parameters:
    - image: Full resolution BGR image array containing a student ID card.

    Returns:
    - A Python list of 8 character digit strings (for example ['12345678']).
    """
    # Point pytesseract directly to the installed Windows Tesseract executable
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    # Extract all readable text from the image into one Python string
    string = pytesseract.image_to_string(image)

    # Find every consecutive run of digits (\d+) anywhere in the OCR text as strings
    all_numbers = re.findall(r'\d+', string)

    # Keep only digit strings that are 8 digits long (matching Maynooth student number length)
    # Keeping them as strings preserves any leading zeros
    numbers = [n for n in all_numbers if len(n) == 8]
    return numbers
