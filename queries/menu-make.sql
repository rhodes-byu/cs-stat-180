--DROP TABLE IF EXISTS categories; --Use this before re-running the CREATE TABLE statements

-- categories table
CREATE TABLE categories (
  category_id INT PRIMARY KEY,
  category_name TEXT
);

INSERT INTO categories VALUES
  (1, 'milk'),
  (2, 'soda'),
  (3, 'juice');

--SELECT * FROM categories; --Use this statement to test if INSERT INTO worked

--DROP TABLE IF EXISTS menu; --Use this before re-running the CREATE TABLE statements

-- menu Table
CREATE TABLE menu (    
  menu_id INT PRIMARY KEY,
  menu_name TEXT,
  category_id INT,
  unit_price REAL,
  FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

INSERT INTO menu VALUES
  (1, 'Plain Milk', '1', 50),
  (2, 'Chocolate Milk', '1', 50),
  (3, 'Strawberry Milk', '1', 50),
  (4, 'Pepsi', '2',55),
  (5, 'Dr Pepper', '2',55),
  (6, 'Sprite', '2',55),
  (7, 'Root Beer', '2',55),
  (8, 'Passion Fruit', '3',60),
  (9, 'Mango Juice', '3',60),
  (10,'Orange Juice', '3',60);

--SELECT * FROM  menu; --Use this statement to test if INSERT INTO worked

--DROP TABLE IF EXISTS customers; --Use this before re-running the CREATE TABLE statements

-- customers Table
CREATE TABLE customers ( 
  customer_id INT PRIMARY KEY, 
  firstname TEXT, 
  lastname TEXT, 
  city TEXT
);

INSERT INTO customers VALUES
(1, 'Mark', 'Lee', 'Bangkok'),
(2, 'Johnny', 'Suh', 'Phuket'),
(3, 'Jennie', 'Kim', 'Chiang Mai'),
(4, 'Jeno', 'Lee', 'Bangkok'),
(5, 'Karina', 'Yoo', 'Chiang Mai');

--SELECT * FROM  customers; --Use this statement to test if INSERT INTO worked

--DROP TABLE IF EXISTS employee; --Use this before re-running the CREATE TABLE statements

-- employee Table
CREATE TABLE employee ( 
  emp_id INT PRIMARY KEY,   
  firstname TEXT,   
  lastname TEXT,   
  hiredate TEXT,   
  branch TEXT 
);

INSERT INTO employee VALUES
(1, 'Nicolene', 'Jones', '2020-09-01', 'Bangkok'),
(2, 'Anna', 'Smith', '2021-12-01', 'Phuket'),
(3, 'Jessica', 'Brown', '2020-08-01', 'Chiang Mai');

--SELECT * FROM employee;--Use this statement to test if INSERT INTO worked

 

--DROP TABLE IF EXISTS orders; --Use this before re-running the CREATE TABLE statements-- orders Table

CREATE TABLE orders(
  orderid INT,
  orderdate TEXT,
  menu_id INT,
  quantity INT DEFAULT 0,
  customer_id INT,
  delivery_platform TEXT,
  emp_id INT,
  FOREIGN KEY (menu_id) REFERENCES menu(menu_id),
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
  FOREIGN KEY (emp_id) REFERENCES employee(emp_id)
);

INSERT INTO orders VALUES
(1, '2022-08-01', 1, 1, 4, 'Grabfood', 1),
(2, '2022-08-01', 6, 2, 1, 'Lineman', 1),
(3, '2022-08-02', 2, 2, 2, 'Robinhood', 2),
(4, '2022-08-03', 3, 1, 5, 'Grabfood', 3),
(5, '2022-08-04', 1, 1, 2, 'Robinhood', 2),
(6, '2022-08-05', 6, 1, 4, 'Grabfood', 1),
(7, '2022-08-05', 10, 1, 3, 'Grabfood', 3),
(8, '2022-08-09', 3, 2, 4, 'Grabfood', 1),
(9, '2022-08-13', 5, 3, 1, 'Lineman', 1),
(10, '2022-08-13', 6, 1, 2, 'Robinhood', 2),
(11, '2022-08-13', 7, 1, 5, 'Lineman', 3),
(12, '2022-08-14', 4, 1, 5, 'Grabfood', 3),
(13, '2022-08-15', 5, 2, 3, 'Grabfood', 3),
(14, '2022-08-15', 10, 1, 2, 'Robinhood', 2),
(15, '2022-08-18', 5, 2, 1, 'Lineman', 1),
(16, '2022-08-20', 6, 1, 2, 'Robinhood', 2),
(17, '2022-08-21', 4, 2, 1, 'Lineman', 1),
(18, '2022-08-25', 5, 1, 5, 'Grabfood', 3),
(19, '2022-08-26', 5, 3, 3, 'Grabfood', 3),
(20, '2022-08-29', 6, 2, 4, 'Grabfood', 1),
(21, '2021-08-29', 6, 2, 4, 'Grabfood', 1),
(22, '2021-08-29', 3, 1, 4, 'Grabfood', 1),
(23, '2022-09-01', 6, 1, 2, 'Robinhood', 2);