# DBMS Assignment 3 - Club Management System Webapp

## Made with Flask and MySQL

### Setup (G1 and G2)

1. Install Python
2. Install MySQL
3. Install the required packages for python: 

    ```bash
    pip install flask
    pip install flask-mysql
    pip install flask-session
    pip install mysql-connector-python
    ```

4. Create the database `CLUB_MS`.
    In order to do login in to MYSQL Workbench using your root user and run the 'studentdb.sql' file in your SQL Workbench. This will create the database and populate it with the required tables and data.

5. Now update the mysql configurations in 'app.py' file.
    If you are using root user like us you can enter your root password for the password key below in the 'app.py' file, however, it should be best to rather use some other user and and passowrd, but for that you need to run the script 'studentdb.sql' with the same user.
    ```py
    mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'DBMS_mysql@0204',    #Enter ur password for root
    'database': 'CLUB_MS'
    }
    ```
6. Login in to MYSQL Workbench using your root user.

   - Click on the 'Administration' tab.
   <img width="1440" alt="Screenshot 2024-04-04 at 4 31 17 PM" src="https://github.com/msrathore-69781/Database-project/assets/103460353/ee5c9d35-38aa-4b1d-aa04-3507ab9d7377">
   
   - Click on the 'Users and Privileges' option.
   - Click on the 'Add Account' button.
   -Enter the following details keeping the rest of the fields as default:

       - Login Name: newuser
       - Password: mannudb
   - Click on the apply button.
      
<img width="1440" alt="Screenshot 2024-04-04 at 4 32 20 PM" src="https://github.com/msrathore-69781/Database-project/assets/103460353/e1d45c6a-da12-41a3-aac6-3584d4a50cd6">

   - Click on 'Administrative Roles' and then click on 'Revoke All Privileges'.
   <img width="1440" alt="Screenshot 2024-04-04 at 4 33 23 PM" src="https://github.com/msrathore-69781/Database-project/assets/103460353/65b4f338-152d-42a9-b252-2655136641cc">

   - Click on 'Schmema Privileges' and then click on 'Revoke All Privileges'.
    
   <img width="1440" alt="Screenshot 2024-04-04 at 4 33 43 PM" src="https://github.com/msrathore-69781/Database-project/assets/103460353/183a31ce-71ba-408c-bd31-20c00185a12c">

   - Go to your home tab in Workbench and then add a new connection by clicking 
     here:
     <img width="1440" alt="Screenshot 2024-04-04 at 4 34 03 PM" src="https://github.com/msrathore-69781/Database-project/assets/103460353/f1cd9d7f-43d0-4263-846b-e3b27146defb">
     
   -  Here Enter the following:
            - Connection Name: student
            - Username: student

   - Click on 'Test Connection' and then enter the password mannudb when 
     prompted. Then click on 'OK'.


7. Repeat the entire above point for a new user 'employee' in your MYSQL 
     Workbench with the following details:
      - Login Name: employee
      - Connection Name: employee
      - Username: employee
      - Password: mannudb


8. Grant Permissions to the 'student' role.
     In order to do this, run the 'student_role_permissions' file in the 'Dump 
     Files' directory in your SQL Workbench. This will grant the required 
     permissions to the 'student' role.


9. Grant Permissions to the 'employee' role.
    In order to do this, run the 'employee_role_permissions' file in the 'Dump 
    Files' directory in your SQL Workbench. This will grant the required 
    permissions to the 'employee' role.



### Running the Webapp

After setting up the database and configuration, we can run our webapp. To do that:
1. Open your terminal window in the folder 'Database-Project/' and run the following:
    ```bash
    python app.py
    ```
2. Open your browser and go to the URL that is displayed in the terminal, like this:
    ```bash
    http://127.0.0.1:5000
    ```

Now your home page is opened which is a login page for our Club Management System where you can login as a student, employee or admin (person with all permissions).

### Operations on ADMIN view
 Admin can perform INSERT, DELETE and RENAME queries on the tables of the database.
 BEFORE : </br>
 ![image](https://github.com/msrathore-69781/Database-project/assets/102381105/f9cd98f7-48ce-4889-b64d-24a143fcd1b7) </br>
 ![image](https://github.com/msrathore-69781/Database-project/assets/102381105/6e0391af-5ff9-477f-955a-b787fe864437) </br>

1. Performing INSERT </br>
    We INSERT a club "Club_dummy" to our clubs table. Fill in all the fields and press INSERT button. Changes will reflect both on the webapp and database. </br>
   ![image](https://github.com/msrathore-69781/Database-project/assets/102381105/e84ec765-ff34-4b2a-8f4c-7737fffa94c4) </br>
   ![image](https://github.com/msrathore-69781/Database-project/assets/102381105/8dfbb7a9-21bf-4b52-8200-3646299043b3) </br>
2. Performing  DELETE </br>
    We DELETE the club "Club_dummy" which we earlier added. Just fill in the corresponding fields and press DELETE. </br>
    ![image](https://github.com/msrathore-69781/Database-project/assets/102381105/e496a804-7a74-44b0-94cb-3e176b3a6c7a) </br>
    ![image](https://github.com/msrathore-69781/Database-project/assets/102381105/7425238f-1b80-4d57-ac3f-998d83729a59) </br>
3. Performing RENAME </br>
    Admin can rename a table and it will reflect over the database and the webapp. </br>
    On pressing the RENAME button the following fields appears asking fora new name. Fill in the field and press enter.</br>
    ![image](https://github.com/msrathore-69781/Database-project/assets/102381105/ff82ea9c-a551-4784-9573-d541b7ea030d) </br>

   Renaming clubs to clubs_of_iitgn.</br>
   ![image](https://github.com/msrathore-69781/Database-project/assets/102381105/e7c00069-bf10-4bf8-baad-de0f8c2eb5ee)</br>
    Also reflected on the sql where now club_ms.clubs table doesn’t exist, instead club_ms.clubs_of_iitgn exists. Same can be tried out for other tables from the admin Page whose access only lies with admin (if you login as admin).</br>
   ![image](https://github.com/msrathore-69781/Database-project/assets/102381105/f765f449-dbdc-457e-9546-f766a90ed031) </br>
   Also the main admin page has now changed </br>
   ![image](https://github.com/msrathore-69781/Database-project/assets/102381105/2c05286d-8ab7-49c8-a8e5-e425ed326222)



   




   
