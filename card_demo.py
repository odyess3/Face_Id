"""A learning demo for card images. Start with README.md, then read down this file.

Inspired by the three techniques in Daniel Lepold's article linked in README.md.
This is a fresh teaching implementation with local folders and video sampling.
It finds possible shapes and faces; it does not identify students or take attendance.
"""

import argparse
import csv
from datetime import datetime
import math
from pathlib import Path

import cv2
import numpy as np


# 1. FOLDERS: resolve paths beside this file, even if the terminal is elsewhere.
# Copy your own files into input/photos or input/videos. No website upload is needed.
PROJECT = Path(__file__).resolve().parent
INPUT = PROJECT / "input"
OUTPUT = PROJECT / "output"
PHOTO_TYPES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
VIDEO_TYPES = {".mp4", ".mov", ".avi", ".mkv", ".m4v"}


def save_image(path, image):
    """Save an image and report a failed write instead of silently losing output."""
    # Encoding to bytes also supports Windows folder names with accented characters.
    success, encoded = cv2.imencode(".jpg", image)
    if not success:
        raise OSError(f"Could not encode {path}")
    path.write_bytes(encoded.tobytes())


def adjust_gamma(image, gamma):
    """2. BRIGHTNESS: gamma 1 leaves it alone; values above 1 brighten it."""
    # Pixels are numbers from 0 (black) to 255 (white).
    # Build a table of replacement values, then apply it to every pixel.
    levels = np.arange(256, dtype=np.float64) / 255.0
    table = np.clip(255 * np.power(levels, 1 / gamma), 0, 255).astype(np.uint8)
    return cv2.LUT(image, table)


def find_card(image):
    """3. SHAPE: return one possible card boundary, plus an edge image to inspect."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # A small blur reduces tiny noisy edges. Canny highlights changes in brightness.
    edges = cv2.Canny(cv2.GaussianBlur(gray, (5, 5), 0), 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    image_area = image.shape[0] * image.shape[1]

    # A contour is an outline. Try the largest outlines first.
    # A book, screen or other rectangle can also pass these checks: inspect the output.
    for contour in sorted(contours, key=cv2.contourArea, reverse=True):
        if cv2.contourArea(contour) < image_area * 0.02:
            continue
        perimeter = cv2.arcLength(contour, True)
        polygon = cv2.approxPolyDP(contour, perimeter * 0.02, True)
        if len(polygon) == 4 and cv2.isContourConvex(polygon):
            return polygon.reshape(4, 2).astype(np.float32), edges
    # An empty image or a missing card is a normal result, not a crash.
    return None, edges


def straighten_card(image, corners):
    """4. PERSPECTIVE: map four corners onto a rectangle without forcing a square."""
    # Sort the corners around their centre, then start at the upper left.
    # This avoids selecting the same corner twice with sum/difference rules.
    centre = corners.mean(axis=0)
    angles = np.arctan2(corners[:, 1] - centre[1], corners[:, 0] - centre[0])
    ordered = corners[np.argsort(angles)]
    ordered = np.roll(ordered, -int(np.argmin(ordered.sum(axis=1))), axis=0)
    top_left, top_right, bottom_right, bottom_left = ordered

    # Estimate dimensions from the visible sides. Exact physical proportions would
    # need the actual card layout or camera information, which we have not established.
    width = round(max(np.linalg.norm(top_right - top_left),
                      np.linalg.norm(bottom_right - bottom_left)))
    height = round(max(np.linalg.norm(bottom_left - top_left),
                       np.linalg.norm(bottom_right - top_right)))
    if min(width, height) < 2:
        raise ValueError("The possible card is too small to straighten")
    destination = np.float32([[0, 0], [width - 1, 0],
                              [width - 1, height - 1], [0, height - 1]])
    matrix = cv2.getPerspectiveTransform(ordered, destination)
    return cv2.warpPerspective(image, matrix, (width, height))


def detect_faces(card, classifier):
    """5. FACE: locate possible faces inside the crop, without recognising anyone."""
    gray = cv2.cvtColor(card, cv2.COLOR_BGR2GRAY)
    # Haar cascade = a supplied face detector. It can miss faces or make mistakes.
    return classifier.detectMultiScale(gray, scaleFactor=1.1,
                                       minNeighbors=5, minSize=(30, 30))


def process_image(image, folder, gamma, classifier):
    """Save each visible step for one photo or sampled video frame."""
    folder.mkdir(parents=True)
    save_image(folder / "01_original.jpg", image)
    bright = adjust_gamma(image, gamma)
    save_image(folder / "02_brightness.jpg", bright)
    corners, edges = find_card(bright)
    save_image(folder / "03_edges.jpg", edges)

    if corners is None:
        return "no_card_candidate", 0

    # Draw on a COPY so green lines never get added to the crop used by the detector.
    outline = bright.copy()
    cv2.polylines(outline, [corners.astype(np.int32)], True, (0, 255, 0), 3)
    save_image(folder / "04_possible_card_outline.jpg", outline)
    card = straighten_card(bright, corners)
    save_image(folder / "05_straightened_candidate.jpg", card)

    faces = detect_faces(card, classifier)
    preview = card.copy()
    for index, (x, y, width, height) in enumerate(faces, start=1):
        save_image(folder / f"face_{index:02d}.jpg", card[y:y + height, x:x + width])
        cv2.rectangle(preview, (x, y), (x + width, y + height), (0, 255, 0), 2)
    save_image(folder / "06_face_detection.jpg", preview)
    return "card_candidate" if len(faces) else "candidate_no_face", len(faces)


def read_video(path, interval, limit):
    """Yield sampled frames, their frame numbers and estimated video times."""
    capture = cv2.VideoCapture(str(path))
    try:
        if not capture.isOpened():
            raise ValueError("Cannot open video. Try converting it to an H.264 MP4.")
        fps = capture.get(cv2.CAP_PROP_FPS)
        if not math.isfinite(fps) or fps <= 0:
            raise ValueError("Cannot determine video frame rate; no timestamps guessed")
        # At 30 frames per second, interval 1 means sample roughly every 30 frames.
        step = max(1, round(fps * interval))
        frame_number = 0
        sampled = 0
        while limit == 0 or sampled < limit:
            success, frame = capture.read()
            if not success:
                if frame_number == 0:
                    raise ValueError("Video opened but no frames could be decoded")
                break
            if frame_number % step == 0:
                yield frame, frame_number, frame_number / fps
                sampled += 1
            frame_number += 1
    finally:
        capture.release()


def main():
    """6. RUN: collect inputs, process them and write a processing summary."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=INPUT,
                        help="A photo, video or folder; default: this project's input folder")
    parser.add_argument("--output", type=Path, default=OUTPUT,
                        help="Where to create a new results folder")
    parser.add_argument("--gamma", type=float, default=1.5)
    parser.add_argument("--interval", type=float, default=1.0,
                        help="Seconds between sampled video frames")
    parser.add_argument("--max-frames", type=int, default=30,
                        help="Maximum samples per video; 0 means no limit")
    args = parser.parse_args()
    if not math.isfinite(args.gamma) or args.gamma <= 0:
        parser.error("--gamma must be a finite number greater than zero")
    if not math.isfinite(args.interval) or args.interval <= 0 or args.max_frames < 0:
        parser.error("--interval must be positive and finite; --max-frames must be 0 or more")

    for name in ("photos", "videos"):
        (INPUT / name).mkdir(parents=True, exist_ok=True)
    source = args.input.resolve()
    if not source.exists():
        parser.error(f"Input does not exist: {source}")
    files = sorted(source.rglob("*")) if source.is_dir() else [source]
    files = [path for path in files if path.is_file()
             and path.suffix.lower() in PHOTO_TYPES | VIDEO_TYPES]
    if not files:
        print(f"No supported photos or videos found in {source}")
        print(f"Copy photos to {INPUT / 'photos'}")
        print(f"Copy videos to {INPUT / 'videos'}, then run again.")
        return 0

    classifier = cv2.CascadeClassifier(
        str(Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"))
    if classifier.empty():
        raise RuntimeError("OpenCV's supplied face detector could not be loaded")

    # A new dated folder prevents a later run overwriting earlier results.
    run_folder = args.output.resolve() / datetime.now().strftime("run_%Y%m%d_%H%M%S_%f")
    run_folder.mkdir(parents=True)
    fields = ["source", "frame_number", "estimated_seconds", "status", "face_count",
              "result_folder", "note"]
    had_errors = False
    with (run_folder / "processing_summary.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for number, path in enumerate(files, start=1):
            print(f"Processing {path.name}")
            destination = run_folder / f"{number:03d}_{path.stem}_{path.suffix[1:].lower()}"
            try:
                if path.suffix.lower() in PHOTO_TYPES:
                    image = cv2.imdecode(np.frombuffer(path.read_bytes(), dtype=np.uint8), cv2.IMREAD_COLOR)
                    if image is None:
                        raise ValueError("Cannot read this photo; check its contents and format")
                    samples = [(image, None, None)]
                else:
                    samples = read_video(path, args.interval, args.max_frames)

                for image, frame_number, seconds in samples:
                    folder = destination if frame_number is None else destination / f"frame_{frame_number:06d}"
                    status, count = process_image(image, folder, args.gamma, classifier)
                    writer.writerow(dict(source=str(path), frame_number=frame_number,
                                         estimated_seconds="" if seconds is None else f"{seconds:.3f}",
                                         status=status, face_count=count, result_folder=str(folder),
                                         note="Shape and face candidates only; inspect the saved images"))
                    handle.flush()
            except (OSError, ValueError, cv2.error) as error:
                had_errors = True
                writer.writerow(dict(source=str(path), status="error", note=str(error)))
                print(f"  Could not finish {path.name}: {error}")

    print(f"Results saved to: {run_folder}")
    print("Open processing_summary.csv and the numbered images. This is not an attendance list.")
    return 1 if had_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
