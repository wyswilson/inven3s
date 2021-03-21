inven3s is a mobile responsive app to track any products with a 13-digit Global Trade Item Number (GTIN) that goes in or out of your pantry or any inventory. It also automatically generates shopping list for your next shopping trip. It's built in the React framework with Python flask back-end. It uses MySQL database for its data.

The front-end code is in /webapp and the API is in /api.

There's minimal configuration required and the main ones are in:
- conf.ini in /api where details about the MySQL instance, etc are stored
- and the respective .js files in /webapp/src for the API host address, e.g., https://inven3s.xyz

The schema for the tables in the MySQL DB is in the file /dbschema.sql