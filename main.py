import cv2   
import glob  
import os   
import sys   

# - os.path.abspath(__file__) turns it into a full path
# - os.path.dirname(...) gets the folder containing main.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import card cleanup and 8 digit OCR functions from card_ocr.py
from card_ocr import (
    adjust_gamma,
    transform_homography,
    detect_face,
    optical_character_recognition,
)

# Import YuNet + SFace model and student face profile helpers from face_profiles.py
from face_profiles import (
    detect_live_faces,
    load_face_models,
    load_student_profiles,
    match_face_to_profile,
    save_face_to_profile,
)

# Import Excel class list helpers from attendance.py
from attendance import (
    check_class_list,
    load_class_list,
)


def run_photo_pipeline(image_folder="input"):
    """
    Process all still .jpg card photos inside image_folder, collect every 8 digit
    student number found by OCR into a set, save warped card/face debug images
    into output/, and check the collected numbers once against class_list.xlsx.
    """
    # Stop early with a clear message if the input folder is missing
    if not os.path.exists(image_folder):
        print(f"Error: The specified folder '{image_folder}' does not exist. Please check the path and try again.")
        return

    # Collect all .jpg file paths directly inside input/
    image_files = glob.glob(f"{image_folder}/*.jpg")

    if not image_files:
        print(f"Error: No .jpg images found in the folder '{image_folder}'. Please ensure the folder contains .jpg files.")
        return

    # Make sure output/ exists so cv2.imwrite() never silently fails to save images
    os.makedirs("output", exist_ok=True)

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
        image = cv2.resize(
            image,
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
    check_class_list(detected_numbers)


def main():
    """
    Program startup function:
    1. Loads YuNet and SFace models once into memory.
    2. Loads any saved student face profiles from input/students/faces/ (empty on Day 1).
    3. Loads the student number -> name dictionary from input/students/class_list.xlsx.
    4. Runs the processing pipeline (currently still photos).
    """
    detector, recognizer = load_face_models()
    profiles = load_student_profiles(detector, recognizer)
    students = load_class_list()
    print(f"Startup ready: {len(students)} students in class list, {len(profiles)} saved face profiles.")

    run_photo_pipeline("input")


# Standard Python entry guard:
# - When you run `python main.py` directly, Python sets __name__ to "__main__", so main() runs.
#   run automatically on import.
if __name__ == "__main__":
    main()
