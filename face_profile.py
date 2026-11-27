import cv2
import glob
import os

# OpenCV Zoo (YuNet + SFace) settings for progressive student face profiles

Yunet_model = "model/face_detection_yunet_2026may.onnx"     # YuNet neural network file that locates faces + 5 landmarks
Sface_model = "model/face_recognition_sface_2021dec.onnx"   # SFace neural network file that creates 128 number face fingerprints
Profiles_dir = "input/students/faces"                       # Folder where each student's face samples will be stored by ID number
Cosine_threshold = 0.363      # Minimum SFace cosine similarity score (0.363+) to count two faces as the same person
Min_live_face_size = 80       # Minimum width and height in pixels so tiny printed ID card photos are ignored
Max_samples_per_student = 5   # Maximum clear face crops saved per student over time


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


# - load_student_profiles(...)               (lines 323 to 364)
# - match_face_to_profile(...)               (lines 367 to 389)
# - save_face_to_profile(...)                (lines 392 to 425)