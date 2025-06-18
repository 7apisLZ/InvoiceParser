from my_dataclasses import *
import re
import calendar
import csv
from dataclasses import asdict
import os
import pprint
import PyPDF2
import shutil
import streamlit as st

invoice_number = "0000000"
corporate_id = "0000000000"
bp_id = "00000000"


def extract_attnto(content):
    """
        Extracts the name of whom the invoice is addressed on from the first page.
    """
    # print(content)
    match = re.search(r'to:\s*(.*)', content)

    if match:
        return ' '.join(match.group(1).title().split())  # Remove excess whitespace and all caps
    else:
        return "None"


def extract_bp_id(content):
    """
        Extracts the bill payer ID from the first page.
    """
    # print(content)
    match = re.search(r'Bill Payer ID:\s*(.*)', content)

    if match:
        global bp_id
        bp_id = match.group(1)


def extract_corporate_id(content):
    """
        Extracts the corporate ID from the first page.
    """
    # print(content)
    match = re.search(r'Corporation ID\s*(.*)', content)

    if match:
        global corporate_id
        corporate_id = match.group(1)


def extract_invoice_num(content):
    """
        Extracts the invoice number from the first page.
    """
    # print(content)
    match = re.search(r'Invoice Number:\s*(.*)', content)

    if match:
        global invoice_number
        invoice_number = match.group(1)


def extract_date(content):
    match = re.search(r'Invoice Date:\s*(.*)', content)

    if match:
        date = match.group(1)
        values = date.split('/')
        month = values[0]
        year = values[2]
        month_name = calendar.month_name[int(month)]
        return "Date: " + month_name + " " + str(year)
    else:
        return "None"


def extract_curr_charges(content):
    """
        Extracts the value for 'Total Current Charges' on page 2 of the invoice.
    """
    # print(content)
    match = re.search(r'Total Current Charges \s+(\S+)', content)

    if match:
        return match.group(1)
    else:
        return 0.0


def extract_num_calls(content):
    """
        Extract the number of calls made per month from the "Total Voice Services" page.
    """
    match = re.search(r'Total Voice Services \s+(\S+)', content)

    if match:
        return int(match.group(1).replace(',', ''))
    else:
        return 0


def extract_calls_data(content):
    """
        Extracts data about all the calls on the 'Voice Services - Inbound Usage/Features by Toll Free Number' page.
        Call data includes the number, num calls, minutes, and total cost.
    """
    # print(content)
    data = []

    lines = iter(content.splitlines())
    for line in lines:  # Go line by line
        if re.match(r"\s+\d{3}-\d{3}-\d{4}", line):  # If the line is a phone number, create NumberData object
            # print("Number found")
            number = NumberData()
            phone_number = line.lstrip().replace("-", "")
            number.number = phone_number  # Record the phone number

            # On the next lines, record all data (including duplicates)
            line = next(lines)
            while re.match(r'\s+N', line):
                number.account_id = line.lstrip()
                line = next(lines)
                values = line.split()
                number.calls = values[2].replace(',', '')
                number.minutes = values[3].replace(',', '')
                number.total_cost = values[len(values) - 1]
                data.append(number)

                number = NumberData()
                number.number = phone_number
                line = next(lines)

    return data


def extract_accounts_data(content, invoice_num):
    """
        Extracts data about all the accounts on the 'Index to Accounts with Totals' page.
        Call data includes the description, account ID, num calls, minutes, and total cost
    """
    # print(content)
    data = []

    lines = iter(content.splitlines())
    for line in lines:
        if "Description" in line:
            _ = next(lines)
            line = next(lines)  # Skip forward 2 lines
            while "_" not in line:
                account = AccountData()

                # On the first line, extract description
                account.desc = line.lstrip()
                line = next(lines)

                # On the next line, extract Account ID, calls, minutes, and total cost
                values = line.split()
                account.account_id = values[0]
                account.invoice_number = invoice_num
                account.calls = values[1].replace(',', '')
                account.minutes = values[2].replace(',', '')
                account.total_cost = values[8]

                data.append(account)  # Record AccountData object to the list
                line = next(lines)

    return data


def make_directory(file_name):
    dir_name = "_" + file_name
    try:
        os.mkdir(dir_name)
    except FileExistsError:
        print(f"Directory '{dir_name}' already exists.")
    except PermissionError:
        print(f"Permission denied: Unable to create '{dir_name}'.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return dir_name


def write_data(data, file_name):
    dict_rows = [asdict(item) for item in data]

    if data:
        fieldnames = dict_rows[0].keys()
        with open(file_name, mode='w', newline='') as file:
            if file_name == "numbers.csv":
                extra_fields = {
                    "Corporation ID": corporate_id,
                    "Bill Payer ID": bp_id,
                    "Invoice Number": invoice_number
                }

                for row in dict_rows:
                    row_copy = {}
                    row_copy.update(extra_fields)
                    row_copy.update(row)
                    row.clear()
                    row.update(row_copy)

            writer = csv.DictWriter(file, fieldnames)
            writer.writeheader()
            writer.writerows(dict_rows)


def remove_duplicates(dir_name, file_name):
    dest_name = dir_name + "/" + file_name
    if os.path.exists(dest_name):  # Replace existing file if duplicate
        os.remove(dest_name)
    shutil.move(file_name, dir_name)


def download_file_button(dir_name, invoice_name, download_name, mime_type):
    with open(dir_name + download_name, "rb") as file:
        st.download_button("Download " + download_name,
                           data=file,
                           file_name=invoice_name + download_name,
                           mime="text/" + mime_type)


def scanned_invoice_data(file_name):
    """
        Extracts data from a scanned invoice.
    """

    # Make directory to store data
    dir_name = make_directory(file_name)

    # Open and read the PDF file
    with open(file_name, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)

        # num_pages = len(pdf_reader.pages)
        # write_num_pages = "Total number of pages: " + str(num_pages) + "\n"

        # Read page 1
        page = pdf_reader.pages[0]
        content = page.extract_text()

        name = extract_attnto(content)
        write_name = "Attention to: " + name + "\n"
        extract_corporate_id(content)
        write_corp_id = "Corporate ID: " + corporate_id + "\n"

        # Read page 2
        page = pdf_reader.pages[1]
        content = page.extract_text()

        extract_bp_id(content)
        write_bp_id = "Bill Payer ID: " + bp_id + "\n"
        extract_invoice_num(content)
        write_invoice_num = "Invoice Number: " + invoice_number + "\n"
        write_date = extract_date(content) + "\n"

        curr_charges = extract_curr_charges(page.extract_text())
        write_curr_charges = "Total Due: " + str(curr_charges)
        # print(f"Total current charges: {curr_charges}")

        ### Search the entire PDF

        # Extract calls per month from 'Voice Services Summary'
        num_calls = 0
        for i, page in enumerate(pdf_reader.pages):
            page_content = page.extract_text()
            if "Voice Services Summary\n" in page_content:
                num_calls = extract_num_calls(page_content)
                print(f"Calls per month: {num_calls} (pg {i + 1})")
                break
        write_calls_per_month = "Calls per month: " + str(num_calls) + "\n"

        # Extract data from 'Index to Accounts with Totals'
        accounts_data = []
        for i, page in enumerate(pdf_reader.pages):
            page_content = page.extract_text()
            if "Index to Accounts with Totals" in page_content:
                accounts_data.extend(extract_accounts_data(page_content, invoice_number))
                print(f"Accounts on page {i + 1}:")
                # pprint.pprint(accounts_data)

        if not accounts_data:
            print("No accounts found.")

        # Extract data from 'Voice Services - Inbound Usage/Features by Toll Free Number'
        numbers_data = []
        for i, page in enumerate(pdf_reader.pages):
            page_content = page.extract_text()
            if "Voice Services - Inbound Usage/Features by Toll Free Number\n" in page_content:
                numbers_data.extend(extract_calls_data(page_content))
                print(f"Numbers on page {i + 1}:")
                # pprint.pprint(numbers_data)

        if not numbers_data:
            print("No phone numbers found.")

    # Information for Invoices tab
    with open("invoice.txt", "w") as file:
        write_lines = [write_corp_id, write_bp_id, write_invoice_num, write_date, write_name, write_calls_per_month,
                       write_curr_charges]
        file.writelines(write_lines)
        # file.write(write_num_pages)

    # Write data into files and move files to new directory
    write_data(accounts_data, "accounts.csv")
    remove_duplicates(dir_name, "accounts.csv")

    write_data(numbers_data, "numbers.csv")
    remove_duplicates(dir_name, "numbers.csv")

    remove_duplicates(dir_name, "invoice.txt")

    # Move the invoice to its own folder TODO add back
    # shutil.move(file_name, dir_name)