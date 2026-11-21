# Initial project research

Project: Efficiently taking attendance in large lectures using student ID cards and computer vision

Written on 4 November 2026, following the user's account of the meeting on Friday 23 October 2026.

## First goal

Build a first version that processes a recorded lecture entrance video, identifies students from their ID cards and creates an attendance list for that lecture. Face comparison and checks against people presenting someone else's card are possible later stages.

The proposed first version assumes that the card has a visible student number or another readable unique identifier. The card layout, identifier format and availability of a class list have not yet been confirmed.

## What the linked article contributes

Daniel Lepold's article demonstrates three steps: adjusting brightness, correcting perspective and extracting a face from a still image. Perspective correction makes an angled card look more like a front facing rectangle. Face detection locates a face; it does not establish whose face it is.

The example does not read student numbers, process lecture video or create attendance records. Its largest contour rule assumes the card is the dominant shape. My assessment is that this could select the wrong object in a crowded entrance. It also stretches images into a square and accesses the first detected face without checking whether a face was found. These choices need review before reuse.

Source: [Face Detection from ID Cards in Python using OpenCV: Gamma Correction & Homography](https://medium.com/@daniel.lepold/image-processing-in-python-gamma-correction-homography-transformation-and-face-detection-with-7c806a587186), published 14 March 2025.

The user described this as an example from America. The article itself has not established that it is a deployed American lecture attendance system.

## A proposed first approach

This is a research proposal, not an implemented or tested system.

1. Read a short recorded video and extract frames. OpenCV supports reading a video file frame by frame with `VideoCapture`. [OpenCV video tutorial](https://docs.opencv.org/4.x/dd/d43/tutorial_py_video_display.html)
2. Find each visible card. Start with a small set of still frames to determine whether simple image processing can locate cards. If it is unreliable, investigate a trained card detector. Do not assume there is only one card in each frame.
3. Crop each card and correct its angle when its corners can be located. Keep the card's proportions. OpenCV's perspective transform maps four source points to four destination points. [OpenCV perspective transformation tutorial](https://docs.opencv.org/4.x/da/d6e/tutorial_py_geometric_transformations.html)
4. Read the student number using optical character recognition, usually called OCR. OCR converts text in an image into text the program can use. PaddleOCR is one candidate with a documented text recognition pipeline; no OCR tool has been selected or tested on this footage. [PaddleOCR quick start](https://www.paddleocr.ai/main/en/quick_start.html)
5. Check the result against the expected student number format and, if available, the class list. Membership of a class list alone should not be treated as proof that a reading is correct. Unclear or conflicting readings should go to review.
6. Combine repeated observations across nearby frames, so a brief blurred view can be supported by a clearer view of the same card. Keep different cards separate.
7. Record each accepted student number once per lecture. A proposed output is a CSV containing the lecture identifier, student number, first accepted video timestamp and review status.

This baseline records evidence that a student's card was presented. It does not yet verify that the person holding it is the card owner. Failure to read a card should be recorded as unresolved rather than automatically treated as proof of absence.

## First experiment

Before training a model, inspect roughly 20 to 30 representative still frames from the actual recording. This is a suggested starting sample, not a claim about the size of the dataset.

Include clear single cards, several cards together, cards held at an angle, partial cards, glare and motion blur. Some of these are conditions to check, rather than problems already observed by the assistant.

For each card, manually note whether its student number can be read. If it cannot be read by a person at the original resolution, brightness changes and straightening should not be assumed to recover the missing detail. The first question is whether the footage contains enough detail for identification.

Then test reading a manually cropped clear card. This separates difficulty finding the card from difficulty reading its text. Follow with automatic card detection and a short video trial if the still image experiment works.

Compare results with a manually checked reference list for the same clip. Record correct student numbers, incorrect student numbers, missed readable cards, duplicate attendance records and unresolved cases. Keep a separate clip or lecture for later evaluation; neighbouring frames from the same recording are too similar to provide a strong independent test.

## Current workspace findings

The existing file `daniel_lepold_face` contains Python functions for gamma adjustment and perspective correction. Its contents were read, but not executed.

- The import line says `import osen`. This appears to be a typo for `import os`; the intended module has not been confirmed.
- `max(contours, key=cv2.contourArea)` has no empty contour check.
- The code draws the outline directly onto the image before transforming it. A later implementation should keep visual annotations on a separate copy so they do not affect text reading.
- There is no main processing loop, video reader, OCR step or attendance output in this file.

The file was left unchanged. No packages were installed and no accuracy or runtime results are available. No recording or sample ID image was present in the workspace's top level file listing; no actual footage was inspected by the assistant.

## Questions to resolve with the professor

- Is the intended identifier printed text, a barcode or another feature on the card?
- Are there several card designs, and is a class list available for checking results?
- What does a readable card look like at the original video resolution?
- What output format and lecture identifiers should the first version use?
- How should unclear cases be reviewed, and what error rate would make the prototype useful?
