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
5. Generate ClienID to be stored in clien_secrets.json file in the application root folder. See section **Generate Client Secrets**

**Generate Client Secrets:**
1. Navigate to [https://console.developers.google.com/apis?project=sportinggoodscatalog-app] and login using your Google account if you have not already loggedin.
2. Create Credentials:
     - Click Credentials on the left side menu and then click on **'Click Credentials'** dropdown button.
     - Select **OAuth client ID** from the dropdown list.
     - On the *Create OAuth client ID* page you will see *Application type* options. Select option **Web Application** and then click on Create button.
     - Enter ```SportingGoodsClient ID``` in the Name text box.
3. OAuth Consent Links: Add the following links
     - Authorized JavaScript origins: 
        - http://localhost:8000
     - Authorized redirect URIs
        - http://localhost:8000/login
        - http://localhost:8000/gconnect
     - Click on **Save**. 
4. OAuth consent screen:
      - Enter 'Sporting Goods Catalog App' under **Application name**.
      - Verify if the email id under **Support email** is the account used to login to Google.
      - Scroll down to the page and click **Save**
5. Download client ID:
      - You should see a new client ID on the Credentials page listed under OAuth 2.0 client IDs.
      - Click the 'Download' icon and save it to the root of the /Catalog application folder.
      - Rename the client ID file to **client_secrets.json**





**Database Setup:**
1. Execute the python script to generate database
     - Change directory and execute the python script file at the vm prompt ```python3 databasesetup.py``` as below 
     
     ```
     vagrant@vagrant:/vagrant/catalog$python3 databasesetup.py
     ```

	- You should see the following db file created in the current folder
	    - sportscatalogitems.db

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

