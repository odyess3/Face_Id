import pandas as pd

# Default path to the Excel class list
# The r prefix ("raw string") keeps Windows backslashes (\s, \c) literal instead of escape codes
class_list_path = r"input\students\class_list.xlsx"


def load_class_list(excel_path=class_list_path):
    """
    Read class_list.xlsx once at startup and return a fast lookup dictionary
    mapping each 8 digit student number to that student's name:
        {"12345678": "Student Name", ...}

    Why a dictionary helps:
    - During a 30 minute video, checking `if number in students:` takes one step
      in memory instead of reopening the Excel file on every frame.
    - Looking up `students[number]` immediately gives the student's full name.

    Parameters:
    - excel_path: File path to the .xlsx class list spreadsheet.

    Returns:
    - Dictionary mapping student_number (str) -> student_name (str).
    """
    # Read the Excel file into a pandas DataFrame:
    # - engine="openpyxl" uses the openpyxl package to read modern .xlsx files
    # - dtype={"Student number": str} keeps numbers as text so leading zeros are preserved
    # - keep_default_na=False keeps empty cells as "" instead of converting them to NaN
    df = pd.read_excel(
        excel_path,
        engine="openpyxl",
        dtype={"Student number": str},
        keep_default_na=False,
    )

    # Start an empty dictionary to store {student_number: student_name}
    students = {}

    # Loop through every row in the spreadsheet:
    # - iterrows() gives back (row_index, row_data)
    # - "_" is the standard Python placeholder when we do not need row_index
    for _, row in df.iterrows():
        # .strip() removes accidental spaces before or after the text in Excel
        student_number = row["Student number"].strip()

        # Only store rows that actually have a student number (skips blank rows)
        if student_number:
            students[student_number] = row["Student name"].strip()

    return students


def check_class_list(detected_numbers):
    """
    Compare all 8 digit student numbers collected across the session against
    the Excel class list once, and print whether each student was detected.
    (In Step 4, we will expand this module to also save output/attendance_summary.csv.)

    Parameters:
    - detected_numbers: A Python set of unique 8 digit student number strings.
    """
    # Load the class list sheet:
    # - dtype={"Student number": str} keeps student numbers as text so leading zeros are never dropped
    # - keep_default_na=False keeps empty cells as "" instead of turning them into NaN
    df = pd.read_excel(
        class_list_path,
        engine="openpyxl",
        dtype={"Student number": str},
        keep_default_na=False,
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
