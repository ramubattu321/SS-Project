import xml.etree.ElementTree as ET
import pandas as pd
from pathlib import Path


def safe_float(value):
    """Convert text to float, return 0.0 for empty or invalid values."""
    if value is None:
        return 0.0
    value = str(value).strip()
    if value == "":
        return 0.0
    try:
        return float(value)
    except ValueError:
        return 0.0


def parse_tally_xml(xml_file):
    """Parse Tally ERP 9 XML and return structured rows."""
    tree = ET.parse(xml_file)
    root = tree.getroot()

    rows = []
    periods = root.findall("DSPPERIOD")
    accinfos = root.findall("DSPACCINFO")

    count = min(len(periods), len(accinfos))

    for i in range(count):
        month = periods[i].text.strip() if periods[i].text else f"Month_{i+1}"

        credit_elem = accinfos[i].find(".//DSPCRAMTA")
        closing_elem = accinfos[i].find(".//DSPCLAMTA")
        debit_elem = accinfos[i].find(".//DSPDRAMTA")

        credit = safe_float(credit_elem.text if credit_elem is not None else None)
        closing = safe_float(closing_elem.text if closing_elem is not None else None)
        debit = safe_float(debit_elem.text if debit_elem is not None else None)

        rows.append(
            {
                "Month": month,
                "Debit Amount": debit,
                "Credit Amount": credit,
                "Closing Balance": closing,
            }
        )

    return rows


def main():
    xml_file = Path("Financial Data.xml")
    output_file = Path("financial_data.xlsx")

    if not xml_file.exists():
        print(f"Error: '{xml_file}' not found in the current folder.")
        return

    data = parse_tally_xml(xml_file)

    if not data:
        print("No data found in XML file.")
        return

    df = pd.DataFrame(data)

    # Add summary row
    summary_row = {
        "Month": "Total",
        "Debit Amount": df["Debit Amount"].sum(),
        "Credit Amount": df["Credit Amount"].sum(),
        "Closing Balance": df["Closing Balance"].iloc[-1],
    }

    df = pd.concat([df, pd.DataFrame([summary_row])], ignore_index=True)

    df.to_excel(output_file, index=False)

    print("XML successfully converted to Excel!")
    print(f"Output file created: {output_file}")


if __name__ == "__main__":
    main()
