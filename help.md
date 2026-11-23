https://www.geeksforgeeks.org/computer-vision/opencv-overview/
#
OpenCV (Open Source Computer Vision Library) is an open-source library used for computer vision, image processing, and machine learning applications. It provides a comprehensive set of tools for analyzing, modifying, and understanding images and videos, making it widely used in both research and industry.

## Quick setup in VS Code

1. Open the `D:\Face_Id` folder in VS Code, then choose **Terminal > New Terminal**.
2. Install the Python packages listed in `requirements.txt`:

   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

3. Install the separate Tesseract program using the [Windows installer](https://github.com/UB-Mannheim/tesseract/wiki#tesseract-installer-for-windows). Keep the suggested folder and English language data. This is already installed on this computer.
4. Your script already tells Python where to find Tesseract:

   ```python
   import pytesseract

   pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
   ```

   `pytesseract` connects Python to Tesseract. The location line points to the program that actually reads the text.
5. Save your file, then run it from the terminal:

   ```powershell
   .\.venv\Scripts\python.exe face_detection.py
   ```

Tesseract is also saved in your user PATH, which is the list of folders Windows searches for programs. Fully close and reopen VS Code to pick up that change. The explicit location line above lets your script find Tesseract without relying on PATH.

Source: [Official pytesseract setup and examples](https://github.com/madmaze/pytesseract#usage).

