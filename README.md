**Password Manager**
___________

This is a CLI-based password manager that takes the site name and password of the user and saves it in a database. If the user wishes to retrieve it or delete the password, it has added functionality of retrieving the database.

**How it's made**
____________

**Tech used**: Python, PostgreSQL

I opted to create a class to add the different add password and delete password methods and used encryption on the passwords to make the process of saving the passwords safer (pm-functions.py). In the main python file (app.py) I coded SQL commands that creates a separate password manager database. Furthermore in the pm-functions.py file, I coded sql scripts to add, retrieve and delete passwords. For encryption, I used the AES algorithm with the CFB mode.
