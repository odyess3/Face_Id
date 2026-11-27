# Library imports

import numpy as np
from PIL import Image
import pytesseract
import cv2
import pandas as pd
import re
import glob
import os


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



# Legacy card face cropper (Haar Cascade)

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



# OpenCV Zoo (YuNet + SFace) settings for progressive student face profiles

Yunet_model = "model/face_detection_yunet_2026may.onnx"     # YuNet neural network file that locates faces + 5 landmarks
Sface_model = "model/face_recognition_sface_2021dec.onnx"   # SFace neural network file that creates 128 number face fingerprints
Profiles_dir = "input/students/faces"                       # Folder where each student's face samples will be stored by ID number
Cosine_threshold = 0.363      # Minimum SFace cosine similarity score (0.363+) to count two faces as the same person
Min_live_face_size = 80       # Minimum width and height in pixels so tiny printed ID card photos are ignored
Max_samples_per_student = 5   # Maximum clear face crops saved per student over time



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


def check_class_list(detected_numbers):
    """
    Compare all 8 digit student numbers collected across the session against
    the Excel class list once, and print whether each student was detected.

    Parameters:
    - detected_numbers: A Python set of unique 8 digit student number strings.
    """
    # Load the class list sheet:
    # - dtype={"Student number": str} keeps student numbers as text so leading zeros are never dropped
    # - keep_default_na=False keeps empty cells as "" instead of turning them into NaN
    df = pd.read_excel(
        r"input\students\class_list.xlsx",
        engine="openpyxl",
        dtype={"Student number": str},
        keep_default_na=False
    )

    # Check each student row in the Excel table one by one
    for index, row in df.iterrows():
        # Remove accidental spaces before or after the student number
        student_number = row["Student number"].strip()

        # Skip any blank row in the spreadsheet
        if not student_number:
            continue

        # Report whether this student's number appeared in any processed image
        if student_number in detected_numbers:
            print(
                f"Student NO: {student_number}, "
                f"Name: {row['Student name']} was detected"
            )
        else:
            print(
                f"Student NO: {student_number}, "
                f"Name: {row['Student name']} was not detected"
            )



# OpenCV Zoo face detection (YuNet) and embedding extraction (SFace)

def load_face_models():
    """
    Load the YuNet face detector and SFace face recognizer once at program startup.

    Returns:
    - (detector, recognizer): Ready to use OpenCV FaceDetectorYN and FaceRecognizerSF objects.
    """
    # Create YuNet detector:
    # - (320, 320) is a placeholder input size updated per frame in detect_live_faces()
    # - score_threshold=0.8 keeps only detections with at least 80% face confidence
    # - nms_threshold=0.3 suppresses overlapping duplicate boxes on the same face
    detector = cv2.FaceDetectorYN.create(
        Yunet_model, "", (320, 320), score_threshold=0.8, nms_threshold=0.3
    )

    # Create SFace recognizer that aligns faces to 112x112 and computes 128 number embeddings
    recognizer = cv2.FaceRecognizerSF.create(Sface_model, "")
    return detector, recognizer


def detect_live_faces(image, detector, recognizer, min_size=Min_live_face_size):
    """
    Detect real sized faces in an image or video frame, align each face using its
    5 facial landmarks (eyes, nose and mouth corners), and extract its 128 number fingerprint.

    Parameters:
    - image: BGR frame or photo as a NumPy array.
    - detector: Loaded YuNet FaceDetectorYN object.
    - recognizer: Loaded SFace FaceRecognizerSF object.
    - min_size: Minimum face box width/height in pixels (skips tiny printed photos on ID cards).

    Returns:
    - A list of dictionaries, one per real face, containing:
      "bbox": (x, y, w, h) pixel coordinates in the original frame,
      "aligned": 112x112 straightened face image ready to save to a profile folder,
      "embedding": (1, 128) float array representing that person's facial fingerprint.
    """
    # NumPy image.shape gives (height, width, channels), whereas setInputSize expects (width, height)
    height, width, _ = image.shape
    detector.setInputSize((width, height))

    # Run YuNet on the frame; faces is None when nobody is in front of the camera
    _, faces = detector.detect(image)

    results = []
    if faces is None:
        return results

    # Each row in faces has 15 numbers: [x, y, w, h, 10 landmark coordinates, confidence_score]
    for face in faces:
        # Convert the bounding box coordinates (first 4 values) to whole pixel integers
        x, y, w, h = map(int, face[:4])

        # Ignore tiny faces (such as the small passport portrait printed on a held up ID card)
        if w < min_size or h < min_size:
            continue

        # Rotate and crop the face into a standard 112x112 square using YuNet's 5 landmarks
        aligned_face = recognizer.alignCrop(image, face)

        # Turn the aligned 112x112 face into its 128 number SFace fingerprint vector
        embedding = recognizer.feature(aligned_face)

        results.append({
            "bbox": (x, y, w, h),
            "aligned": aligned_face,
            "embedding": embedding,
        })

    return results


# Student face profile loading, matching and progressive saving

def load_student_profiles(detector, recognizer, profiles_dir=Profiles_dir):
    """
    Load any saved student face profiles from input/students/faces/ at startup.
    On Lecture 1 this returns an empty dictionary {}; on later runs it loads each
    student's saved 112x112 face crops and turns them into 128 number fingerprints.

    Parameters:
    - detector: Loaded YuNet FaceDetectorYN object (used if a full photo is in a folder).
    - recognizer: Loaded SFace FaceRecognizerSF object.
    - profiles_dir: Root folder holding one subfolder per 8 digit student number.

    Returns:
    - Dictionary mapping student_number (str) -> list of (1, 128) embedding arrays.
    """
    profiles = {}
    # Create input/students/faces/ automatically if it does not exist yet
    os.makedirs(profiles_dir, exist_ok=True)

    # Check each item inside input/students/faces/ (each subfolder name is a student number)
    for student_number in os.listdir(profiles_dir):
        student_folder = os.path.join(profiles_dir, student_number)
        if not os.path.isdir(student_folder):
            continue

        embeddings = []
        # Read every saved .jpg face sample for this student in sorted order
        for img_path in sorted(glob.glob(os.path.join(student_folder, "*.jpg"))):
            img = cv2.imread(img_path)
            if img is None:
                continue

            # Crops saved by save_face_to_profile() are already aligned to 112x112 pixels
            if img.shape[:2] == (112, 112):
                embeddings.append(recognizer.feature(img))
            else:
                # Fallback if someone manually placed an uncropped photo in the student's folder
                found = detect_live_faces(img, detector, recognizer, min_size=30)
                if found:
                    embeddings.append(found[0]["embedding"])

        if embeddings:
            profiles[student_number] = embeddings

    return profiles


def match_face_to_profile(live_embedding, saved_embeddings, recognizer):
    """
    Compare a live face fingerprint from the video against all saved fingerprints
    for one student, and check whether the highest cosine similarity beats 0.363.

    Parameters:
    - live_embedding: (1, 128) fingerprint of the face seen in the current frame.
    - saved_embeddings: List of (1, 128) fingerprints stored for this student.
    - recognizer: Loaded SFace FaceRecognizerSF object.

    Returns:
    - (is_match, best_score): Boolean match result and highest similarity score found.
    """
    best_score = -1.0

    # Compare against every saved sample for this student (up to Max_samples_per_student)
    for saved_emb in saved_embeddings:
        score = float(
            recognizer.match(saved_emb, live_embedding, cv2.FaceRecognizerSF_FR_COSINE)
        )
        if score > best_score:
            best_score = score

    # OpenCV's SFace benchmark counts cosine scores of 0.363 or above as the same person
    return best_score >= Cosine_threshold, best_score


def save_face_to_profile(student_number, face_data, profiles, profiles_dir=Profiles_dir):
    """
    Save a clear aligned 112x112 face crop into a student's profile folder and add
    its fingerprint to memory, up to Max_samples_per_student samples total.

    Parameters:
    - student_number: 8 digit student number string (used as the subfolder name).
    - face_data: Dictionary from detect_live_faces() containing "aligned" and "embedding".
    - profiles: In memory dictionary of student profiles updated immediately.
    - profiles_dir: Root folder holding student profile subfolders.

    Returns:
    - True if a new sample was saved; False if the student already reached the sample limit
      or writing the image failed.
    """
    student_folder = os.path.join(profiles_dir, student_number)
    os.makedirs(student_folder, exist_ok=True)

    # Get this student's existing list of fingerprints, or start a new empty list
    existing = profiles.setdefault(student_number, [])

    # Stop saving once we already have enough clear samples (default 5) for this student
    if len(existing) >= Max_samples_per_student:
        return False

    sample_num = len(existing) + 1
    save_path = os.path.join(student_folder, f"sample_{sample_num}.jpg")

    # Save the 112x112 aligned crop to disk and store the fingerprint in memory right away
    if cv2.imwrite(save_path, face_data["aligned"]):
        existing.append(face_data["embedding"])
        return True
    return False



# Current main loop: process still .jpg images in input/ and check class list

image_folder = "input"

# Stop early with a clear message if the input folder is missing
if not os.path.exists(image_folder):
    print(f"Error: The specified folder '{image_folder}' does not exist. Please check the path and try again.")
else:
    # Collect all .jpg file paths directly inside input/
    image_files = glob.glob(f"{image_folder}/*.jpg")

    if not image_files:
        print(f"Error: No .jpg images found in the folder '{image_folder}'. Please ensure the folder contains .jpg files.")
    else:

      # Use a set so if the same student's card appears in multiple photos, their number is stored once
      detected_numbers = set()
      
      # Loop through every found .jpg photo one at a time
      for imgpath in image_files:
          
          print(f"Processing of {imgpath} has started.")
          # Pull just the filename without folder or ".jpg" (e.g. "input/IMG_7857.jpg" -> "IMG_7857")
          imgname = os.path.splitext(os.path.basename(imgpath))[0]

          # Load the image from disk as a BGR NumPy array (returns None if unreadable)
          image = cv2.imread(imgpath)

          if image is None:
              print(f"Unable to read image: {imgpath}")
              continue

          # Copy the full resolution image for OCR before resizing shrinks fine text details
          image_text = image.copy()

          # Extract 8 digit student numbers from this photo and add them to the session set
          numbers = optical_character_recognition(image_text)
          detected_numbers.update(numbers)

          # Resize to 800x800 and brighten to prepare for card contour and homography detection
          image = cv2.resize(image,
              (800, 800),
              interpolation=cv2.INTER_AREA,
          )

          image = adjust_gamma(image, gamma=1.5)

          try:
              # Find the card border and warp it flat, saving debug images to output/
              transformed = transform_homography(image, imgname)
          except Exception as e:
              # If contour detection fails (e.g. blank image with no contours), skip to the next image
              print(f"Homography error for image {imgname}: {e}")
              continue

          try:
              # Crop the first Haar Cascade face found on the warped card image
              detect_face(transformed, imgname)
          except Exception as e:
              # Caught when detectMultiScale finds zero faces (face[0] raises IndexError)
              print(f"Face detection error for image {imgname}: {e}")

          print(f"Processing of {imgname} has been completed.")

      # Outside the image loop: compare all collected student numbers against class_list.xlsx once
ption as e:
              # Log the error if face detection fails
              print(f"Face detection error for image {imgname}: {e}")


          
          # Log the completion of processing for the current image
          print(f"Processing of {imgname} has been completed.")
      check_class_list(detected_numbers)
