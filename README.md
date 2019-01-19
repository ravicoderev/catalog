# Full Stack Web Development

## Project: Item Catalog

Create a web application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.

- Vagrant
- Language: Python (Python 3.5.2))
- Database: SQLite 

**Pre-requisites:**

1.	Vagrant is up and running if not vagrant up from the root folder where you have vagrant file and log in using vagrant ssh into vm.
2.	Download ZIP file, Unzip & Copy **catalog** repo into the vagrant folder
3.	SQLite database is up and running.
4. The application uses Google OAuth to sign-in. You will need a Google Account.

**Database Setup:**
1. Execute the python script to generate database
     - Change directory and execute the python script file at the vm prompt ```python3 databasesetup.py``` as below 
     
     ```
     vagrant@vagrant:/vagrant/catalog$python3 databasesetup.py
     ```

	- You should see the following db file created in the current folder
	    - catalogitems_test.db

**Application Start:**  
1. Execute the python script to generate database
     - Change directory and execute the python script file at the vm prompt ```python3 application.py``` as below 
     
     ```
     vagrant@vagrant:/vagrant/catalog$python3 application.py
     ``` 
     - You should see the following message if the application starts successfully
    ''' Running on http://0.0.0.0:8000/ '''

**Launch Application In Browser:** 
1. Click on the link above to launch the application in your browser.
2. By default /home page is loaded.
3. Click the '''Login''' button to sign-in to Google.
4. Google sing-in is required for all create, read, update and delete operations. You are allowd to only view without successful sing-in.

