# Article practice script

`article_face_detection.py` is a snapshot of Ody's separate `D:\Face_id_test\face_detection.py` practice script, copied on 21 November 2026. The source in that folder is preserved. Changes there do not automatically update this copy.

It follows [Daniel Lepold's article](https://medium.com/@daniel.lepold/image-processing-in-python-gamma-correction-homography-transformation-and-face-detection-with-7c806a587186). The main `card_demo.py` is the separately rewritten learning demo with more input formats, video sampling, numbered outputs and missing detection handling.

To run the article practice script from the repository root, place JPG files directly inside `input`, then run:

```powershell
.\.venv-card-demo\Scripts\python.exe .\examples\article_face_detection.py
```

This script uses `input/*.jpg`, so it does not search the `input/photos` subfolder. Its output JPG files are saved in the current working folder. Photos, videos, generated results and Python environments are excluded from Git.

The article method selects the largest contour, forces a square perspective result and saves the first detected face. A printed completion message does not guarantee a correct card or face crop. This example does not read student numbers or create attendance records.
