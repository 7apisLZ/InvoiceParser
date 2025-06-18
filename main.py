from scanned_file import scanned_invoice_data
from scanned_file import download_file_button
import streamlit as st


def main():
    # file_name = "BP 99536677_2025-05_Invoice 05517027.pdf"

    st.title("Invoice Data Parser")
    st.text("Created by Lizzy Zhou")
    st.divider()
    uploaded_file = st.file_uploader("Upload your invoice here:", type="pdf")

    if uploaded_file:
        file_name = uploaded_file.name
        dir_name = "_" + file_name

        st.write("You uploaded file: ", file_name)
        file_content = uploaded_file.read()

        with open(file_name, "wb") as file:
            file.write(file_content)

        scanned_invoice_data(file_name)        # Generate the data

        download_file_button(dir_name, file_name, "/invoice.txt", "plain")
        download_file_button(dir_name, file_name, "/accounts.csv", "csv")
        download_file_button(dir_name, file_name, "/numbers.csv", "csv")


if __name__ == "__main__":
    main()