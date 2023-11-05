import maskpass
import bcrypt
import mysql.connector
import csv 
from datetime import datetime
import copy

mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "",
    database = "finance_advisor"
)

cursor = mydb.cursor()

class Admin:
    def __init__(self, Admin_ID, Firstname, Lastname, Hiredate, email, Password):
        self.Admin_ID = Admin_ID 
        self.Firstname = Firstname
        self.Lastname = Lastname
        self.Hiredate = Hiredate 
        self.email = email 
        self.Password = Password  
    # login method, checking input hashed password with stored hashed password
    def login(self):
        max_login_attempts = 3  # Set the maximum number of login attempts
        
        for i in range(max_login_attempts):
            Admin_ID = input('\nEnter your Admin ID: ')
            Password = maskpass.askpass('Enter your password: ')

            cursor.execute("SELECT Password FROM admin_info WHERE Admin_ID = %s", (Admin_ID,))
            result = cursor.fetchone()

            if not result:
                print('\nLogin unsuccessful. Admin ID not found.')
                
            elif result[0] is None:  # Check if the stored password is None (no password required)
                print('\nLogin successful (no password required).')
                logged_in_admin_id = Admin_ID
                admin_menu(logged_in_admin_id)
                return Admin_ID
            
            elif not Password:  # Check if the password is empty
                print('\nLogin unsuccessful. Password is required.')
            else:
                stored_password = result[0].encode('utf-8')
                input_password_bytes = Password.encode('utf-8')

                if bcrypt.checkpw(input_password_bytes, stored_password):  # Compare using checkpw
                    print('\nLogin successful.')
                    logged_in_admin_id = Admin_ID
                    admin_menu(logged_in_admin_id)
                    return Admin_ID
                else:
                    print('\nLogin unsuccessful. Wrong credentials.')

        print('\nLogin failed. Maximum login attempts reached. Check for errors or seek help from an admin.')
        return None

    # create admin method
    def create_admin(self):  
        Admin_ID = input('Enter Admin ID:')

        # Check if the admin_id already exists in the database
        cursor.execute("SELECT COUNT(*) FROM admin_info WHERE Admin_ID = %s", (Admin_ID,))
        result = cursor.fetchone()

        if result[0] > 0:
            print('This Admin ID is already in the system.')
            return None

        Firstname = input("Enter Admin first name: ")
        Lastname = input("Enter Admin last name: ")
        while True:
            hiredate_str = input("Enter Admin hire date (yyyy-mm-dd): ")
            try:
                Hiredate = datetime.strptime(hiredate_str, "%Y-%m-%d")
                break
            except ValueError:
                print("Incorrect date format. Please use yyyy-mm-dd.")
        email = input('Enter Admin email: ')
        Password = maskpass.askpass('Enter a password:')

        # Generate a random salt
        salt = bcrypt.gensalt()

        # Encode the password to bytes
        password_bytes = Password.encode('utf-8')

        # Hash the password with the salt
        hashed_password = bcrypt.hashpw(password_bytes, salt)

        admin = Admin(Admin_ID, Firstname, Lastname, Hiredate, email, hashed_password)  

        insert_query = "INSERT INTO admin_info (Admin_ID, Firstname, Lastname, Hiredate, email, Password) VALUES (%s, %s, %s, %s, %s, %s)"
        values = (Admin_ID, Firstname, Lastname, Hiredate, email, hashed_password)  

        cursor.execute(insert_query, values)
        mydb.commit()
        print('\nAdmin creation successful.')
    
    def update_password(self, admin_ID):
        try:
            # Check if the admin exists
            cursor.execute("SELECT COUNT(*) FROM admin_info WHERE Admin_ID = %s", (admin_ID,))
            result = cursor.fetchone()

            if result[0] == 0:
                print(f"Admin with ID {admin_ID} not found.")
                return

            Password = maskpass.askpass('Enter new password: ')
            salt = bcrypt.gensalt()
            password_bytes = Password.encode('utf-8')
            hashed_password = bcrypt.hashpw(password_bytes, salt)

            # Update the password for the specific admin
            update_query = "UPDATE admin_info SET Password = %s WHERE Admin_ID = %s"
            values = (hashed_password, admin_ID)
            cursor.execute(update_query, values)
            mydb.commit()

            print(f"Password for Admin {admin_ID} updated successfully.")

        except mysql.connector.Error as err:
            print(f"Error: {err}")

class Customer:
    def __init__(self, Customer_ID, Admin_ID, Firstname, Lastname, Age, email):
        self.Customer_ID = Customer_ID  
        self.Admin_ID = Admin_ID
        self.Firstname = Firstname
        self.Lastname = Lastname 
        self.Age = Age 
        self.email = email
    
    # adding customer method that adds to the database
    def add_customer_info(admin_id):
    
        Customer_ID = input('Enter Customer ID: ').upper()
        Admin_ID = admin_id

        # Check if the customer_id already exists in the database
        cursor.execute("SELECT COUNT(*) FROM customer_info WHERE customer_ID = %s", (Customer_ID,))
        result = cursor.fetchone()

        if result[0] > 0:
            print('This Customer ID is already in the system.')
            return None

        Firstname = input("Enter first name: ")
        Lastname = input("Enter last name: ")
        Age = input("Enter age: ")
        email = input('Enter email: ')

        customer = Customer(Customer_ID, Admin_ID, Firstname, Lastname, Age, email) 

        insert_query = "INSERT INTO customer_info (Customer_ID, Admin_ID, Firstname, Lastname, age, email) VALUES (%s, %s, %s, %s, %s, %s)"
        values = (Customer_ID, Admin_ID, Firstname, Lastname, Age, email)  # Note: Wrap the values in a tuple
        cursor.execute(insert_query, values)
        mydb.commit()

        print('\nCumtomer added successfully.')
        
    # modifing customer information from database
    def modify_customer_info():
    
        try:
            # Prompt the user for a customer ID
            selected_customer_id = input("Enter Customer ID to update information: ")

            # SQL query to select customer data for the specified customer ID
            query = "SELECT * FROM customer_info WHERE Customer_ID = %s"

            # Execute the query with the provided customer ID
            cursor.execute(query, (selected_customer_id,))
            customer_data = cursor.fetchone()  # Fetch one row (assuming customer IDs are unique)

            if customer_data:
  
                edit_choice = input("\nWhat would you like to edit?\n \n[1] First Name \n[2] Last Name \n[3] Age \n[4] Email  \n[5] All\n \nEnter your choice: ").lower()

                if edit_choice =='1':

                    new_Firstname = input("Update First Name to: ")
                    update_query = "UPDATE customer_info SET Firstname = %s WHERE Customer_ID = %s"
                    values = (new_Firstname, selected_customer_id)
                    cursor.execute(update_query, values)
                    mydb.commit()

                elif edit_choice == '2':

                    new_Lastname = input("Update Last Name to: ")
                    update_query = "UPDATE customer_info SET Lastname = %s WHERE Customer_ID = %s"
                    values = (new_Lastname, selected_customer_id)
                    cursor.execute(update_query, values)
                    mydb.commit()

                elif edit_choice == '3':

                    new_Age = input("Update Age to: ") 
                    update_query = "UPDATE customer_info SET Age = %s, WHERE Customer_ID = %s"
                    values = (new_Age, selected_customer_id)
                    cursor.execute(update_query, values)
                    mydb.commit()
                    
                elif edit_choice == '4':

                    new_Email = input("Update Email to: ") 
                    update_query = "UPDATE customer_info SET email = %s WHERE Customer_ID = %s"
                    values = (new_email, selected_customer_id)
                    cursor.execute(update_query, values)
                    mydb.commit()
                    
                elif edit_choice == '5':

                    new_Firstname = input("Update First Name to: ")
                    new_Lastname = input("Update Last Name to: ")
                    new_Age = input("Update Age to: ")
                    new_email = input("Update Email to: ")
                    update_query = "UPDATE customer_info SET Firstname = %s, Lastname = %s, Age = %s, email = %s WHERE Customer_ID = %s"
                    values = (new_Firstname, new_Lastname, new_Age, new_email, selected_customer_id)
                    cursor.execute(update_query, values)
                    mydb.commit()                    
            else:
                print(f"Customer with ID {selected_customer_id} not found.")

        except mysql.connector.Error as err:
            print(f"Error: {err}")    
            
    # showing customer information from database
    def show_customer_info(admin_id):
        try:
            # SQL query to select customer data for the specified admin
            query = "SELECT Customer_ID, Firstname, Lastname FROM customer_info WHERE Admin_ID = %s"
            
            # Execute the query with the provided admin ID
            cursor.execute(query, (admin_id,))
            customer_data = cursor.fetchall()
            
            if not customer_data:
                print("No customers found for this admin.")
                return
            
            print("\nCustomers under your administration:\n------------------------------------")
            for row in customer_data:
                # Display the list of customers
                customer_id, first_name, last_name = row
                print(f"Customer ID: {customer_id}, Name: {first_name} {last_name}")
            
            # Prompt the admin to select a customer to view
            selected_customer_id = input("\nEnter the Customer ID you would like to view: ")
            
            # Check if the selected_customer_id is valid and exists under the admin
            valid_customer_ids = [str(row[0]) for row in customer_data]
            if selected_customer_id in valid_customer_ids:
                # Retrieve and display detailed customer information
                query = "SELECT * FROM customer_info WHERE Customer_ID = %s"
                cursor.execute(query, (selected_customer_id,))
                customer_info = cursor.fetchone()
                
                if customer_info:
                    # Display detailed customer information
                    print("\nCustomer Information:")
                    customer_id, admin_id, first_name, last_name, age, email = customer_info
                    print(f"Customer ID: {customer_id}")
                    print(f"Admin ID: {admin_id}")
                    print(f"First Name: {first_name}")
                    print(f"Last Name: {last_name}")
                    print(f"Age: {age}")
                    print(f"Email: {email}")
                else:
                    print("Customer not found.")
            else:
                print(f"\nYou do not have access to view information for this Customer.")
        
        except mysql.connector.Error as err:
            print(f"Error: {err}")

    # add to expenses tables in database
    def add_expenses_info(admin_id):
    
        try:
        
            # SQL query to select customers under the provided admin ID
            query = "SELECT Customer_ID, Firstname, Lastname, Admin_ID FROM customer_info WHERE Admin_ID = %s"

            # Execute the query with the provided admin ID
            cursor.execute(query, (admin_id,))
            customer_data = cursor.fetchall()  # Fetch all rows for the admin

            if not customer_data:
                print("No customers found for this Admin ID.")
                return

            print("\nCustomers under your administration:")
            print('---------------------------------------')
            for row in customer_data:
                # Extract and display customer ID, name, and admin ID
                customer_id, firstname, lastname, customer_admin_id = row
                print(f"Customer ID: {customer_id}, Name: {firstname} {lastname}")

            # Prompt for customer ID to add expenses info
            selected_customer_id = input("\nEnter Customer ID to add expenses info: ")

            # Check if the selected customer belongs to the current admin
            valid_customer_ids = [str(row[0]) for row in customer_data]
            if selected_customer_id not in valid_customer_ids:
                print(f"\nYou do not have access for that Customer.")
                return
            
            # Prompt for month and year to add expenses info
            month = input("Enter Month and Year: ")
                    
            # SQL query to check if expense info for given month and year already exists
            query = "SELECT * FROM expenses WHERE Customer_ID = %s and month = %s"

            # Execute the query with the provided customer id and month
            cursor.execute(query, (selected_customer_id,month))
            customer_data = cursor.fetchone()
                       
            if customer_data is None:
                               
                
                income = float(input("What was your Income: "))
                expenditure_goal = float(input("What is your Expenditure Goal: "))
                rent = float(input("How much rent you paid for this month: "))
                groceries = float(input("How much did you spend on groceries: "))
                utilities = float(input("How much did you paid for Utilities: "))
                other_costs = float(input("How much did you spend on other things: "))
                total_amount_spent = rent + groceries + utilities + other_costs
                remaining_amount = income - total_amount_spent
                
                insert_expense_query = "INSERT INTO expenses (Customer_Id, Admin_ID, Month, Income, Expenditure_Goal, Rent, Groceries, Utilities, Other_Costs,  Total_Amount_Spent, Remaining_Amount) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                values = (selected_customer_id, admin_id, month, income, expenditure_goal, rent, groceries, utilities, other_costs,  total_amount_spent, remaining_amount)  # Note: Wrap the values in a tuple
                cursor.execute(insert_expense_query, values)
                mydb.commit()
                
                print(f"\nIncome/Expense for {month} added for Customer {selected_customer_id}")
            
            else: 
                print(f"\nCustomer {selected_customer_id} already has income/expense record for {month}")
                return     
            
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            
    # modifying expenses from database 
    def modify_expenses_info(admin_id):
        try:
            
            # SQL query to select customers under the provided admin ID
            query = "SELECT Customer_ID, Firstname, Lastname, Admin_ID FROM customer_info WHERE Admin_ID = %s"

            # Execute the query with the provided admin ID
            cursor.execute(query, (admin_id,))
            customer_data = cursor.fetchall()  # Fetch all rows for the admin

            if not customer_data:
                print("No customers found for this Admin ID.")
                return

            print("\nCustomers under your administration:")
            print('---------------------------------------')
            for row in customer_data:
                # Extract and display customer ID, name, and admin ID
                customer_id, firstname, lastname, customer_admin_id = row
                print(f"Customer ID: {customer_id}, Name: {firstname} {lastname}")

            # Prompt for customer ID to modify expenses info
            selected_customer_id = input("\nEnter Customer ID to modify Expenses info: ")
            
            # Check if the selected customer belongs to the current admin
            valid_customer_ids = [str(row[0]) for row in customer_data]
            if selected_customer_id not in valid_customer_ids:
                print(f"\nYou do not have access for this Customer.")
                return
                
            month = input("Enter the month and year for which you want to update the Expenses Info: ")

            # SQL query to select customer data for the specified customer ID
            query = "SELECT * FROM expenses WHERE Customer_ID = %s and Month = %s"

            # Execute the query with the provided customer ID
            cursor.execute(query, (selected_customer_id, month))
            customer_data = cursor.fetchone()  # Fetch one row (assuming customer IDs are unique)

            if customer_data:
  
                edit_choice = input("\nWhat would you like to edit?\n \n[1] Income \n[2] Expenditure_Goal \n[3] Rent \n[4] Groceries  \n[5] Utilities \n[6] Other_Costs \n[7] All \n \nEnter your choice: ").lower()

                if edit_choice =='1':

                    new_income = float(input("Update Income to: "))
                    total_amount_spent = float(customer_data[9])
                    remaining_amount = new_income - total_amount_spent
                    update_query = "UPDATE expenses SET Income = %s, Remaining_Amount = %s WHERE Customer_ID = %s and Month = %s"
                    values = (new_income, remaining_amount, customer_id, month)
                    cursor.execute(update_query, values)
                    mydb.commit()

                elif edit_choice == '2':

                    new_expenditure_goal = float(input("Update Expenditure Goal to: "))
                    update_query = "UPDATE expenses SET Expenditure = %s WHERE Customer_ID = %s and Month = %s"
                    values = (new_expenditure_goal, customer_id, month)
                    cursor.execute(update_query, values)
                    mydb.commit()

                elif edit_choice == '3':

                    new_rent = float(input("Update Rent to: "))
                    total_amount_spent = new_rent + float(customer_data[6]) + float(customer_data[7]) + float(customer_data[8])
                    remaining_amount = float(customer_data[3]) - total_amount_spent
                    update_query = "UPDATE expenses SET Rent = %s, Total_Amount_Spent = %s, Remaining_Amount = %s WHERE Customer_ID = %s and Month = %s"
                    values = (new_rent, total_amount_spent, remaining_amount, customer_id, month)
                    cursor.execute(update_query, values)
                    mydb.commit()
                    
                elif edit_choice == '4':

                    new_groceries = float(input("Update Groceries to: "))
                    total_amount_spent = float(customer_data[5]) + new_groceries + float(customer_data[7]) + float(customer_data[8])
                    remaining_amount = float(customer_data[3]) - total_amount_spent
                    update_query = "UPDATE expenses SET Groceries = %s, Total_Amount_Spent = %s, Remaining_Amount = %s WHERE Customer_ID = %s and Month = %s"
                    values = (new_groceries, total_amount_spent, remaining_amount, customer_id, month)
                    cursor.execute(update_query, values)
                    mydb.commit()
                    
                elif edit_choice == '5':

                    new_utilities = float(input("Update Utilities to: "))
                    total_amount_spent = float(customer_data[5]) + float(customer_data[6]) + new_utilities + float(customer_data[8])
                    remaining_amount = float(customer_data[3]) - total_amount_spent
                    update_query = "UPDATE expenses SET Utilities = %s, Total_Amount_Spent = %s, Remaining_Amount = %s WHERE Customer_ID = %s and Month = %s"
                    values = (new_utilities,total_amount_spent, remaining_amount, customer_id, month)
                    cursor.execute(update_query, values)
                    mydb.commit()
                    
                elif edit_choice == '6':

                    new_other_costs = float(input("Update Other Costs to: "))
                    total_amount_spent = float(customer_data[5]) + float(customer_data[6]) + float(customer_data[7]) + new_other_costs
                    remaining_amount = float(customer_data[3]) - total_amount_spent
                    update_query = "UPDATE expenses SET Other_Costs = %s, Total_Amount_Spent = %s, Remaining_Amount = %s WHERE Customer_ID = %s and Month = %s"
                    values = (new_other_costs, total_amount_spent, remaining_amount, customer_id, month)
                    cursor.execute(update_query, values)
                    mydb.commit()
                    
                elif edit_choice == '7':

                    new_income = float(input("Update Income to: "))
                    new_expenditure_goal = float(input("Update Expenditure_Goal to: "))
                    new_rent = float(input("Update Rent to: "))
                    new_groceries = float(input("Update Groceries to: "))
                    new_utilities = float(input("Update Utilities to: "))
                    new_other_costs = float(input("Update Other_Costs to: "))
                    total_amount_spent = new_rent + new_groceries + new_utilities + new_other_costs
                    remaining_amount = new_income - total_amount_spent
                    update_query = "UPDATE expenses SET Income = %s, Expenditure_Goal = %s, Rent = %s, Groceries = %s, Utilities = %s, Other_Costs = %s Total_Amount_Spent = %s, Remaining_Amount = %s WHERE Customer_ID = %s and Month = %s"
                    values = (new_income, new_expenditure_goal, new_rent, new_groceries, new_utilities, new_other_costs, total_amount_spent, remaining_amount, customer_id, month)
                    cursor.execute(update_query, values)
                    mydb.commit()                    
            else:
                print(f"Customer {selected_customer_id} has no income/expense record for {month}.")

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            
    # show expenses information from database
    def show_expenses_info(admin_id):
        try:
            # SQL query to select customers under the provided admin ID
            query = "SELECT Customer_ID, Firstname, Lastname, Admin_ID FROM customer_info WHERE Admin_ID = %s"

            # Execute the query with the provided admin ID
            cursor.execute(query, (admin_id,))
            customer_data = cursor.fetchall()  # Fetch all rows for the admin

            if not customer_data:
                print("No customers found for this Admin ID.")
                return

            print("\nCustomers under your administration:")
            print('---------------------------------------')
            for row in customer_data:
                # Extract and display customer ID, name, and admin ID
                customer_id, firstname, lastname, customer_admin_id = row
                print(f"Customer ID: {customer_id}, Name: {firstname} {lastname}")

            # Prompt for customer ID to view expenses info
            selected_customer_id = input("\nEnter Customer ID to view expenses info: ")

            # Check if the selected customer belongs to the current admin
            valid_customer_ids = [str(row[0]) for row in customer_data]
            if selected_customer_id not in valid_customer_ids:
                print(f"\nYou do not have access to view expenses for that Customer.")
                return

            # SQL query to select expenses data for the selected customer ID
            query = "SELECT * FROM expenses WHERE Customer_ID = %s"

            # Execute the query with the provided customer ID
            cursor.execute(query, (selected_customer_id,))
            expenses_data = cursor.fetchall()

            if not expenses_data:
                print("No expenses information found for this Customer ID.")
                return

            print("\nExpenses Information:")
            for row in expenses_data:
                # Extract and display relevant columns
                Customer_ID, Admin_ID, Month, Income, Expenditure_Goal, Rent, Groceries, Utilities, Other_Costs, Total_Amount_Spent, Remaining_Amount = row
                print(f"Customer ID: {Customer_ID}")
                print(f"Admin ID: {Admin_ID}")
                print(f"Month: {Month}")
                print(f"Income: {Income}")
                print(f"Expenditure Goal: {Expenditure_Goal}")
                print(f"Rent: {Rent}")
                print(f"Groceries: {Groceries}")
                print(f"Utilities: {Utilities}")
                print(f"Other Costs: {Other_Costs}")
                print(f"Total Amount Spent: {Total_Amount_Spent}")
                print(f"Remaining Amount: {Remaining_Amount}")
                print("\n")

        except mysql.connector.Error as err:
            print(f"Error: {err}")

    # add to savings table in database
    def add_savings_info(admin_id):
        try:
        
            # SQL query to select customers under the provided admin ID
            query = "SELECT Customer_ID, Firstname, Lastname, Admin_ID FROM customer_info WHERE Admin_ID = %s"

            # Execute the query with the provided admin ID
            cursor.execute(query, (admin_id,))
            customer_data = cursor.fetchall()  # Fetch all rows for the admin

            if not customer_data:
                print("No customers found for this Admin ID.")
                return

            print("\nCustomers under your administration:")
            print('---------------------------------------')
            for row in customer_data:
                # Extract and display customer ID, name, and admin ID
                customer_id, firstname, lastname, customer_admin_id = row
                print(f"Customer ID: {customer_id}, Name: {firstname} {lastname}")

            # Prompt for customer ID to add savings info
            selected_customer_id = input("\nEnter Customer ID to add savings info: ")

            # Check if the selected customer belongs to the current admin
            valid_customer_ids = [str(row[0]) for row in customer_data]
            if selected_customer_id not in valid_customer_ids:
                print(f"\nYou do not have access for that Customer.")
                return
            
            # Prompt for month and year to add savings info
            month = input("Enter Month and Year: ")
            
            
            # SQL query to check if savings info for given month and year already exists
            query = "SELECT * FROM savings WHERE Customer_ID = %s and month = %s"

            # Execute the query with the provided customer id and month
            cursor.execute(query, (selected_customer_id,month))
            customer_data = cursor.fetchone()
            
            
            if customer_data is None:
                               
                # SQL query to fetch the value of remaining amount from expenses info for given customer Id and month year.
                query = "SELECT Remaining_Amount FROM expenses WHERE Customer_ID = %s and month = %s"

                # Execute the query with the provided customer id and month
                cursor.execute(query, (selected_customer_id,month))
                amount_remaining_data= cursor.fetchone()
                
                if amount_remaining_data is None:
                    print(f"\nPlease first fill in the income/expense info of Customer {selected_customer_id} for {month}")
                else:
                    amount_remaining = amount_remaining_data[0]
                    amount_put_into_savings = float(input("How much you want to put into savings for this month: "))
                    monthly_interest_rate = float(input("Enter monthly interest rate: "))
                    
                    # SQL query to fetch the previous total savings for the provided customer id
                    query = "SELECT max(Total_Savings) FROM savings WHERE Customer_ID = %s"
                   
                   # Execute the query with the provided customer id and month
                    cursor.execute(query, (selected_customer_id,))
                    total_savings_data= cursor.fetchone()
                    
                    if total_savings_data is not None:
                        total_savings = float(total_savings_data[0]) + (amount_put_into_savings * (monthly_interest_rate)/100)
                    else:
                        total_savings = amount_put_into_savings * (monthly_interest_rate)/100
                    
                    
                    insert_savings_query = "INSERT INTO savings (Customer_Id, Admin_ID, Month, Amount_Remaining, Amount_Put_Into_Savings, Monthly_Interest_Rate, Total_Savings) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                    values = (selected_customer_id, admin_id, month, amount_remaining, amount_put_into_savings, monthly_interest_rate, total_savings )  # Note: Wrap the values in a tuple
                    cursor.execute(insert_savings_query, values)
                    mydb.commit()
                    
                    print(f"\nSavings for {month} added for Customer {selected_customer_id}")
            
            else: 
                print(f"\nCustomer {selected_customer_id} already has savings record for {month}")
                return     
            
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        
    # modify savings table from database 
    def modify_savings_info(admin_id):
        
        try:
            
            # SQL query to select customers under the provided admin ID
            query = "SELECT Customer_ID, Firstname, Lastname, Admin_ID FROM customer_info WHERE Admin_ID = %s"

            # Execute the query with the provided admin ID
            cursor.execute(query, (admin_id,))
            customer_data = cursor.fetchall()  # Fetch all rows for the admin

            if not customer_data:
                print("No customers found for this Admin ID.")
                return

            print("\nCustomers under your administration:")
            print('---------------------------------------')
            for row in customer_data:
                # Extract and display customer ID, name, and admin ID
                customer_id, firstname, lastname, customer_admin_id = row
                print(f"Customer ID: {customer_id}, Name: {firstname} {lastname}")

            # Prompt for customer ID to modify expenses info
            selected_customer_id = input("\nEnter Customer ID to modify Savings info: ")
            
            # Check if the selected customer belongs to the current admin
            valid_customer_ids = [str(row[0]) for row in customer_data]
            if selected_customer_id not in valid_customer_ids:
                print(f"\nYou do not have access for this Customer.")
                return
                
            month = input("Enter the month and year for which you want to update the Savings Info: ")

            # SQL query to select customer data for the specified customer ID
            query = "SELECT * FROM savings WHERE Customer_ID = %s and Month = %s"

            # Execute the query with the provided customer ID
            cursor.execute(query, (selected_customer_id, month))
            customer_data = cursor.fetchone()  # Fetch one row (assuming customer IDs are unique)
            
            if customer_data:
  
                edit_choice = input("\nWhat would you like to edit?\n \n[1] Amount to put into Savings \n[2] Monthly Interest Rate \n[3] All \n \nEnter your choice: ").lower()

                if edit_choice =='1':

                    new_amount_put_into_savings = float(input("Enter amount to put into savings: "))
                    new_total_savings = new_amount_put_into_savings * float(customer_data[6])/100
                    update_query = "UPDATE savings SET Amount_Put_Into_Savings = %s, Total_Savings = %s WHERE Customer_ID = %s and Month = %s"
                    values = (new_amount_put_into_savings, new_total_savings, selected_customer_id, month)
                    cursor.execute(update_query, values)
                    mydb.commit()

                elif edit_choice == '2':

                    new_monthly_interest_rate = float(input("Enter new monthly interest rate: "))
                    new_total_savings = float(customer_data[5]) * (new_monthly_interest_rate)/100
                    update_query = "UPDATE savings SET Monthly_Interest_Rate = %s Total_Savings = %s WHERE Customer_ID = %s and Month = %s"
                    values = (new_monthly_interest_rate, new_total_savings, selected_customer_id, month)
                    cursor.execute(update_query, values)
                    mydb.commit()
                    
                elif edit_choice == '3':

                    new_amount_put_into_savings = float(input("Enter amount to put into savings: "))
                    new_monthly_interest_rate = float(input("Enter new monthly interest rate: "))
                    new_total_savings = new_amount_put_into_savings * (new_monthly_interest_rate)/100
                    update_query = "UPDATE savings SET Amount_Put_Into_Savings = %s, Monthly_Interest_Rate = %s Total_Savings = %s WHERE Customer_ID = %s and Month = %s"
                    values = (new_amount_put_into_savings, new_monthly_interest_rate, new_total_savings, selected_customer_id, month)
                    cursor.execute(update_query, values)
                    mydb.commit()
                    
                else:
                    print(f"Customer {selected_customer_id} has no savings record for {month}.")

        except mysql.connector.Error as err:
            print(f"Error: {err}")
        
    # show savings information from database
    def show_savings_info(admin_id):
        try:
            # SQL query to select customers under the provided admin ID
            query = "SELECT Customer_ID, Firstname, Lastname FROM customer_info WHERE Admin_ID = %s"
            
            # Execute the query with the provided admin ID
            cursor.execute(query, (admin_id,))
            customer_data = cursor.fetchall()  # Fetch all rows for the admin
            
            if not customer_data:
                print("No customers found for this Admin ID.")
                return
            
            print("\nCustomers under your administration:")
            print('---------------------------------------')
            for row in customer_data:
                # Extract and display customer ID and name
                customer_id, firstname, lastname = row
                print(f"Customer ID: {customer_id}, Name: {firstname} {lastname}")

            # Prompt for customer ID to view savings info
            selected_customer_id = input("\nEnter Customer ID to view savings info: ")

            # Check if the selected_customer_id is valid and exists under the admin
            valid_customer_ids = [str(row[0]) for row in customer_data]
            if selected_customer_id in valid_customer_ids:
                # SQL query to select savings data for the selected customer ID
                query = "SELECT * FROM savings WHERE Customer_ID = %s"
                
                # Execute the query with the provided customer ID
                cursor.execute(query, (selected_customer_id,))
                savings_data = cursor.fetchall()

                if not savings_data:
                    print("No savings information found for this Customer ID.")
                    return

                print("\nSavings Information:")
                for row in savings_data:
                    # Extract and display relevant columns
                    Customer_ID, Admin_ID, Month, Amount_Remaining, Amount_Put_Into_Savings, Monthly_Interest_Rate, Total_Savings  = row
                    print(f"Customer ID: {Customer_ID}")
                    print(f"Admin ID: {Admin_ID}")
                    print(f"Month: {Month}")
                    print(f"Amount Remaining: {Amount_Remaining}")
                    print(f"Amount Put Into Savings: {Amount_Put_Into_Savings}")
                    print(f"Monthly Interest Rate: {Monthly_Interest_Rate}")
                    print(f"Total Savings: {Total_Savings}")
                    print("\n")
            else:
                print(f"\nYou do not have access to view savings information for that Customer.")

        except mysql.connector.Error as err:
            print(f"Error: {err}")

    # adding information to debt table in database
    def add_debt_info(admin_id):
    
        try:
        
            # SQL query to select customers under the provided admin ID
            query = "SELECT Customer_ID, Firstname, Lastname, Admin_ID FROM customer_info WHERE Admin_ID = %s"

            # Execute the query with the provided admin ID
            cursor.execute(query, (admin_id,))
            customer_data = cursor.fetchall()  # Fetch all rows for the admin

            if not customer_data:
                print("No customers found for this Admin ID.")
                return

            print("\nCustomers under your administration:")
            print('---------------------------------------')
            for row in customer_data:
                # Extract and display customer ID, name, and admin ID
                customer_id, firstname, lastname, customer_admin_id = row
                print(f"Customer ID: {customer_id}, Name: {firstname} {lastname}")

            # Prompt for customer ID to add debt info
            selected_customer_id = input("\nEnter Customer ID to add debt info: ")

            # Check if the selected customer belongs to the current admin
            valid_customer_ids = [str(row[0]) for row in customer_data]
            if selected_customer_id not in valid_customer_ids:
                print(f"\nYou do not have access for that Customer.")
                return
            
            # Prompt for month and year to add debt info
            month = input("Enter Month and Year: ")
            
            
            # SQL query to check if debt info for given month and year already exists
            query = "SELECT * FROM debt WHERE Customer_ID = %s and month = %s"

            # Execute the query with the provided customer id and month
            cursor.execute(query, (selected_customer_id,month))
            customer_data = cursor.fetchone()
            
            
            if customer_data is None:
                               
                # SQL query to fetch the value of remaining amount from expenses info for given customer Id and month year.
                query = "SELECT Remaining_Amount FROM expenses WHERE Customer_ID = %s and month = %s"

                # Execute the query with the provided customer id and month
                cursor.execute(query, (selected_customer_id,month))
                amount_remaining_data= cursor.fetchone()
               
                if amount_remaining_data is None:
                    print(f"\nPlease first fill in the income/expense info of Customer {selected_customer_id} for {month}")
                else:
                    amount_remaining = float(amount_remaining_data[0])
                    debt_remaining = float(input("How much debt remaining: "))
                    interest_rate_percent = float(input("Enter monthly interest rate: "))/100
                    amount_paid = float(input("How much amount you paid this month: "))
                    
                    
                    insert_debt_query = "INSERT INTO debt (Customer_Id, Admin_ID, Month, Amount_Remaining, Debt_Remaining, Interest_Rate_Percent, Amount_Paid) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                    values = (selected_customer_id, admin_id, month, amount_remaining, debt_remaining, interest_rate_percent, amount_paid)  # Note: Wrap the values in a tuple
                    cursor.execute(insert_debt_query, values)
                    mydb.commit()
                    
                    print(f"\nDebt for {month} added for Customer {selected_customer_id}")
            
            else: 
                print(f"\nCustomer {selected_customer_id} already has debt record for {month}")
                return     
            
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        
    # modifying debt information table from database   
    def modify_debt_info(admin_id):
        try:
            
            # SQL query to select customers under the provided admin ID
            query = "SELECT Customer_ID, Firstname, Lastname, Admin_ID FROM customer_info WHERE Admin_ID = %s"

            # Execute the query with the provided admin ID
            cursor.execute(query, (admin_id,))
            customer_data = cursor.fetchall()  # Fetch all rows for the admin

            if not customer_data:
                print("No customers found for this Admin ID.")
                return

            print("\nCustomers under your administration:")
            print('---------------------------------------')
            for row in customer_data:
                # Extract and display customer ID, name, and admin ID
                customer_id, firstname, lastname, customer_admin_id = row
                print(f"Customer ID: {customer_id}, Name: {firstname} {lastname}")

            # Prompt for customer ID to modify expenses info
            selected_customer_id = input("\nEnter Customer ID to modify Debt info: ")
            
            # Check if the selected customer belongs to the current admin
            valid_customer_ids = [str(row[0]) for row in customer_data]
            if selected_customer_id not in valid_customer_ids:
                print(f"\nYou do not have access for this Customer.")
                return
                
            month = input("Enter the month and year for which you want to update the Debt Info: ")

            # SQL query to select customer data for the specified customer ID
            query = "SELECT * FROM expenses WHERE Customer_ID = %s and Month = %s"

            # Execute the query with the provided customer ID
            cursor.execute(query, (selected_customer_id, month))
            customer_data = cursor.fetchone()  # Fetch one row (assuming customer IDs are unique)
            
            if customer_data:
  
                edit_choice = input("\nWhat would you like to edit?\n \n[1] Amount to put into Savings \n[2] Monthly Interest Rate \n[3] All \n \nEnter your choice: ").lower()

                if edit_choice =='1':

                    new_amount_put_into_savings = float(input("Enter amount to put into savings: "))
                    new_total_savings = new_amount_put_into_savings * (monthly_interest_rate)/100
                    update_query = "UPDATE savings SET Amount_Put_Into_Savings = %s, Total_Savings = %s WHERE Customer_ID = %s and Month = %s"
                    values = (new_amount_put_into_savings, new_total_savings, selected_customer_id, month)
                    cursor.execute(update_query, values)
                    mydb.commit()

                elif edit_choice == '2':

                    new_monthly_interest_rate = float(input("Enter new monthly interest rate: "))
                    new_total_savings = amount_put_into_savings * (new_monthly_interest_rate)/100
                    update_query = "UPDATE savings SET Monthly_Interest_Rate = %s Total_Savings = %s WHERE Customer_ID = %s and Month = %s"
                    values = (new_monthly_interest_rate, new_total_savings, selected_customer_id, month)
                    cursor.execute(update_query, values)
                    mydb.commit()
                    
                    
                else:
                    print(f"Customer {selected_customer_id} has no savings record for {month}.")

        except mysql.connector.Error as err:
            print(f"Error: {err}")
    # show debt information from database   
    def show_debt_info(admin_id):
        try:
            # SQL query to select customers under the provided admin ID
            query = "SELECT customer_info.Customer_ID, customer_info.Firstname, customer_info.Lastname FROM customer_info WHERE Admin_ID = %s"
            
            # Execute the query with the provided admin ID
            cursor.execute(query, (admin_id,))
            customer_data = cursor.fetchall()  # Fetch all rows for the admin
            
            if not customer_data:
                print("\nNo customers found for this Admin ID.")
                return
            
            print("\nCustomers under your administration:")
            print("------------------------------------")
            for row in customer_data:
                # Extract and display customer ID and name
                customer_id, firstname, lastname = row
                print(f"Customer ID: {customer_id}, Name: {firstname} {lastname}")

            # Prompt for customer ID to view debt info
            selected_customer_id = input("\nEnter Customer ID to view debt info: ")

            # Check if the selected_customer_id is valid and exists under the admin
            valid_customer_ids = [str(row[0]) for row in customer_data]
            if selected_customer_id in valid_customer_ids:
                # SQL query to select debt data for the selected customer ID
                query = "SELECT * FROM debt WHERE Customer_ID = %s"
                
                # Execute the query with the provided customer ID
                cursor.execute(query, (selected_customer_id,))
                debt_data = cursor.fetchall()

                if not debt_data:
                    print("\nNo debt information found for this Customer ID.")
                    return

                print("\nDebt Information:")
                for row in debt_data:
                    # Extract and display relevant columns
                    Customer_ID, Admin_ID, Month, Amount_Remaining, Debt_Remaining, Interest_Rate_Percent, Amount_Paid = row
                    print(f"Customer ID: {Customer_ID}")
                    print(f"Admin ID: {Admin_ID}")
                    print(f"Month: {Month}")
                    print(f"Amount Remaining: {Amount_Remaining}")
                    print(f"Debt Remaining: {Debt_Remaining}")
                    print(f"Interest Rate Percent: {Interest_Rate_Percent}")
                    print(f"Amount Paid: {Amount_Paid}")
                    print("\n")
            else:
                print(f"\nYou do not have access to view debt information for that Customer.")

        except mysql.connector.Error as err:
            print(f"Error: {err}")

# function exporting most recent data to csv format
def export_table_to_csv(table_name, file_name):
    try:
        # SQL query to select all data from the specified table
        query = f"SELECT * FROM {table_name}"

        # Execute the query
        cursor.execute(query)

        # Fetch all rows
        data = cursor.fetchall()

        if not data:
            print(f"No data found in the {table_name} table.")
            return

        # Get the column names from the cursor description
        column_names = [desc[0] for desc in cursor.description]

        # Write the data to a CSV file
        with open(file_name, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            
            # Write the header row with column names
            csv_writer.writerow(column_names)
            
            # Write the data rows
            csv_writer.writerows(data)
        
        print(f"Data from {table_name} table to {file_name} has been created successfully.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

# savings calculator function 
def savings_calculator():
    total = int(input("Please enter your starting value : £"))
    adding = float(input("Approximately, how much would you like to enter into your savings each month: £"))
    ir = float(input("Please enter the monthly interest rate (%): "))
    months = int(input("How many months ahead would you like to calculate the total savings?: "))
    total_amount = {}
    print('\n')
    i = 1

    while i<= months:
        total = round((total+adding)*(1+ir/100),2)
        total_amount[f'month {i}'] = total
        i += 1

    for month in total_amount:
        print(f"{month} = {total_amount[month]}")

def debt_payoff_calulator():

    starting_debt = float(input("Starting debt: £"))
    debt = copy.deepcopy(starting_debt)
    paying = float(input("Approximately how much is being paid off each month: £"))
    IR = float(input("Monthly interest rate (%): "))
    IR_increase = float(input("Monthly increase in interest rate: "))
    #months = 12
    debt_dict = {}

    i = 1

    while debt>=0:
        if i == 1:
            debt = (debt-paying)*(1+(IR)/100)
        else:
            debt = (debt-paying)*(1+(IR+IR_increase)/100)
        debt_dict[f'Month {i}'] = round(debt,2)
        i += 1

    print("\n")
    for month in debt_dict:
        print(f"{month} = {debt_dict[month]}")

    print("\n")
    print(f"It will take you approximately {i-1} months to pay off a debt of £{starting_debt}.")
    print(f"Given that £{paying} is paid off every month with an starting interest rate of {IR}% which increases by {IR_increase}% each month.")

admin = Admin(None, None, None, None, None, None)
# admin menu
def admin_menu(admin_id):
    while True:

        print('\n+---------------------------+\n|Financial Management System|\n+---------------------------+')
        print(f'\nLogged in as Admin: {admin_id}')
        print('\n[1] Customer Profile \n[2] Expenses Report \n[3] Savings Report')
        print('[4] Debt Report \n[5] Add Customer Profile  \n[6] Modify Customer Profile \n[7] Savings Calculator')
        print('[8] Debt payoff calculator \n[9] Update Admin Password \n[10] Log out')
        
        choice = input('\nEnter your choice: ')

        if choice == '1':
            Customer.show_customer_info(admin_id)

        elif choice == '2':
            Customer.show_expenses_info(admin_id) 

        elif choice == '3':
            Customer.show_savings_info(admin_id)

        elif choice == '4':
            Customer.show_debt_info(admin_id) 

        elif choice == '5':
            add_menu(admin_id) 
            
        elif choice == '6':
            modify_menu(admin_id) 

        elif choice == '7':
            savings_calculator()

        elif choice == '8':
            debt_payoff_calulator()

        elif choice == '9':
            admin.update_password(admin_id)

        elif choice == '10':    
            print('\nLogging out.')
            break

        else:
            print('Invalid choice.')  

# menu to add new information             
def add_menu(admin_id):

    while True:
        print('\n+--------------------+\n|Add information menu|\n+--------------------+')
        print('\n[1] Add New Customer Profile \n[2] Add Expenses Info \n[3] Add Savings Info')
        print('[4] Add Debt Info \n[5] Back to Main Menu')
        
        choice = input('\nEnter your choice: ')

        if choice == '1':
            Customer.add_customer_info(admin_id)

        elif choice == '2':
            Customer.add_expenses_info(admin_id) 

        elif choice == '3':
            Customer.add_savings_info(admin_id)

        elif choice == '4':
            Customer.add_debt_info(admin_id) 

        elif choice == '5':
            break

        else:
            print('Invalid choice.')  

# menu to modify existing information
def modify_menu(admin_id):
    
    while True:
        print('\n+-----------------------+\n|Modify information menu|\n+-----------------------+')
        print('\n[1] Modify Customer \n[2] Modify  Income/Expense Info \n[3] Modify Savings Info \n[4] Modify Debt Info \n[5] Back to Main Menu')

        choice = input('\nEnter your choice: ')  
            
        if choice == '1':
            Customer.modify_customer_info(admin_id)
            
        elif choice == '2':
            Customer.modify_expenses_info(admin_id)
            
        elif choice == '3':
            Customer.modify_savings_info(admin_id)

        elif choice == '4':
            Customer.modify_debt_info(admin_id)
            
        elif choice == '5':
            break 

        else:
            print('Invalid choice.')            

# main menu
def main_menu():

    while True:

        print('\n+---------------------------+\n|Financial Management System|\n+---------------------------+')
        print('\n[1] Login \n[2] Register an Admin \n[3] Exit')

        choice = input('\nEnter your choice: ')  

        if choice == '1':
            admin_id = admin.login()   
            if admin_id:
                admin_menu(admin_id)
        elif choice == '2':
            admin.create_admin()
        
        elif choice == '3':
            print('\nExiting the system.\n')
            export_table_to_csv("customer_info", "customer_info.csv")
            export_table_to_csv("debt", "debt.csv")
            export_table_to_csv("expenses", "expenses.csv")
            export_table_to_csv("savings", "savings.csv")
            cursor.close()
            mydb.close()
            break

        else:
            print('Invalid choice.') 

main_menu()