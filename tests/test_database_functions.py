import unittest #unittest requires test methods to start with test_ 
from unittest.mock import patch, call
from main import main, create_database
from main import add_customer, add_appointment
from main import delete_appointment, delete_customer
from main import view_customer
from main import search_customer
import tempfile
import sqlite3
import os
#python -m unittest discover -s tests -p "test_*.py" -v


class TestDatabase(unittest.TestCase): # grouping tests on thr program in class TestDatabase. unittest.Testcase gives class the features Pythons testing framework needs

    def setUp(self): # runs before each test, a fresh test database is created
        self.temp_folder = tempfile.TemporaryDirectory() # tempfile.TemporaryDirectory()  creates temporary folder for testing. 
        self.addCleanup(self.temp_folder.cleanup) #schedules temporary folder for an automatic clean up
        self.database_path = os.path.join(self.temp_folder.name, "test.db") # using os.path.join to create a path with the folder and the file
        create_database(self.database_path)

    def test_create_database_tables(self): # checking that the database creates both required tables, customers and appointments
        connection = sqlite3.connect(self.database_path) #connecting to temporary database
        self.addCleanup(connection.close) #schedules the connection to close automatically after the test -> if the test fails/error the connection will still close
        cursor = connection.cursor()
        cursor.execute( "SELECT name FROM sqlite_master WHERE type='table';") #sqlite_master retrieves table names
        rows = cursor.fetchall() # fetches all rowws
        table_names = [] #creating a list to store the table names
        for row in rows:
            table_names.append(row[0]) #loops through the results gathered and appends each table name into the list
        self.assertIn("customers", table_names) #checking if "customers" exists in table_names , passes if customers is in the list, unittest reports outcome
        self.assertIn("appointments", table_names)


    def test_add_customer_saves_details(self):  # this test will ensure that customer details are saved correctly to the database 
        customer_details = ["Alex Hedge", "alexhedge3112@example.com", "0735177231"] # false information used for the test that will be inputted upon request of the add_customer function
        with patch("builtins.input", side_effect=customer_details): #using the customer_detail list to input, when the add_customer function asks
            add_customer(self.database_path)
        connection = sqlite3.connect(self.database_path)
        self.addCleanup(connection.close)
        cursor = connection.cursor()
        cursor.execute("SELECT name, email, phone FROM customers ") #Selecting name,email and phone
        customer_details_fetched = cursor.fetchone() # storing the details fetched from the test database and storing it in customer_details_fetched
        customer_details = tuple(customer_details) #converting customer_details to a tuple as it needs to be compared to customer_details_fetched which is also a tuple
        self.assertEqual(customer_details, customer_details_fetched) #customer_details is compared to customer_details_fetched. If the same the test passed

    def test_adding_appointment_saves_details(self): #This test is ensuring that appointment details are saved correctly to the database
        connection = sqlite3.connect(self.database_path)
        self.addCleanup(connection.close)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)",  #We ned a customer created in order to create an appointment for that customer
        ("Test Customer", "test@example.com", "07431341341"))
        connection.commit()
        customer_id = cursor.lastrowid #Storing the ID of the customer we just inserted ready to enter into the appointment
        appointment_details = [customer_id,"18.11.2027","16:30"] # this line is the details we will enter for the appointment
        with patch("builtins.input", side_effect=appointment_details): #fill inputs in add_appointment with the appointment_details list #patch() temporarily replaces a real function with a mock version during test
            add_appointment(self.database_path)
        cursor.execute("SELECT customer_id, date, time FROM appointments")
        appointment_details_fetched = cursor.fetchone() #fetching the appointment details and storing them
        expected_appointment_details = (customer_id, "18.11.2027","16:30") #the tuple needed to compare to the fetched details. customer_id is not a string here as fetched details will have customer id as an integer and they need to be compared
        self.assertEqual(expected_appointment_details, appointment_details_fetched) #comparing the expected_appointment_details to the appointment details we just fetched from the database. Test should pass if equivalant

    def test_deleting_appointment_removes_record(self): #Ensuring that an appointment is sucessfully deleted
        connection = sqlite3.connect(self.database_path)
        self.addCleanup(connection.close)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)", #creating customer for appointment
        ("Test Customer2", "test2@example.com", "07238472347"))
        connection.commit()
        customer_id = cursor.lastrowid #storing the customer id
        cursor.execute("INSERT INTO appointments (customer_id, date, time) VALUES (?, ?, ?) ", # creating appointment with the customer id
                       (customer_id, "19.12.2027", "17:30"))
        connection.commit()
        appointment_id = cursor.lastrowid
        with patch("builtins.input", return_value=appointment_id): #inputs in the program, will be given appointment_id
            delete_appointment(self.database_path) 
        cursor.execute("SELECT * FROM appointments WHERE appointment_id = ?",
                        (appointment_id,)) 
        deleted_appointment = cursor.fetchone() #fetching the deleted appointment to see if it exists
        self.assertIsNone(deleted_appointment) #checking if the appointment exists, if it doesn't the test is successful

    def test_deleting_customer_removes_record(self): # Ensuring that a customer is successfully deleted
        connection = sqlite3.connect(self.database_path)
        self.addCleanup(connection.close)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)", #creating a new customer
                       ("Test Customer3", "test3@example.com", "07234523253"))
        connection.commit()
        customer_id = cursor.lastrowid #storing the customer id
        with patch("builtins.input", return_value=customer_id): #entering customer id into the input of delete_customer()
            delete_customer(self.database_path)
        cursor.execute("SELECT * FROM customers WHERE id = ?",
                       (customer_id,))
        deleted_customer = cursor.fetchone() #fetching the deleted customer to see if they still exist
        self.assertIsNone(deleted_customer) #checking if the customer doesn't exist.

    def test_customers_with_appointments_cannot_be_deleted(self): # This test is to ensure that customers cannot be deleted if they have appointments
        connection = sqlite3.connect(self.database_path)
        self.addCleanup(connection.close)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)", # creating a customer
                       ("Test Customer4", "test4@example.com", "07233323253"))
        connection.commit()
        customer_id = cursor.lastrowid #storing the customer id
        cursor.execute("INSERT INTO appointments (customer_id, date, time) VALUES (?, ?, ?) ", #creating an appointment for that customer
                               (customer_id, "20.12.2027", "18:30"))
        connection.commit()
        with patch("builtins.input", return_value=customer_id): #entering customer_id into the input of delete_customer()
            delete_customer(self.database_path)
        cursor.execute("SELECT * FROM customers where id = ?",
                       (customer_id,))
        attempted_deleted_customer = cursor.fetchone() #fetching the customer to see if they still exist
        self.assertIsNotNone(attempted_deleted_customer) #ensuring that the customer still exists and isn't deleted 
        
    def test_deleting_nonexistent_customer(self): #This test is to ensure the program correctly handle a user attempting to delete a non-existent customer
        connection = sqlite3.connect(self.database_path)
        self.addCleanup(connection.close)
        cursor = connection.cursor()
        with patch("builtins.input", return_value=999), patch("builtins.print") as mock_print: #storing what is printed in variable mock_print (also stores info on function calls + argument)
            delete_customer(self.database_path)
        cursor.execute("SELECT COUNT(*) FROM customers") #returns/counts no of rows, * including every row even if column values NULL.
        customer_count = cursor.fetchone()[0] #[0] referring to the first position in the tuple returning it as an integer
        self.assertEqual(customer_count, 0) #comparing 0 to 0 to show nothing has changed, customer count should be 0 (fresh table).
        mock_print.assert_called_with("Customer not Found! There was no one with the ID:", 999) #Checking if the correct error message was printed by comparing it to mock_print variable (its important 999 isnt included in the sting as in this case mock_print has two seperate arguments from the print)


    def test_view_customer_displays_details(self):
        connection = sqlite3.connect(self.database_path)
        self.addCleanup(connection.close)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)", 
                       ("Test Customer4", "test4@example.com", "07232523253"))
        connection.commit()
        with patch("builtins.print") as mock_print:
            view_customer(self.database_path)
        mock_print.assert_any_call("ID:", 1) # i put 1 here as its an empty table for a test, however i could have used cursor.lastrowid too
        mock_print.assert_any_call("Name:", "Test Customer4") #assert call is checking if mock_print recorded this argument atleast once
        mock_print.assert_any_call("Email:", "test4@example.com")
        mock_print.assert_any_call("Phone Number:", "07232523253")

    def test_search_customer_displays_correct_details(self):
        connection = sqlite3.connect(self.database_path)
        self.addCleanup(connection.close)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)",  #adding customer 1
                       ("Customer1", "test5@example.com", "07239323253"))
        connection.commit()
        customer_id1 = cursor.lastrowid
        cursor.execute("INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)",  #adding customer 2
                       ("Customer2", "test6@example.com", "07139323253"))
        connection.commit()
        customer_id2 = cursor.lastrowid 
        with patch("builtins.input", return_value=customer_id2), patch("builtins.print") as mock_print: #setting up search for customer 2, recording the output in mock_print. any inputs requested from search_customer() will be filled with customer_id2
            search_customer(self.database_path)
        mock_print.assert_any_call("ID:", customer_id2) #the next 4 lines are checking if customer 2 was correctly displayed
        mock_print.assert_any_call("Name:", "Customer2")
        mock_print.assert_any_call("Email:", "test6@example.com")
        mock_print.assert_any_call("Phone Number:", "07139323253")
        self.assertNotIn(call("ID:", customer_id1), mock_print.call_args_list) #the next 4 lines are ensuring customer 1 was not displayed
        self.assertNotIn(call("Name:", "Customer1"), mock_print.call_args_list) #Checking to ensure that customer 1 is not in the list that is being displayed. call() is a representation of the function call (print is the function call)
        self.assertNotIn(call("Email:", "test5@example.com"), mock_print.call_args_list)
        self.assertNotIn(call("Phone Number:", "07239323253"), mock_print.call_args_list)

    def test_search_nonexistent_customer(self): #This test ensures that the program correctly handles a search of a non-existent customer
        #No connection = , cleanup or cursor needed as we arent inserting/deleting/modifying anything
        with patch("builtins.input", return_value=878), patch("builtins.print") as mock_print: # 878 could be a string here as users input are strings, however the int(input()) will cast it into an integer anyway.
            search_customer(self.database_path)
        mock_print.assert_any_call("Customer not Found! There was no one with the ID:", 878) #878 would need to be an integer here.

    def test_mainmenu_input_validation(self): #This test is to ensure that invalid inputs from the user are handled correctly
        input_for_test = ["abc", "0", "985", "9"] #Inputs we will be entering into main() there are 3 invalid inputs and 1 valid
        with patch("main.create_database"), patch("builtins.input", side_effect=input_for_test), patch("builtins.print") as mock_print: #patch(main.create_databae) will create a mock database for the test.
            main()
        count_of_invalid_input = mock_print.call_args_list.count(call("Invalid choice, Enter a choice (1-9)")) # counting how many times "Invalid choice..." appears in the mock_print.call_args_list . (should be 3 as theres 3 invalid)
        self.assertEqual(count_of_invalid_input, 3) # As there are 3 invalid inputs, the count should be 3. so here we are comparing the count to 3, if 3=3 then the test has passed

        

