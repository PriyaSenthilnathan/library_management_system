import streamlit as st
import pymysql
import pandas as pd
import credentials as cr

# Load custom CSS from a file
def load_custom_css():
    with open('theme.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Database connection
def get_connection():
    return pymysql.connect(host=cr.host, user=cr.user, password=cr.password, database=cr.database)

# Clear Screen equivalent for Streamlit
def clear_screen():
    st.experimental_rerun()

# Function to fetch book records from the database
def fetch_books():
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM book_list")
            rows = cursor.fetchall()
        connection.close()
        return rows
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return []

# Function to show book records without displaying the index
def show_books():
    st.header("Book Records")
    books = fetch_books()
    if not books:
        st.info("There is no data to show")
        return

    # Convert data to DataFrame for easier manipulation
    cols = ['Book ID', 'Book Name', 'Author', 'Edition', 'Price', 'Quantity']
    df = pd.DataFrame(books, columns=cols)

    # Display the DataFrame as a table without the index
    st.table(df)

# Function to search for a book
def search_book(book_name):
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM book_list WHERE book_name LIKE %s", ("%" + book_name + "%"))
            rows = cursor.fetchall()
        connection.close()
        return rows
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return []

def display_search_results():
    st.header("Search Book")
    book_name = st.text_input("Enter the Book Name")
    if st.button("Search"):
        if not book_name:
            st.error("Please Enter the Book Name")
        else:
            results = search_book(book_name)
            if not results:
                st.info("There is no data to show")
            else:
                st.table(results)

def add_new_book():
    st.header("Add New Book")

    book_id = st.text_input("Book ID")
    book_name = st.text_input("Book Name")
    author = st.text_input("Author")
    edition = st.text_input("Edition")
    price = st.text_input("Price")
    quantity = st.text_input("Quantity")

    if st.button("Submit"):
        if not all([book_id, book_name, author, edition, price, quantity]):
            st.error("All fields are required")
        else:
            try:
                connection = get_connection()
                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM book_list WHERE book_id=%s", book_id)
                    row = cursor.fetchone()
                    if row:
                        st.error("This book ID already exists, please try again with another one")
                    else:
                        cursor.execute("INSERT INTO book_list (book_id, book_name, author, edition, price, qty) VALUES (%s, %s, %s, %s, %s, %s)",
                                       (book_id, book_name, author, edition, price, quantity))
                        connection.commit()
                connection.close()
                st.success("The data has been submitted")
                clear_screen()
            except Exception as e:
                st.error(f"Error: {str(e)}")

def issue_book():
    st.header("Issue Book")

    book_id = st.text_input("Book ID")
    book_name = st.text_input("Book Name")
    stu_roll = st.text_input("Student Roll Number")
    stu_name = st.text_input("Student Name")
    course = st.text_input("Course")
    subject = st.text_input("Subject")
    issue_date = st.date_input("Issue Date")
    return_date = st.date_input("Return Date")

    if st.button("Issue"):
        if not all([book_id, book_name, stu_roll, stu_name, course, subject, issue_date, return_date]):
            st.error("All fields are required")
        else:
            try:
                connection = get_connection()
                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM book_list WHERE book_id=%s", book_id)
                    row = cursor.fetchone()
                    if not row:
                        st.error("This book ID does not exist")
                    else:
                        book_quantity = row[5]
                        if book_quantity < 1:
                            st.error("This book is currently unavailable")
                        else:
                            cursor.execute("SELECT * FROM borrow_record WHERE stu_roll=%s AND book_id=%s", (stu_roll, book_id))
                            existing_borrow = cursor.fetchone()
                            if existing_borrow:
                                st.error("This book is already borrowed by this student")
                            else:
                                cursor.execute("SELECT * FROM borrow_record WHERE stu_roll=%s", stu_roll)
                                borrowed_books = cursor.fetchall()
                                if len(borrowed_books) >= 3:
                                    st.error("A student can borrow a maximum of 3 books")
                                else:
                                    cursor.execute("INSERT INTO borrow_record (book_id, book_name, stu_roll, stu_name, course, subject, issue_date, return_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                                                   (book_id, book_name, stu_roll, stu_name, course, subject, issue_date, return_date))
                                    cursor.execute("UPDATE book_list SET qty = qty - 1 WHERE book_id=%s", book_id)
                                    connection.commit()
                                    st.success("Book issued successfully")
                connection.close()
                clear_screen()
            except Exception as e:
                st.error(f"Error: {str(e)}")

def return_book():
    st.header("Return Book")

    stu_roll = st.text_input("Student Roll Number")
    book_id = st.text_input("Book ID")

    if st.button("Return"):
        if not all([stu_roll, book_id]):
            st.error("All fields are required")
        else:
            try:
                connection = get_connection()
                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM borrow_record WHERE stu_roll=%s AND book_id=%s", (stu_roll, book_id))
                    borrow_record = cursor.fetchone()
                    if not borrow_record:
                        st.error("No such borrow record found")
                    else:
                        cursor.execute("DELETE FROM borrow_record WHERE stu_roll=%s AND book_id=%s", (stu_roll, book_id))
                        cursor.execute("UPDATE book_list SET qty = qty + 1 WHERE book_id=%s", book_id)
                        connection.commit()
                        st.success("Book returned successfully")
                connection.close()
                clear_screen()
            except Exception as e:
                st.error(f"Error: {str(e)}")

def update_book():
    st.header("Update Book")

    book_id = st.text_input("Book ID")
    book_name = st.text_input("Book Name")
    author = st.text_input("Author")
    edition = st.text_input("Edition")
    price = st.text_input("Price")
    quantity = st.text_input("Quantity")

    if st.button("Update"):
        if not all([book_id, book_name, author, edition, price, quantity]):
            st.error("All fields are required")
        else:
            try:
                connection = get_connection()
                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM book_list WHERE book_id=%s", book_id)
                    row = cursor.fetchone()
                    if not row:
                        st.error("This book ID does not exist")
                    else:
                        cursor.execute("UPDATE book_list SET book_name=%s, author=%s, edition=%s, price=%s, qty=%s WHERE book_id=%s",
                                       (book_name, author, edition, price, quantity, book_id))
                        connection.commit()
                        st.success("Book updated successfully")
                connection.close()
                clear_screen()
            except Exception as e:
                st.error(f"Error: {str(e)}")

def delete_book():
    st.header("Delete Book")

    book_id = st.text_input("Book ID")

    if st.button("Delete"):
        if not book_id:
            st.error("Book ID is required")
        else:
            try:
                connection = get_connection()
                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM book_list WHERE book_id=%s", book_id)
                    row = cursor.fetchone()
                    if not row:
                        st.error("This book ID does not exist")
                    else:
                        cursor.execute("DELETE FROM book_list WHERE book_id=%s", book_id)
                        connection.commit()
                        st.success("Book deleted successfully")
                connection.close()
                clear_screen()
            except Exception as e:
                st.error(f"Error: {str(e)}")

def main():
    load_custom_css()

    st.sidebar.title("Library Management System")
    option = st.sidebar.selectbox("Choose an action", ["Show Books", "Search Book", "Add New Book", "Issue Book", "Return Book", "Update Book", "Delete Book", "Exit"])

    if option == "Show Books":
        show_books()
    elif option == "Search Book":
        display_search_results()
    elif option == "Add New Book":
        add_new_book()
    elif option == "Issue Book":
        issue_book()
    elif option == "Return Book":
        return_book()
    elif option == "Update Book":
        update_book()
    elif option == "Delete Book":
        delete_book()

if __name__ == "__main__":
    main()
