
-- 2. List all customers who are from Canada (`Country = 'Canada'`).
-- SELECT *
-- FROM Customer
-- WHERE Country = 'Canada';

-- SELECT COUNT(TrackID)
-- FROM Track;


-- SELECT FirstName, LastName, Email
-- FROM Employee;

SELECT * FROM Invoice
WHERE Total > 10;

-- # SQL Practice Questions

-- ## Basic Queries
-- 1. Retrieve the names of all albums along with their corresponding artist names.

-- 3. Find the total number of tracks in the database.
-- 4. Display the first name, last name, and email of all employees.
-- 5. Retrieve all invoices where the total amount is greater than $10.

-- ## Join Queries
-- 6. List all album titles along with the names of their artists.
-- 7. Retrieve all invoice details, including the customer’s first and last name, invoice date, and total amount.
-- 8. Find all tracks along with their corresponding genre names.
-- 9. Display all employees along with their manager’s (`ReportsTo`) name.
-- 10. Retrieve all playlists and the total number of tracks in each playlist.

-- ## Aggregation Queries
-- 11. Find the total revenue generated from all invoices.
-- 12. Retrieve the total number of albums for each artist.
-- 13. Find the average invoice total.
-- 14. Count how many customers are assigned to each support representative.
-- 15. Determine the number of tracks for each genre.

-- ## Filtering and Sorting
-- 16. Find all customers whose last name starts with "S".
-- 17. Retrieve the most expensive track in the database.
-- 18. List all invoices from the year 2023.
-- 19. Display the top 5 customers who have spent the most (`Total`).
-- 20. Find the most purchased track based on the `InvoiceLine` table.

-- ## Subqueries and Advanced Queries
-- 21. Find all customers who have not placed any orders (invoices).
-- 22. Retrieve the name of the artist(s) who has/have the most albums.
-- 23. Display all employees who do not have a manager (`ReportsTo IS NULL`).
-- 24. Find the top 3 most common genres in the database based on track count.
-- 25. List the albums that do not contain any tracks.
