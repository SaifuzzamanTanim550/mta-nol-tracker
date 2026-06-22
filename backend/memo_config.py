"""Editable defaults for the MTA memorandum.

Change the values here once and every generated memo uses them. Anything a
staff member needs to override per-memo can still be edited in the app before
generating.
"""

# Who the memo is from (the Transportation Support contact).
FROM_LINE = "Kim Jiggetts, Transportation Support"

# Where operators submit proof of payment / dismissal.
SUBMIT_TO = "Kim Jiggetts at Transportation Support, 25 Jamaica Avenue, Room 310"

# Recipient ("To:") by division. Fill in the AGM for each division as you
# confirm them. Keys match the Division dropdown values. Blank = staff fills in.
DIVISION_RECIPIENTS = {
    "Brooklyn": "Denis Miriam, AGM, Strategic Planning & Development, Brooklyn Division",
    "Bronx": "",
    "Manhattan": "",
    "Queens North": "",
    "Queens South": "",
    "Staten Island": "",
    "Safety": "",
    "Safety & Training": "",
    "Road Operations": "",
    "Collection & Services": "",
    "Facilities": "",
    "Labor Relations": "",
    "Trans Support": "",
    "BUS TECHNOLOGY": "",
    "ENY CMF": "",
    "Grand Avenue CMF": "",
    "Zerega CMF": "",
}

# Violation type → the program name used in the memo "Re:" line.
VIOLATION_PROGRAMS = {
    "Speeding": "SCHOOL ZONE SPEEDING CAMERA MONITORING PROGRAM",
    "School Bus Safety": "SCHOOL BUS SAFETY CAMERA MONITORING PROGRAM",
    "Red Light": "RED LIGHT CAMERA MONITORING PROGRAM",
    "Bus Lane": "BUS LANE CAMERA MONITORING PROGRAM",
    "ACE": "AUTOMATED CAMERA ENFORCEMENT (ACE) PROGRAM",
    "Work Zone Safety": "WORK ZONE SPEED CAMERA MONITORING PROGRAM",
    "Weigh in Motion": "WEIGH-IN-MOTION MONITORING PROGRAM",
    "Courtesy": "CAMERA MONITORING PROGRAM",
    "Parking": "PARKING VIOLATION",
}

# Enforcement agency abbreviation → full name for the memo body.
AGENCY_FULL = {
    "NYCDOT": "New York City Department of Transportation",
    "NYSDOT": "New York State Department of Transportation",
    "YPVB": "Yonkers Parking Violations Bureau",
    "NCTPVA": "Nassau County Traffic and Parking Violations Agency",
    "COY": "City of Yonkers",
    "TOH": "Town of Hempstead",
}
