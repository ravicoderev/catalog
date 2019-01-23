# Full Stack Web Development

## Project: Item Catalog

Create a web application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.

- Vagrant
- Language: Python (Python 3.5.2))
- Database: SQLite 

**Pre-requisites:**

1.	Vagrant is up and running if not vagrant up from the root folder where you have vagrant file and log in using vagrant ssh into vm. See sections **1, 2** below for details on getting VM and to run the VM using Vagrant.
2.	Download ZIP file, Unzip & Copy **catalog** repo into the vagrant folder
3.	SQLite database is up and running.
4. The application uses Google OAuth to sign-in. You will need a Google Account.
5. Generate ClienID to be stored in clien_secrets.json file in the application root folder. See section **3** below for details.

**1. Clone the remote to your local machine:**

From the terminal, run the following command (be sure to replace <username> with your GitHub username): git clone http://github.com/<username>/fullstack-nanodegree-vm fullstack. This will give you a directory named fullstack that is a clone of your remote fullstack-nanodegree-vm repository.

**2. Run the virtual machine:**

Using the terminal, change directory using the command ```cd fullstack/vagrant```, then type ```vagrant up``` to launch your virtual machine. 
Once it is up and running, type ```vagrant ssh```. 
Change directory to the /vagrant directory by typing ```cd /vagrant```. This will take you to the shared folder between your virtual machine and host machine.

**3. Generate Client Secrets:**
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


**4. Database Setup:**
1. Execute the python script to generate database
     - Change directory and execute the python script file at the vm prompt ```python3 databasesetup.py``` as below 
     
     ```
     vagrant@vagrant:/vagrant/catalog$python3 databasesetup.py
     ```

	- You should see the following db file created in the current folder
	    - sportscatalogitems.db

**5. Application Start:**  
1. Execute the python script to generate database
     - Change directory and execute the python script file at the vm prompt ```python3 application.py``` as below 
     
     ```
     vagrant@vagrant:/vagrant/catalog$python3 application.py
     ``` 
     - You should see the following message if the application starts successfully
    ''' Running on http://0.0.0.0:8000/ '''

**6. Launch Application In Browser:** 
1. Click on the link above to launch the application in your browser.
2. By default /home page is loaded.
3. Click the '''Login''' button to sign-in to Google.
4. Google sing-in is required for all create, read, update and delete operations. You are allowd to only view without successful sing-in.

**7. Application Features & Navigation:**
1. Login (/login):
      - Launches Google Sign-In to enable authentication.
      - Redirects users to /home if the user has signed-in.
      - Creates a new user in the database for all new user sign-in if the user email id does not exist in the database.
      - The users created in the database is used to validate/constrain inadvertent Edit/Delete of Category/Items created by other users.
2. Home (/home): 
      - Default view lists all Categories and Recent Items added across all categories.
      - When user is signed-in the Categories list will have options to Edit/Delete/View. Recent Items is *View* only in both Signed-In and Sign-Out states. 
2. Sport Categories (/category):
      - When user is signed-in all the categories with Edit/Delete/View options is displayed.
      - Adde new category using the link *Add New Category* below the category listing
      - Validation to ensure Edit/Deletes are enabled for owners/creators of the category. 
      - Error message is displayed on top of the screen when non owners/creators try to Edit/Delete.
      - Duplicate category name check is enabled when creation of new category.
      - Delete operation on a category by the owner will also delete all items under that category.
      - Navigate into View option enables Add/Edit/Delete of items for the category.
3. Items (/items):
      - View only of all items across all categories.
4. JSON:
      - List all categories: [http://localhost:8000/categories/JSON]
      - Details of a particular category: [http://localhost:8000/categorydetails/1/JSON]
      - Recent items added: [http://localhost:8000/recentitems/JSON]
      - List of items in specific category: [http://localhost:8000/category/1/items/JSON]
5. Logout (/gdisconnect):
      - Log out of application. 
      NOTE: This does not sign-out of Google. To sign-out of Google navigate to link in the browser (Ex. On CHROME the far top right will show a picture of the signed-in user.)

