
# Customer and Appointment Manager

This is a Python command-line application for managing different customer records and appointments.
It uses SQLite for data storage.

## Features

- Add, view, search and delete customers
- Create, view, search and delete appointments
- Stores customer and appointment data in an SQLite database
- Exit the application
- Validates customer information such as emails, phone numbers and appointment inputs such as the date and time
- Prevents customers from being deleted while they still have appointments
- Parameterised SQL queries for database operations to help prevent SQL injection

# Technologies Used

- Python
- SQLite
- Git and GitHub

## How to run the program

### Requirements

- Python installed on your computer
- Git, if you want to clone the repository

### Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/chris-codes7/customer-appointment-manager.git
   ```

2. Navigate into the project folder:

   ```bash
   cd customer-appointment-manager
   ```

3. Run the application:

   ```bash
   python main.py
   ```
