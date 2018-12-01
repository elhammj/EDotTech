# EDotTech Shop

## Objective: 
It is a Catalog Full Stack project that emphsizes python, Flask &  OAuth and third party login. 

## Overview:
This project provides a list of tech items within a variety of tech categories as well as provide a user registration and authentication system. 
Registered users will have the ability to post, edit and delete their own items.

The application uses google login API. 

## To Run the application:
### Download the following software/files
1. [Vagrant](https://www.vagrantup.com/)
2. [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
3. [Udacity Virtual Machine](https://github.com/udacity/fullstack-nanodegree-vm)

### Start your machine
1. Run `vagrant up`
2. Run `vagrant ssh`
3. Access the shared folder `cd/vagrant`
4. Install Requests `sudo pip install requests`

### Setup the database
1. Create the database, run `python database_setup.py`
2. Seed your database, run `python technologyLists.py`

### Start the application
1. Run `python application.py`
2. Access the app through [http://localhost:5000](http://localhost:5000)
* You May change the port to 8000 in applciation.py in main funciton since the app works in 5000 and 8000

## Pages:
1. **Categories**: run in `http://localhost:5000/categories/`
- It shows all the categories and latest 5 items
- Avaliable for both public users and registered users 
2. **Items for a category**: run in `http://localhost:5000/<int:category_id>/items`
- It shows all the items under a selected category
- Avaliable only for registered users
3. **Item's Details**: run in `http://localhost:5000//<int:category_id>/items/<int:item_id>/`
- It shows item's details
- Avaliable only for registered users
4. **Add a new item**: run in `http://localhost:5000/<int:category_id>/items/new/`
- User can add a new item
- Avaliable only for registered users
5. **Edit an item**: run in `http://localhost:5000/<int:category_id>/items/<int:item_id>/edit/`
- User can edit item's info
- Avaliable only for registered users
6. **Delete an item**: run in `http://localhost:5000/<int:category_id>/items/<int:item_id>/delete/`
- User can delete an item
- Avaliable only for registered users
7. **Login Page**: run in `http://localhost:5000/login/`
- User can login by using Google

## JSON Endpoints
### Access JSON pages
`/catalog/JSON`
- It has list of categories and its items.

`categories/JSON`
- It has list of all catgeories. 

`/categories/<int:category_id>/items/JSON`
- It has list of items under a specific catalog.

`/categories/<int:category_id>/items/<int:item_id>/JSON`
- It has item's details.
