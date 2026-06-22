"""NOL data model — the tracked fields, grouped to match the app layout."""
from pydantic import BaseModel, Field
from typing import Optional


# Tracked fields, in display order, grouped by section. This order is also
# the column order of the Excel export.
NOL_FIELDS = [
    # NOL Details
    "NOL_Number", "Issue_Date", "Date_Received", "Type_of_Violation",
    "Enforcement_Agency",
    # Violation
    "Violation_Date", "Violation_Time", "Violation_Location", "Speed_Over_Limit",
    # Vehicle & Assignment
    "License_Plate_Number", "Vehicle_Number", "Depot_Assigned_To", "Division",
    "Vehicle_Parked_At",
    # Financial
    "Fine_Amount", "Due_Date", "TSD_Amount", "Budget_2_Pay", "Late_Fee",
    # Notices & Memo
    "Memo_Date", "Notice_2nd_Date", "Notice_3rd_Date",
    # Case Tracking
    "Case_Status", "Status",
    # Remarks
    "Remarks",
]

# Human-readable column headers for the Excel export.
FIELD_LABELS = {
    "NOL_Number": "NOL Number",
    "Issue_Date": "NOL Date",
    "Date_Received": "Date Received",
    "Type_of_Violation": "Type of Violation",
    "Enforcement_Agency": "Enforcement Agency",
    "Violation_Date": "Violation Date",
    "Violation_Time": "Violation Time",
    "Violation_Location": "Violation Location",
    "Speed_Over_Limit": "Speed Over Limit",
    "License_Plate_Number": "License Plate Number",
    "Vehicle_Number": "Vehicle Number",
    "Depot_Assigned_To": "Depot / Assigned To",
    "Division": "Division",
    "Vehicle_Parked_At": "Vehicle Parked At",
    "Fine_Amount": "Amount Due",
    "Due_Date": "Due Date",
    "TSD_Amount": "TSD Amount",
    "Budget_2_Pay": "Budget 2 Pay",
    "Late_Fee": "Late Fee",
    "Memo_Date": "Memo Date",
    "Notice_2nd_Date": "2nd Notice Date",
    "Notice_3rd_Date": "3rd Notice Date",
    "Case_Status": "Case Status",
    "Status": "Status",
    "Remarks": "Remarks Pertaining to NOL",
}


class NOLRecord(BaseModel):
    """A single Notice of Liability record. All fields optional except the
    NOL number so partially-entered records can still be saved."""
    NOL_Number: str = Field(..., description="The DOF notice number")
    Issue_Date: Optional[str] = ""
    Date_Received: Optional[str] = ""
    Type_of_Violation: Optional[str] = ""
    Enforcement_Agency: Optional[str] = ""
    Violation_Date: Optional[str] = ""
    Violation_Time: Optional[str] = ""
    Violation_Location: Optional[str] = ""
    Speed_Over_Limit: Optional[str] = ""
    License_Plate_Number: Optional[str] = ""
    Vehicle_Number: Optional[str] = ""
    Depot_Assigned_To: Optional[str] = ""
    Division: Optional[str] = ""
    Vehicle_Parked_At: Optional[str] = ""
    Fine_Amount: Optional[str] = ""
    Due_Date: Optional[str] = ""
    TSD_Amount: Optional[str] = ""
    Budget_2_Pay: Optional[str] = ""
    Late_Fee: Optional[str] = ""
    Memo_Date: Optional[str] = ""
    Notice_2nd_Date: Optional[str] = ""
    Notice_3rd_Date: Optional[str] = ""
    Case_Status: Optional[str] = ""
    Status: Optional[str] = "OPEN"
    Remarks: Optional[str] = ""
