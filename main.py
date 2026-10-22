import sqlite3
from datetime import datetime



def create_database(database_path="customer_manager.db"): #This function sets up the database tables, customers and appointments if they do not already exist. -> If function has no paramter passed then database_path = "customer_manager.db"
     connection = sqlite3.connect(database_path) # Creates the specified database if it doesn't exist else it will opens database with its contents.
     cursor = connection.cursor()

     cursor.execute(
     """CREATE TABLE IF NOT EXISTS customers (
     id INTEGER PRIMARY KEY,
     name TEXT,
     email TEXT,
     phone TEXT
     )      
     """)
     cursor.execute("""
     CREATE TABLE IF NOT EXISTS appointments (
     appointment_id INTEGER PRIMARY KEY,
     customer_id INTEGER,
     date TEXT,
     time TEXT,
     FOREIGN KEY (customer_id) REFERENCES customers(id)
     )
     """)
     
     connection.commit()
     connection.close()

def add_appointment(database_path="customer_manager.db"): # allows the user to create an appointment belonging to a specific customer using their customer ID. Validates customer ID, date and time
     connection = sqlite3.connect(database_path)
     cursor = connection.cursor()
     while True:
          try:
               idcheck = int(input("Enter Customer ID"))
               break
          except ValueError:
               print("A valid customer ID must be inputted")
     cursor.execute(
             "SELECT * FROM customers WHERE id = ?",
             (idcheck,)
        )
     customer = cursor.fetchone()
     if customer is None:
          print("No customer with ID:",idcheck,"found, appointment not created")
          connection.close()
     else:
         while True:
               date = input("Enter date for appointment")
               try: 
                    datetime.strptime(date, "%d.%m.%Y") # string date -> should follow format day(01-31), month(01-12), year -> 4 digit year
               except ValueError: #Invalid format occured user must re-enter date:
                    print("Enter a valid date for the appointment e.g. (15.11.2027)")
               else:
                    while True:
                         time = input("Enter time for appointment e.g. 13:30")
                         try:
                              datetime.strptime(time, "%H:%M") #Time should follow format Hours:Minutes 
                         except ValueError:
                              print("a valid time must be inputted e.g. 13:30")
                         else:
                              cursor.execute(
                                   "INSERT INTO appointments (customer_id, date, time) VALUES (?, ?, ?)",
                                   (idcheck, date, time)
                              )
                              connection.commit()
                              connection.close()
                              break
                    break


     
def add_customer(database_path="customer_manager.db"): # allows the user to add a customer to the customer table by entering a name, email and phone number (also validates name, phone and email)
    while True:
          name = input("Enter your name")
          if not name.strip(): # If user has inputted just spaces or nothing -> return not False = True
               print("A valid name must be inputted")
          else:
               while True:
                    email = input("Enter your email")
                    if not email.strip():
                         print("Enter a valid email")
                    elif "@" not in email or "." not in email: # or gate used. If or gate = True-> invalid email. Testing for invalid emails.
                         print("Enter a valid email")
                    else:
                         while True:
                              phone_number = input("Enter your phone number no spaces")
                              if not phone_number.strip():
                                   print("Enter a valid phone number no spaces")
                              elif not phone_number.isdigit(): # Checking if its digits. If NOT digit return True -> invalid phone number
                                   print("Enter a valid phone number no spaces")
                              else:
                                   connection = sqlite3.connect(database_path)
                                   cursor = connection.cursor()
                                   cursor.execute(
                                        "INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)",
                                        (name, email, phone_number)
                                   )
                                   connection.commit()
                                   connection.close()
                                   break
                         break
               break
                              


def view_appointments(database_path="customer_manager.db"): # displays all appointments and their details date,time and appointment ID from the appointment table, along with the customer name from the customer table
     connection = sqlite3.connect(database_path)
     cursor = connection.cursor()
     cursor.execute("""
     SELECT appointments.appointment_id, customers.name, appointments.date, appointments.time
     FROM appointments
     JOIN customers
     ON appointments.customer_id = customers.id
     """)
     appointment_rows = cursor.fetchall()
     for appointment in appointment_rows:
          print("Appointment ID:", appointment[0])
          print("Customer Name:", appointment[1])
          print("Date:", appointment[2])
          print("Time:", appointment[3])
     connection.close()



def view_customer(database_path="customer_manager.db"): # display all customers and their details from the customers table to the user
        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM customers")
        customer_rows = cursor.fetchall()
        for customer in customer_rows:
             print("ID:", customer[0])
             print("Name:", customer[1])
             print("Email:", customer[2])
             print("Phone Number:", customer[3])
             print("\n")
        connection.close()

def search_appointment(database_path="customer_manager.db"): # Takes a customer ID and finds all appointments assosciated to that customer. The appointments are then displayed with their information to the user
     connection = sqlite3.connect(database_path)
     cursor = connection.cursor()
     while True:
          try:
               idcheck = int(input("Enter a customer ID to show their appointments"))
               break
          except ValueError:
               print("A valid customer ID must be inputted")
     cursor.execute("""
     SELECT appointments.appointment_id, customers.name, appointments.date, appointments.time 
     FROM appointments
     JOIN customers
     ON appointments.customer_id = customers.id
     WHERE appointments.customer_id = ?
     """,
          (idcheck,)
     )
     customer_appointments = cursor.fetchall()
     if not customer_appointments:
          print("This Customer either does not exist, or has no existing appointments with customer ID:", idcheck)
     else:
          print("Appointments matching customer with ID:",idcheck)
          for appointment in customer_appointments:
               print("Appointment ID:", appointment[0])
               print("Customer Name:", appointment[1])
               print("Date:", appointment[2])
               print("Time:", appointment[3])
     connection.close()

def search_customer(database_path="customer_manager.db"): # Takes a customer ID and selects all details assosicated to that customer from the customer table, displaying it to the user
        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()
        while True:
                    try:
                         idcheck = int(input("Enter an ID to search for"))
                         break
                    except ValueError:
                         print("A valid customer ID must be inputted")
        cursor.execute(
             "SELECT * FROM customers WHERE id = ?",
             (idcheck,)
        )
        customer = cursor.fetchone()
        if customer is None:
            print("Customer not Found! There was no one with the ID:", idcheck)
        else:
            print("Customer Found!")
            print("ID:", customer[0])
            print("Name:", customer[1])
            print("Email:", customer[2])
            print("Phone Number:", customer[3])
            print("\n")
        connection.close()

def delete_appointment(database_path="customer_manager.db"): # Takes an appointment ID and deletes the matching appointment from the appointment table.
     connection = sqlite3.connect(database_path)
     cursor = connection.cursor()
     while True:
          try:
               idcheck = int(input("Enter id of the appointment you want to delete"))
               break
          except ValueError:
               print("A valid customer ID must be inputted")
     cursor.execute(
          "DELETE FROM appointments where appointment_id = ?",
          (idcheck,)
     )
     if cursor.rowcount == 0: # If the row count == 0 then no rows were deleted. In this case this means the appointment ID didn't exist
          print("Appointment not Found! There was no appointment with the ID:", idcheck)

     else:
          print("Appointment Found & Deleted with the ID:", idcheck) 
     connection.commit()
     connection.close()



def delete_customer(database_path="customer_manager.db"): # deletes a customer by taking a customer id. The deletion can only occur if the customer has no appointments and exists
            connection = sqlite3.connect(database_path)
            cursor = connection.cursor()
            while True:
                 try:
                    idcheck = int(input("Enter id of user you want to delete:"))
                    break
                 except ValueError:
                      print("A valid customer ID must be inputted")
            cursor.execute( # This part is searching for the customer using the customer id inputted by the user
                 "SELECT * FROM customers WHERE id = ?",
                 (idcheck,)
            )
            customer = cursor.fetchone()
            if customer is None: # This part is checking if the customer exists or not, skips the else block and closes the data base connection returning to main menu if no customer is found
                 print("Customer not Found! There was no one with the ID:", idcheck)
            else:
               cursor.execute(
                    "SELECT * FROM appointments WHERE customer_id = ?", 
                    (idcheck,)
               )
               appointments = cursor.fetchall()
               if appointments:  # if appointments is = [] then = False , (Checking if the customer has appointments)
                    print("This customer has appointments. Please delete all appointments relating to this customer before deletion")
               else:
                    cursor.execute(
                         "DELETE FROM customers WHERE id = ?",
                         (idcheck,)
                    )
                    print("Customer Found & deleted with the ID", idcheck)
            connection.commit()
            connection.close()




def main(): # this is the command line menu displayed to the user in the terminal. The user interacts with the program using numbers 1-9
     create_database()   

     while True:

          print(""" 
          ======================================
               Customer & Appointment Manager
          ======================================

          1. Add Customer
          2. View Customer
          3. Search Customer
          4. Delete Customer
          ----------------------
          5. Add Appointment
          6. View Appointment
          7. Search Appointment
          8. Delete Appointment
          ----------------------
          9. Exit

          """)

          while True:
                    try: 
                         user_choice = int(input("Enter your choice (1-9):"))
                         if user_choice > 9 or user_choice < 1:
                              print("Invalid choice, Enter a choice (1-9)")
                         else:
                              break
                    except ValueError:
                         print("Invalid choice, Enter a choice (1-9)")

                         
          if user_choice == 1:
                    add_customer()

          elif user_choice == 2:
                    view_customer()

          elif user_choice == 3:
                    search_customer()

          elif user_choice == 4:
                    delete_customer()

          elif user_choice == 5:
                    add_appointment()

          elif user_choice == 6:
                    view_appointments()

          elif user_choice == 7:
                    search_appointment()

          elif user_choice == 8:
                    delete_appointment()

          elif user_choice == 9:
                    break
          

if __name__ == "__main__": # if this file isn't being run directly, the main() will not be called. (Won't run if its imported used for testing)
      main()











