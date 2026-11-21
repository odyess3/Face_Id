# Card image learning demo

This puts the techniques from [Daniel Lepold's article](https://medium.com/@daniel.lepold/image-processing-in-python-gamma-correction-homography-transformation-and-face-detection-with-7c806a587186) into a runnable Python learning example. The code is in `card_demo.py`, with numbered sections and plain English comments. Video sampling and the folder arrangement are additions for this project. The original `daniel_lepold_face` fragment is preserved.

## Where to put your photos and videos

There is no website upload button. Copy files from your phone or computer into these folders, using File Explorer or the VS Code Explorer:

| Your file | Put it here |
| --- | --- |
| Card photo, such as `my_card.jpg` | `D:\Face_Id\input\photos` |
| Card video, such as `card_clip.mp4` | `D:\Face_Id\input\videos` |
| Results made by the program | `D:\Face_Id\output` |

Start with one clear photo, showing the whole card against a plain background. The method tries one large rectangular shape per image, so it can choose the wrong object in a busy scene. It does not yet handle all the cards in a lecture entrance video.

Photos can be JPG, JPEG, PNG, BMP or WEBP. Videos can be MP4, MOV, AVI, MKV or M4V if OpenCV can decode their contents. A file extension alone does not guarantee support. If an iPhone photo is HEIC, export a JPEG first. If a video fails, try exporting an H.264 MP4.

## Run it in VS Code

1. Open the `D:\Face_Id` folder in VS Code.
2. Copy a photo or video into the matching input folder.
3. Press **Ctrl+Shift+B** to run **Run card learning demo**. This task uses the prepared Python environment directly and does not require activation.
4. Read the terminal message that starts **Results saved to:**.
5. Open that new folder inside `output` and click the images to inspect them.

You can also use **Terminal > New Terminal** and run:

```powershell
cd D:\Face_Id
.\.venv-card-demo\Scripts\python.exe .\card_demo.py
```

If you use the Python extension's **Run Python File** button, choose **Python: Select Interpreter** from Ctrl+Shift+P and select `D:\Face_Id\.venv-card-demo\Scripts\python.exe`. The workspace supplies this as the default, but VS Code may remember an older selection.

With empty input folders, the program tells you where to copy files. It does not produce demonstration results from nonexistent inputs.

## Where the output appears

Each run with supported input files creates a new folder, for example:

```text
D:\Face_Id\output\run_20261118_143000_123456\
    processing_summary.csv
    001_my_card_jpg\
        01_original.jpg
        02_brightness.jpg
        03_edges.jpg
        04_possible_card_outline.jpg
        05_straightened_candidate.jpg
        06_face_detection.jpg
        face_01.jpg
```

This is an example layout, not a promise that a face will be found. The program creates the outline and card crop only when it finds a candidate. It creates `face_01.jpg`, and any further face crops, only when the face detector returns candidates. Originals in `input` are not modified.

| File | What to learn from it |
| --- | --- |
| `01_original.jpg` | The input view, saved as a JPEG for comparison |
| `02_brightness.jpg` | What the brightness setting changed |
| `03_edges.jpg` | Outlines found by changes in brightness |
| `04_possible_card_outline.jpg` | The shape selected as a possible card, marked in green |
| `05_straightened_candidate.jpg` | The selected shape after correcting its perspective |
| `06_face_detection.jpg` | Any possible faces marked inside that crop |
| `face_01.jpg` | A separate crop of a possible face |
| `processing_summary.csv` | Input paths, frame numbers, estimated times, statuses, face counts and result folders |

Open the CSV in VS Code or Excel. `no_card_candidate` means no suitable four sided outline was found. `candidate_no_face` means a shape was found but no face was detected. `card_candidate` means both a possible shape and at least one possible face were found. These labels do not establish that the shape is an ID card or that the face detector is correct. `error` records a file the program could not finish.

## What happens to videos

A video is a sequence of pictures called frames. This demo processes selected frames using the same steps as a photo. By default it samples roughly one frame per second and stops after 30 samples per video, covering roughly the first 30 seconds of a long clip. It saves a separate `frame_000000`, `frame_000030`, etc. folder inside that video's results folder; those example numbers assume 30 frames per second.

The CSV's estimated times come from frame number divided by the reported frame rate. They are approximate, especially for videos whose frame rate changes. Decode failure later in a video may look like the end of the recording, so this is not a completeness check. There is no edited output video, student tracking or attendance list.

To sample a whole clip every half second, with no sample limit:

```powershell
.\.venv-card-demo\Scripts\python.exe .\card_demo.py --interval 0.5 --max-frames 0
```

That can produce many images. To process just one file rather than everything in `input`:

```powershell
.\.venv-card-demo\Scripts\python.exe .\card_demo.py --input ".\input\photos\my_card.jpg"
```

## Read the code in this order

1. **Folders:** `Path` represents a file or folder location. `PROJECT` is the folder containing this script.
2. **Brightness:** `adjust_gamma` changes pixel values. A pixel is one small coloured point in the image. Gamma 1 keeps brightness unchanged; 1.5 brightens it.
3. **Shape:** `find_card` looks for a large outline with four corners. It is a simple geometric guess.
4. **Perspective:** `straighten_card` maps those four corners onto a rectangle. This transformation is often called a homography. It estimates proportions from visible side lengths, so it cannot guarantee the card's true physical proportions.
5. **Face:** `detect_faces` applies OpenCV's supplied Haar cascade detector to the candidate crop. This locates possible faces; it does not tell us who they belong to.
6. **Run:** `main` collects the files, calls these steps and records the results. `read_video` supplies sampled pictures when the input is a video.

For example, `card[y:y + height, x:x + width]` means keep only the rectangle starting at position `(x, y)`, with that width and height. Python array slicing takes the rows first, then the columns.

The pipeline is:

```text
input photo or video frame
  -> brightness adjustment
  -> possible card outline
  -> straightened crop
  -> possible face crops
  -> saved pictures and processing summary
```

This learning example stops before student number reading, identity checks and attendance recording. Missing detections do not prove that a student was absent. Actual card footage has not yet been used to evaluate this demo.

## Python setup

The prepared environment is `.venv-card-demo`, using Python 3.13. It contains the versions in `requirements.txt`. The earlier `.venv` is preserved. To recreate the demo environment with `uv`:

```powershell
uv venv --python 3.13 .venv-card-demo
uv pip install --python .venv-card-demo\Scripts\python.exe -r requirements.txt
```

Python environments, card photos, videos and generated results are kept locally and excluded from Git. After cloning this repository, recreate the environment using the commands above and copy your own inputs into the appropriate folders. Paths shown as `D:\Face_Id` refer to the original workspace; use your own checkout location if different.

The [article practice example](examples/README.md) also contains a snapshot of the separate `Face_id_test` script. It has different input and output conventions, explained in that folder.

## References

The article provides the three learning techniques. This implementation adds input checks, empty detection handling, separate annotation copies, estimated rectangular crop dimensions, video sampling and explicit result folders.

For the library calls, see OpenCV's official [perspective transformation tutorial](https://docs.opencv.org/4.x/da/d6e/tutorial_py_geometric_transformations.html), [video tutorial](https://docs.opencv.org/4.x/dd/d43/tutorial_py_video_display.html) and [cascade classifier tutorial](https://docs.opencv.org/4.x/db/d28/tutorial_cascade_classifier.html).

## Checks completed on 18 November 2026

Eight local tests passed using artificial images and a generated MP4. They checked brightness, missing outlines, rectangular and rotated crops, face crop file saving with a substitute detector, photo and video processing, CSV output, corrupt input handling and invalid settings. OpenCV's real detector was loaded and called during the photo and video checks, but no actual face photo or card recording was available to check its detection accuracy. These checks do not measure attendance accuracy.

To repeat the local checks:

```powershell
.\.venv-card-demo\Scripts\python.exe -m unittest -v test_card_demo
```
