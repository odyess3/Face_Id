r"""Local checks with artificial images and video, not actual student data.

Run: .\.venv-card-demo\Scripts\python.exe -m unittest -v test_card_demo
"""

import csv
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import cv2
import numpy as np

import card_demo as demo


def artificial_card():
    image = np.zeros((360, 640, 3), dtype=np.uint8)
    cv2.fillConvexPoly(image, np.int32([[100, 80], [540, 60], [560, 280], [80, 300]]),
                      (210, 210, 210))
    return image


class CardDemoChecks(unittest.TestCase):
    def test_gamma_identity_and_brightness(self):
        image = np.full((10, 10, 3), 64, np.uint8)
        np.testing.assert_array_equal(demo.adjust_gamma(image, 1), image)
        self.assertGreater(demo.adjust_gamma(image, 1.5).mean(), image.mean())

    def test_blank_image_has_no_candidate(self):
        corners, edges = demo.find_card(np.zeros((100, 100, 3), np.uint8))
        self.assertIsNone(corners)
        self.assertEqual(np.count_nonzero(edges), 0)

    def test_straightening_keeps_wide_shape_and_original_pixels(self):
        image = artificial_card()
        original = image.copy()
        corners, _ = demo.find_card(image)
        self.assertIsNotNone(corners)
        crop = demo.straighten_card(image, corners)
        self.assertGreater(crop.shape[1], crop.shape[0] * 1.5)
        self.assertGreater(crop.mean(), 190)
        np.testing.assert_array_equal(image, original)

    def test_rotated_square_does_not_repeat_corners(self):
        image = np.full((220, 220, 3), 200, np.uint8)
        corners = np.float32([[110, 10], [210, 110], [110, 210], [10, 110]])
        crop = demo.straighten_card(image, corners)
        self.assertGreater(crop.mean(), 195)

    def test_face_crop_saving_with_stub_detector(self):
        # This checks crop saving, not the accuracy of OpenCV's face detector.
        class StubDetector:
            def detectMultiScale(self, gray, **kwargs):
                return [(10, 10, 40, 45), (70, 10, 30, 35)]

        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary) / "result"
            status, count = demo.process_image(artificial_card(), folder, 1, StubDetector())
            self.assertEqual((status, count), ("card_candidate", 2))
            self.assertEqual(cv2.imread(str(folder / "face_01.jpg")).shape[:2], (45, 40))
            self.assertTrue((folder / "face_02.jpg").exists())

    def test_cli_photo_video_and_summary(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "inputs"
            source.mkdir()
            demo.save_image(source / "card.jpg", artificial_card())
            demo.save_image(source / "blank.jpg", np.zeros((360, 640, 3), np.uint8))
            video = source / "clip.mp4"
            writer = cv2.VideoWriter(str(video), cv2.VideoWriter_fourcc(*"mp4v"), 10, (640, 360))
            self.assertTrue(writer.isOpened(), "Test MP4 encoder unavailable")
            for _ in range(25):
                writer.write(artificial_card())
            writer.release()
            command = [sys.executable, str(demo.PROJECT / "card_demo.py"),
                       "--input", str(source), "--output", str(root / "results"), "--max-frames", "2"]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            summary = next((root / "results").glob("*/processing_summary.csv"))
            with summary.open(encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 4)
            self.assertEqual(rows[0]["status"], "no_card_candidate")
            self.assertEqual(rows[1]["status"], "candidate_no_face")
            self.assertEqual([row["frame_number"] for row in rows[2:]], ["0", "10"])
            self.assertEqual([row["estimated_seconds"] for row in rows[2:]], ["0.000", "1.000"])
            for row in rows:
                self.assertTrue((Path(row["result_folder"]) / "01_original.jpg").is_file())

    def test_corrupt_photo_is_reported(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            photo = root / "broken.jpg"
            photo.write_text("This is not an image", encoding="utf-8")
            result = subprocess.run([sys.executable, str(demo.PROJECT / "card_demo.py"),
                                     "--input", str(photo), "--output", str(root / "results")],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            summary = next((root / "results").glob("*/processing_summary.csv"))
            with summary.open(encoding="utf-8-sig", newline="") as handle:
                self.assertEqual(next(csv.DictReader(handle))["status"], "error")

    def test_invalid_settings_are_rejected(self):
        for arguments in (["--gamma", "0"], ["--interval", "nan"], ["--max-frames", "-1"]):
            result = subprocess.run([sys.executable, str(demo.PROJECT / "card_demo.py"), *arguments],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
