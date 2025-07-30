from scanned_file import scanned_invoice_data
from scanned_file import download_file_button


def main():
    # TODO: Change the file name here
    file_name = "BP 99536677_2025-05_Invoice 05517027.pdf"
    scanned_invoice_data(file_name)  # Generate the data


if __name__ == "__main__":
    main()
