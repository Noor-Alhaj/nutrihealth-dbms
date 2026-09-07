DROP DATABASE IF EXISTS nutri_health_db;
CREATE DATABASE nutri_health_db;
USE nutri_health_db;
-- ============================================
-- CREATE TABLES 
-- ============================================
CREATE TABLE Branches(
    Branch_ID INT AUTO_INCREMENT,
    Branch_Name VARCHAR(100) NOT NULL,
    City VARCHAR(100) NOT NULL,
    Address VARCHAR(200),
    Manager_ID INT,
    Phone VARCHAR(20) NOT NULL UNIQUE,
    PRIMARY KEY (Branch_ID)
);

CREATE TABLE Employees(
    Employee_ID INT AUTO_INCREMENT,
    Employee_Name VARCHAR(100) NOT NULL,
    Position VARCHAR(50) NOT NULL,
    Branch_ID INT NOT NULL,
    Salary NUMERIC(10, 2) NOT NULL,
    Hire_Date DATE DEFAULT (CURRENT_DATE) NOT NULL,
    Phone VARCHAR(20) NOT NULL UNIQUE,
    Address VARCHAR(200),
    PRIMARY KEY (Employee_ID),
    FOREIGN KEY (Branch_ID) REFERENCES Branches(Branch_ID)
        ON UPDATE CASCADE
);

-- Add foreign key constraint to link Manager_ID in Branches table to Employee_ID in Employees table
-- If a manager is deleted, set Manager_ID to NULL; if Employee_ID is updated, cascade the change
ALTER TABLE Branches
ADD CONSTRAINT fk_manager
FOREIGN KEY (Manager_ID) REFERENCES Employees(Employee_ID)
    ON DELETE SET NULL
    ON UPDATE CASCADE;
    
CREATE TABLE Customers(
	Customer_ID INT AUTO_INCREMENT, 
	Customer_FirstName VARCHAR(100) NOT NULL,
	Customer_LastName VARCHAR(100) NOT NULL, # to but the composite attributes need to but more than attributes for represent it  
	Phone VARCHAR(20) NOT NULL UNIQUE,
	Address VARCHAR(200), 
	Join_Date DATE DEFAULT (CURRENT_DATE),
	PRIMARY KEY (Customer_ID)
-- Health_Notes TEXT // To track the health of the customer for الاستشارة
 );

CREATE TABLE Suppliers (
	Supplier_ID INT AUTO_INCREMENT, 
	Supplier_Name VARCHAR(100) NOT NULL, 
	Phone VARCHAR(20) NOT NULL UNIQUE, 
	Address VARCHAR(200), 
	Payment_Terms VARCHAR(255), 
	Delivery_Time_Days INT,
	PRIMARY KEY (Supplier_ID)
);

CREATE TABLE Health_Products(
    Product_ID INT AUTO_INCREMENT,
    Product_Name VARCHAR(100) NOT NULL,
    Category VARCHAR(50) NOT NULL,
    Price NUMERIC(10, 2) NOT NULL,
    Cost_Price NUMERIC(10, 2) NOT NULL,
    Expiry_Date DATE,
    Supplier_ID INT NOT NULL,
    Description TEXT,
    PRIMARY KEY (Product_ID),
    FOREIGN KEY (Supplier_ID) REFERENCES Suppliers(Supplier_ID)
        ON UPDATE CASCADE
);

-- Ensure positive values
ALTER TABLE Health_Products 
ADD CONSTRAINT chk_price CHECK (Price > 0),
ADD CONSTRAINT chk_cost_price CHECK (Cost_Price > 0);

CREATE TABLE Inventory(
    Inventory_ID INT AUTO_INCREMENT,
    Branch_ID INT NOT NULL,
    Product_ID INT NOT NULL,
    Quantity INT NOT NULL DEFAULT 0,
    Entry_Date DATE DEFAULT (CURRENT_DATE) NOT NULL,
    PRIMARY KEY (Inventory_ID),
    FOREIGN KEY (Branch_ID) REFERENCES Branches(Branch_ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (Product_ID) REFERENCES Health_Products(Product_ID)
        ON UPDATE CASCADE
);

CREATE TABLE Sales(
	Sale_ID INT AUTO_INCREMENT, 
	Sale_Date DATE NOT NULL DEFAULT (CURRENT_DATE),
	Customer_ID INT NOT NULL, 
	Employee_ID INT NOT NULL, 
	Branch_ID INT NOT NULL, 
	Total_Price NUMERIC(15, 2) NOT NULL,
	PRIMARY KEY (Sale_ID),
	FOREIGN KEY (Customer_ID) REFERENCES Customers(Customer_ID)
    ON UPDATE CASCADE,
	FOREIGN KEY (Employee_ID) REFERENCES Employees(Employee_ID)
    ON UPDATE CASCADE,
	FOREIGN KEY (Branch_ID) REFERENCES Branches(Branch_ID)
    ON UPDATE CASCADE
);

CREATE TABLE Sale_Details(
    Sale_Detail_ID INT AUTO_INCREMENT,
    Sale_ID INT NOT NULL,
    Product_ID INT NOT NULL,
    Quantity INT NOT NULL,
    Unit_Price NUMERIC(10, 2) NOT NULL,
    Subtotal NUMERIC(10, 2) NOT NULL,
    PRIMARY KEY (Sale_Detail_ID),
    FOREIGN KEY (Sale_ID) REFERENCES Sales(Sale_ID)
        ON UPDATE CASCADE,
    FOREIGN KEY (Product_ID) REFERENCES Health_Products(Product_ID)
        ON UPDATE CASCADE
);

CREATE TABLE Purchases(
	Purchase_ID INT AUTO_INCREMENT, 
	Purchase_Date DATE NOT NULL DEFAULT (CURRENT_DATE), 
	Supplier_ID INT NOT NULL, 
	Branch_ID INT NOT NULL, 
	Total_Cost NUMERIC(10, 2) NOT NULL,
	PRIMARY KEY (Purchase_ID),
	FOREIGN KEY (Supplier_ID) REFERENCES Suppliers(Supplier_ID)
    ON UPDATE CASCADE,
	FOREIGN KEY (Branch_ID) REFERENCES Branches(Branch_ID)
    ON UPDATE CASCADE
);

CREATE TABLE Purchase_Details(
    Purchase_Detail_ID INT AUTO_INCREMENT,
    Purchase_ID INT NOT NULL,
    Product_ID INT NOT NULL,
    Quantity INT NOT NULL,
    Unit_Cost NUMERIC(10, 2) NOT NULL,
    Subtotal NUMERIC(10, 2) NOT NULL,
    PRIMARY KEY (Purchase_Detail_ID),
    FOREIGN KEY (Purchase_ID) REFERENCES Purchases(Purchase_ID)
        ON UPDATE CASCADE,
    FOREIGN KEY (Product_ID) REFERENCES Health_Products(Product_ID)
        ON UPDATE CASCADE
);

CREATE TABLE UserAccount(
	User_ID INT AUTO_INCREMENT, 
	User_Name VARCHAR(100) NOT NULL UNIQUE, 
	Employee_ID INT NOT NULL UNIQUE,
	User_Password VARCHAR(200) NOT NULL, 
	Role VARCHAR(100) NOT NULL,
	PRIMARY KEY (User_ID),
	FOREIGN KEY (Employee_ID) REFERENCES Employees(Employee_ID)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- ============================================
-- SAMPLE DATA INSERTION
-- ============================================
-- Insert sample branches
INSERT INTO Branches (Branch_Name, City, Address, Phone) VALUES
('Nablus Main Branch', 'Nablus', 'Faisal Street, Opposite Municipality', '092345678'),
('Ramallah Branch', 'Ramallah', 'Al-Irsal Street, Next to Irsal Complex', '022987654'),
('Hebron Branch', 'Hebron', 'Ein Sara Street, Next to Hebron University', '022567890'),
('Jenin Branch', 'Jenin', 'Haifa Street, Opposite Government Hospital', '042234567'),
('Tulkarm Branch', 'Tulkarm', 'Al-Nabulsi Street, Next to Municipality', '092876543');

-- Insert sample Employees
INSERT INTO Employees (Employee_Name, Position, Branch_ID, Salary, Phone, Address) VALUES
-- Nablus Branch
('Ahmad Mahmoud', 'Branch_Manager', 1, 4500.00, '0599123456', 'Nablus, Rafidia'),
('Fatima Abdullah', 'Nutrition_Specialist', 1, 3500.00, '0597234567', 'Nablus, Old City'),
('Mohammed Khaled', 'Cashier', 1, 2200.00, '0598345678', 'Nablus, East District'),
('Sara Ahmed', 'Warehouse_Keeper', 1, 2500.00, '0599456789', 'Nablus, Al-Makhfiya'),

-- Ramallah Branch
('Khaled Youssef', 'Branch_Manager', 2, 4500.00, '0597567890', 'Ramallah, Al-Bireh'),
('Noor Hassan', 'Nutrition_Specialist', 2, 3500.00, '0598678901', 'Ramallah, Al-Masyoun'),
('Ali Saeed', 'Cashier', 2, 2200.00, '0599789012', 'Ramallah, Al-Tireh'),

-- Hebron Branch
('Mariam Issa', 'Branch_Manager', 3, 4500.00, '0597890123', 'Hebron, Ein Sara'),
('Youssef Ibrahim', 'Nutrition_Specialist', 3, 3500.00, '0598901234', 'Hebron, Old City'),
('Huda Mahmoud', 'Cashier', 3, 2200.00, '0599012345', 'Hebron, Al-Reihiya'),

-- Jenin Branch
('Omar Fares', 'Branch_Manager', 4, 4500.00, '0597123456', 'Jenin, City Center'),
('Layla Kamal', 'Nutrition_Specialist', 4, 3500.00, '0598234567', 'Jenin, Al-Zahraa'),

-- Tulkarm Branch
('Tariq Salem', 'Branch_Manager', 5, 4500.00, '0599345678', 'Tulkarm, City Center'),
('Rana Khalil', 'Cashier', 5, 2200.00, '0597456789', 'Tulkarm, Eastern District');

-- Update Manager_ID in Branches
UPDATE Branches SET Manager_ID = 1 WHERE Branch_ID = 1;  -- Ahmad Mahmoud
UPDATE Branches SET Manager_ID = 5 WHERE Branch_ID = 2;  -- Khaled Youssef
UPDATE Branches SET Manager_ID = 8 WHERE Branch_ID = 3;  -- Mariam Issa
UPDATE Branches SET Manager_ID = 11 WHERE Branch_ID = 4; -- Omar Fares
UPDATE Branches SET Manager_ID = 13 WHERE Branch_ID = 5; -- Tariq Salem

-- Customers
INSERT INTO Customers (Customer_FirstName, Customer_LastName, Phone, Address) VALUES
('Amer', 'Saleh', '0599111222', 'Nablus, Rafidia Street'),
('Lina', 'Mohammad', '0597222333', 'Ramallah, Downtown'),
('Hassan', 'Ali', '0598333444', 'Hebron, Old City'),
('Reem', 'Khalil', '0599444555', 'Jenin, Central Market'),
('Sami', 'Nasser', '0597555666', 'Tulkarm, Main Street'),
('Dina', 'Yousef', '0598666777', 'Nablus, Askar Camp'),
('Tariq', 'Ahmad', '0599777888', 'Ramallah, Al-Bireh'),
('Hala', 'Salem', '0597888999', 'Hebron, City Center'),
('Karim', 'Ibrahim', '0598999000', 'Jenin, Haifa Street'),
('Nadia', 'Mansour', '0599000111', 'Tulkarm, Industrial Zone'),
('Fadi', 'Hasan', '0597111222', 'Nablus, Balata'),
('Maya', 'Khader', '0598222333', 'Ramallah, Ein Misbah'),
('Bashar', 'Omar', '0599333444', 'Hebron, Wadi Al-Tuffah'),
('Suha', 'Zeid', '0597444555', 'Jenin, Al-Yamoun'),
('Walid', 'Fares', '0598555666', 'Tulkarm, Nur Shams Camp');

-- Suppliers
INSERT INTO Suppliers (Supplier_Name, Phone, Address, Payment_Terms, Delivery_Time_Days) VALUES
('Global Health Supplies', '022334455', 'Ramallah, Industrial Area', 'Net 30', 7),
('Nutrition Plus Co.', '092445566', 'Nablus, Industrial Zone', 'Net 45', 10),
('Premium Supplements Ltd.', '042556677', 'Jenin, Main Street', 'Cash on Delivery', 5),
('Healthy Life Distributors', '022667788', 'Hebron, Commercial District', 'Net 30', 14),
('VitaMax International', '092778899', 'Tulkarm, Industrial Park', 'Net 60', 21),
('ProFit Nutrition', '022889900', 'Ramallah, Downtown', 'Net 30', 7),
('Natural Health Store', '092990011', 'Nablus, City Center', 'Cash on Delivery', 3);

-- Health_Products
INSERT INTO Health_Products (Product_Name, Category, Price, Cost_Price, Expiry_Date, Supplier_ID, Description) VALUES
-- Protein Supplements
('Whey Protein Gold', 'Protein', 180.00, 120.00, '2026-12-31', 1, '100% pure whey protein isolate, 2kg'),
('Casein Protein Night', 'Protein', 150.00, 100.00, '2026-10-15', 1, 'Slow-release protein for overnight recovery'),
('Plant Protein Blend', 'Protein', 140.00, 95.00, '2026-11-20', 2, 'Vegan protein powder, pea and rice blend'),
('Mass Gainer Pro', 'Protein', 220.00, 150.00, '2026-09-30', 2, 'High calorie mass gainer with protein'),

-- Vitamins
('Vitamin C 1000mg', 'Vitamins', 45.00, 28.00, '2027-03-15', 3, 'Immune support, 100 tablets'),
('Vitamin D3 5000IU', 'Vitamins', 55.00, 35.00, '2027-02-28', 3, 'Bone health support, 120 capsules'),
('Multivitamin Daily', 'Vitamins', 70.00, 45.00, '2027-01-31', 4, 'Complete daily vitamin complex'),
('B-Complex Plus', 'Vitamins', 50.00, 32.00, '2026-12-15', 4, 'Energy and metabolism support'),

-- Minerals
('Calcium Magnesium Zinc', 'Minerals', 60.00, 38.00, '2027-04-20', 5, 'Bone and muscle support'),
('Iron Complex', 'Minerals', 40.00, 25.00, '2027-05-10', 5, 'Supports healthy blood cells'),

-- Omega & Fish Oil
('Omega-3 Fish Oil', 'Omega', 85.00, 55.00, '2026-08-30', 6, 'Heart and brain health, 180 softgels'),
('Flaxseed Oil 1000mg', 'Omega', 65.00, 42.00, '2026-07-25', 6, 'Plant-based omega-3'),

-- Pre-Workout
('Energy Blast Pre-Workout', 'Pre-Workout', 120.00, 80.00, '2026-11-30', 7, 'Maximum energy and focus'),
('Pump Enhancer', 'Pre-Workout', 110.00, 75.00, '2026-10-20', 7, 'Nitric oxide booster'),

-- Amino Acids
('BCAA 2:1:1', 'Amino Acids', 95.00, 62.00, '2027-01-15', 1, 'Muscle recovery blend'),
('L-Glutamine Powder', 'Amino Acids', 80.00, 52.00, '2026-12-20', 2, 'Muscle recovery and immune support'),

-- Weight Management
('Fat Burner Extreme', 'Weight Loss', 130.00, 85.00, '2026-09-15', 3, 'Thermogenic fat burner'),
('Appetite Control', 'Weight Loss', 90.00, 58.00, '2026-08-10', 4, 'Natural appetite suppressant'),

-- Probiotics
('Probiotic 10 Billion', 'Digestive', 75.00, 48.00, '2026-06-30', 5, 'Digestive health support'),
('Digestive Enzyme Complex', 'Digestive', 70.00, 45.00, '2026-07-15', 6, 'Supports nutrient absorption');

-- Inventory 
INSERT INTO Inventory (Branch_ID, Product_ID, Quantity, Entry_Date) VALUES
-- Nablus Branch
(1, 1, 50, '2025-01-10'),
(1, 2, 30, '2025-01-10'),
(1, 3, 25, '2025-01-10'),
(1, 5, 100, '2025-01-12'),
(1, 6, 80, '2025-01-12'),
(1, 7, 60, '2025-01-12'),
(1, 11, 45, '2025-01-14'),
(1, 13, 35, '2025-01-14'),
(1, 15, 40, '2025-01-15'),

-- Ramallah Branch
(2, 1, 45, '2025-01-11'),
(2, 4, 20, '2025-01-11'),
(2, 5, 90, '2025-01-13'),
(2, 8, 55, '2025-01-13'),
(2, 9, 70, '2025-01-13'),
(2, 11, 50, '2025-01-15'),
(2, 17, 30, '2025-01-15'),

-- Hebron Branch
(3, 1, 40, '2025-01-12'),
(3, 3, 35, '2025-01-12'),
(3, 6, 75, '2025-01-14'),
(3, 10, 65, '2025-01-14'),
(3, 12, 40, '2025-01-16'),
(3, 16, 45, '2025-01-16'),

-- Jenin Branch
(4, 2, 28, '2025-01-13'),
(4, 5, 85, '2025-01-13'),
(4, 7, 50, '2025-01-15'),
(4, 13, 30, '2025-01-15'),
(4, 19, 38, '2025-01-16'),

-- Tulkarm Branch
(5, 1, 35, '2025-01-14'),
(5, 4, 18, '2025-01-14'),
(5, 8, 48, '2025-01-16'),
(5, 14, 25, '2025-01-16'),
(5, 20, 42, '2025-01-17');

-- Purchases 
INSERT INTO Purchases (Purchase_Date, Supplier_ID, Branch_ID, Total_Cost) VALUES
('2025-01-10', 1, 1, 6000.00),
('2025-01-10', 2, 1, 4750.00),
('2025-01-11', 1, 2, 5400.00),
('2025-01-11', 3, 2, 3500.00),
('2025-01-12', 4, 3, 4200.00),
('2025-01-12', 5, 3, 3800.00),
('2025-01-13', 6, 4, 3300.00),
('2025-01-14', 7, 5, 2900.00),
('2025-01-15', 1, 1, 5500.00),
('2025-01-16', 2, 2, 4100.00);

-- Purchases_Details 
INSERT INTO Purchase_Details (Purchase_ID, Product_ID, Quantity, Unit_Cost, Subtotal) VALUES
-- Purchase 1 (Nablus from Global Health)
(1, 1, 50, 120.00, 6000.00),

-- Purchase 2 (Nablus from Nutrition Plus)
(2, 2, 30, 100.00, 3000.00),
(2, 3, 25, 95.00, 2375.00),

-- Purchase 3 (Ramallah from Global Health)
(3, 1, 45, 120.00, 5400.00),

-- Purchase 4 (Ramallah from Premium Supplements)
(4, 5, 100, 28.00, 2800.00),
(4, 6, 20, 35.00, 700.00),

-- Purchase 5 (Hebron from Healthy Life)
(5, 7, 60, 45.00, 2700.00),
(5, 8, 50, 32.00, 1600.00),

-- Purchase 6 (Hebron from VitaMax)
(6, 9, 70, 38.00, 2660.00),
(6, 10, 30, 25.00, 750.00),

-- Purchase 7 (Jenin from ProFit)
(7, 11, 50, 55.00, 2750.00),
(7, 12, 15, 42.00, 630.00),

-- Purchase 8 (Tulkarm from Natural Health)
(8, 13, 30, 80.00, 2400.00),
(8, 14, 10, 75.00, 750.00),

-- Purchase 9 (Nablus from Global Health)
(9, 15, 40, 62.00, 2480.00),
(9, 16, 30, 52.00, 1560.00),

-- Purchase 10 (Ramallah from Nutrition Plus)
(10, 17, 35, 85.00, 2975.00),
(10, 18, 20, 58.00, 1160.00);

-- Sales
INSERT INTO Sales (Sale_Date, Customer_ID, Employee_ID, Branch_ID, Total_Price) VALUES
('2025-01-15', 1, 3, 1, 360.00),
('2025-01-15', 2, 7, 2, 495.00),
('2025-01-16', 3, 10, 3, 275.00),
('2025-01-16', 4, 12, 4, 550.00),
('2025-01-16', 5, 14, 5, 420.00),
('2025-01-17', 6, 3, 1, 625.00),
('2025-01-17', 7, 7, 2, 315.00),
('2025-01-17', 8, 10, 3, 540.00),
('2025-01-18', 9, 12, 4, 390.00),
('2025-01-18', 10, 14, 5, 455.00),
('2025-01-18', 11, 3, 1, 730.00),
('2025-01-18', 12, 7, 2, 295.00),
('2025-01-18', 13, 10, 3, 610.00),
('2025-01-18', 14, 12, 4, 380.00),
('2025-01-18', 15, 14, 5, 520.00);

-- Sales_Details 
INSERT INTO Sale_Details (Sale_ID, Product_ID, Quantity, Unit_Price, Subtotal) VALUES
-- Sale 1 (Customer 1, Nablus)
(1, 1, 2, 180.00, 360.00),

-- Sale 2 (Customer 2, Ramallah)
(2, 5, 3, 45.00, 135.00),
(2, 1, 2, 180.00, 360.00),

-- Sale 3 (Customer 3, Hebron)
(3, 6, 5, 55.00, 275.00),

-- Sale 4 (Customer 4, Jenin)
(4, 7, 5, 70.00, 350.00),
(4, 13, 1, 120.00, 120.00),
(4, 11, 1, 85.00, 85.00),

-- Sale 5 (Customer 5, Tulkarm)
(5, 2, 2, 150.00, 300.00),
(5, 13, 1, 120.00, 120.00),

-- Sale 6 (Customer 6, Nablus)
(6, 1, 3, 180.00, 540.00),
(6, 11, 1, 85.00, 85.00),

-- Sale 7 (Customer 7, Ramallah)
(7, 5, 7, 45.00, 315.00),

-- Sale 8 (Customer 8, Hebron)
(8, 1, 3, 180.00, 540.00),

-- Sale 9 (Customer 9, Jenin)
(9, 15, 3, 95.00, 285.00),
(9, 5, 2, 45.00, 90.00),

-- Sale 10 (Customer 10, Tulkarm)
(10, 7, 5, 70.00, 350.00),
(10, 19, 1, 75.00, 75.00),

-- Sale 11 (Customer 11, Nablus)
(11, 4, 2, 220.00, 440.00),
(11, 17, 2, 130.00, 260.00),

-- Sale 12 (Customer 12, Ramallah)
(12, 8, 5, 50.00, 250.00),
(12, 5, 1, 45.00, 45.00),

-- Sale 13 (Customer 13, Hebron)
(13, 1, 2, 180.00, 360.00),
(13, 9, 3, 60.00, 180.00),
(13, 7, 1, 70.00, 70.00),

-- Sale 14 (Customer 14, Jenin)
(14, 6, 4, 55.00, 220.00),
(14, 16, 2, 80.00, 160.00),

-- Sale 15 (Customer 15, Tulkarm)
(15, 1, 2, 180.00, 360.00),
(15, 11, 1, 85.00, 85.00),
(15, 19, 1, 75.00, 75.00);

-- UserAccount 
-- f92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f = password123
INSERT INTO UserAccount (User_Name, Employee_ID, User_Password, Role) VALUES
('ahmad_m', 1, 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'Branch_Manager'),
('fatima_a', 2, 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'Nutrition_Specialist'),
('mohammed_k', 3, 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'Cashier'),
('sara_a', 4, 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'Warehouse_Keeper'),
('khaled_y', 5, 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'Branch_Manager'),
('noor_h', 6, 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'Nutrition_Specialist'),
('ali_s', 7, 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'Cashier'),
('mariam_i', 8, 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'Branch_Manager'),
('youssef_i', 9, 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'Nutrition_Specialist'),
('huda_m', 10, 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'Cashier'),
('omar_f', 11, 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'Branch_Manager'),
('layla_k', 12, 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'Nutrition_Specialist'),
('tariq_s', 13, 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'Branch_Manager'),
('rana_k', 14, 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'Cashier');

-- ============================================
-- Queries
-- ============================================

-- ============================================
-- Branches & Employees
-- ============================================

-- 1. Retrieve details of all branches located in a specific city
SELECT Branch_ID, Branch_Name, City, Address, Phone
FROM Branches
WHERE City = 'Nablus';

-- 2. Retrieve the names, positions, and salaries of staff members at a specific branch, sorted by staff name
SELECT Employee_Name, Position, Salary
FROM Employees
WHERE Branch_ID = 1
ORDER BY Employee_Name;

-- 3. Retrieve the name of the manager for each branch, sorted by branch number
SELECT 
    b.Branch_ID,
    b.Branch_Name,
    e.Employee_Name AS Manager_Name
FROM Branches b
LEFT JOIN Employees e ON b.Manager_ID = e.Employee_ID                
ORDER BY b.Branch_ID;

-- 4. Retrieve the total number of employees working in each branch
SELECT 
    b.Branch_Name,
    COUNT(e.Employee_ID) AS Total_Employees
FROM Branches b
LEFT JOIN Employees e ON b.Branch_ID = e.Branch_ID
GROUP BY b.Branch_ID, b.Branch_Name
ORDER BY b.Branch_Name;

-- 5. Retrieve the total salary expenses per branch
SELECT 
    b.Branch_Name,
    COALESCE(SUM(e.Salary), 0) AS Total_Salary_Expenses -- Because of left join the sum of salaries may be nulls so the result will be null, and coalesce will but 0 instead of null 
FROM Branches b
LEFT JOIN Employees e ON b.Branch_ID = e.Branch_ID
GROUP BY b.Branch_ID, b.Branch_Name
ORDER BY Total_Salary_Expenses DESC;

-- 6. Retrieve the number of employees hired during the last year
SELECT COUNT(*) AS Employees_Hired_Last_Year
FROM Employees
WHERE Hire_Date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR);

-- ============================================q
-- Inventory
-- ============================================

-- 7. Retrieve all health products available at a specific branch, sorted by category
SELECT 
    hp.Product_Name,
    hp.Category,
    i.Quantity,
    hp.Price
FROM Inventory i
JOIN Health_Products hp ON i.Product_ID = hp.Product_ID
WHERE i.Branch_ID = 1 AND i.Quantity > 0
ORDER BY hp.Category, hp.Product_Name;

-- 8. Retrieve the total number of products in each category at a specific branch, sorted by supplier
SELECT 
    hp.Category,
    s.Supplier_Name,
    COUNT(hp.Product_ID) AS Total_Products, -- Distinct; dont count the same product more than once 
    SUM(i.Quantity) AS Total_Quantity
FROM Inventory i
JOIN Health_Products hp ON i.Product_ID = hp.Product_ID
JOIN Suppliers s ON hp.Supplier_ID = s.Supplier_ID
WHERE i.Branch_ID = 1
GROUP BY hp.Category, s.Supplier_Name -- we used here s.Supplier_Name because we will use it in order by 
ORDER BY s.Supplier_Name, hp.Category;

-- 9. Retrieve all products that are currently below the minimum stock level in any branch
SELECT 
    b.Branch_Name,
    hp.Product_Name,
    hp.Category,
    i.Quantity
FROM Inventory i
JOIN Health_Products hp ON i.Product_ID = hp.Product_ID
JOIN Branches b ON i.Branch_ID = b.Branch_ID
WHERE i.Quantity < 50
ORDER BY i.Quantity ASC, b.Branch_Name;

-- ============================================
-- Sales & Purchases
-- ============================================

-- 10. Retrieve the total sales for each branch in a specific period
SELECT 
    b.Branch_Name,
    COUNT(s.Sale_ID) AS Total_Sales_Count,
    SUM(s.Total_Price) AS Total_Sales_Amount
FROM Sales s
JOIN Branches b ON s.Branch_ID = b.Branch_ID
WHERE s.Sale_Date BETWEEN '2025-01-01' AND '2025-01-31'
GROUP BY b.Branch_ID, b.Branch_Name
ORDER BY Total_Sales_Amount DESC;

-- 11. Retrieve all sales made by a specific branch, sorted by sale date
SELECT 
    s.Sale_ID,
    s.Sale_Date,
    CONCAT(c.Customer_FirstName, ' ', c.Customer_LastName) AS Customer_Name, -- The full name of the customer
    e.Employee_Name,
    s.Total_Price
FROM Sales s
JOIN Customers c ON s.Customer_ID = c.Customer_ID
JOIN Employees e ON s.Employee_ID = e.Employee_ID
WHERE s.Branch_ID = 1
ORDER BY s.Sale_Date DESC;

-- 12. Retrieve total purchases and sales per branch, sorted by branch name
SELECT 
    b.Branch_Name,
    COALESCE(SUM(p.Total_Cost), 0) AS Total_Purchases,
    COALESCE(SUM(s.Total_Price), 0) AS Total_Sales,
    COALESCE(SUM(s.Total_Price), 0) - COALESCE(SUM(p.Total_Cost), 0) AS Net_Profit
FROM Branches b
LEFT JOIN Purchases p ON b.Branch_ID = p.Branch_ID
LEFT JOIN Sales s ON b.Branch_ID = s.Branch_ID
GROUP BY b.Branch_ID, b.Branch_Name
ORDER BY b.Branch_Name;

-- 13. Retrieve sales handled by a specific employee within a selected date range
SELECT 
    s.Sale_ID,
    s.Sale_Date,
    CONCAT(c.Customer_FirstName, ' ', c.Customer_LastName) AS Customer_Name,
    s.Total_Price
FROM Sales s
JOIN Customers c ON s.Customer_ID = c.Customer_ID
WHERE s.Employee_ID = 3
  AND s.Sale_Date BETWEEN '2025-01-01' AND '2025-01-31'
ORDER BY s.Sale_Date DESC;

-- 14. Retrieve all purchases made from each supplier during the last quarter
SELECT 
    sup.Supplier_Name,
    COUNT(p.Purchase_ID) AS Total_Purchases,
    SUM(p.Total_Cost) AS Total_Amount
FROM Purchases p
JOIN Suppliers sup ON p.Supplier_ID = sup.Supplier_ID
WHERE p.Purchase_Date >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
GROUP BY sup.Supplier_ID, sup.Supplier_Name
ORDER BY Total_Amount DESC;

-- ============================================
-- Customers
-- ============================================

-- 15. Retrieve a list of inactive customers (no purchases in the last 6 months)
SELECT 
    c.Customer_ID,
    CONCAT(c.Customer_FirstName, ' ', c.Customer_LastName) AS Customer_Name,
    c.Phone,
    c.Join_Date,
    MAX(s.Sale_Date) AS Last_Purchase_Date,
    DATEDIFF(CURDATE(), MAX(s.Sale_Date)) AS Days_Since_Last_Purchase
FROM Customers c
LEFT JOIN Sales s ON c.Customer_ID = s.Customer_ID
GROUP BY c.Customer_ID
HAVING MAX(s.Sale_Date) < DATE_SUB(CURDATE(), INTERVAL 6 MONTH) 
   OR MAX(s.Sale_Date) IS NULL
ORDER BY Last_Purchase_Date DESC;

-- 16. Retrieve the number of consultations each customer received from nutrition specialists
-- Note: Track customer visits through sales
SELECT 
    CONCAT(c.Customer_FirstName, ' ', c.Customer_LastName) AS Customer_Name,
    COUNT(s.Sale_ID) AS Total_Visits,
    COUNT(DISTINCT DATE(s.Sale_Date)) AS Unique_Visit_Days -- The customer may buy multiple of times in a day (we want just count the days)
FROM Customers c
LEFT JOIN Sales s ON c.Customer_ID = s.Customer_ID
GROUP BY c.Customer_ID
ORDER BY Total_Visits DESC;

-- 17. Retrieve the product categories most frequently purchased by each customer
SELECT 
    c.Customer_ID,
    CONCAT(c.Customer_FirstName, ' ', c.Customer_LastName) AS Customer_Name,
    hp.Category AS Most_Purchased_Category,
    COUNT(sd.Product_ID) AS Purchase_Count,
    SUM(sd.Quantity) AS Total_Quantity
FROM Customers c
JOIN Sales s ON c.Customer_ID = s.Customer_ID
JOIN Sale_Details sd ON s.Sale_ID = sd.Sale_ID
JOIN Health_Products hp ON sd.Product_ID = hp.Product_ID
GROUP BY c.Customer_ID, c.Customer_FirstName, c.Customer_LastName, hp.Category
HAVING COUNT(sd.Product_ID) = (
    SELECT MAX(cat_count)
    FROM (
        SELECT COUNT(sd2.Product_ID) AS cat_count
        FROM Sales s2
        JOIN Sale_Details sd2 ON s2.Sale_ID = sd2.Sale_ID
        JOIN Health_Products hp2 ON sd2.Product_ID = hp2.Product_ID
        WHERE s2.Customer_ID = c.Customer_ID
        GROUP BY hp2.Category
    ) AS category_counts
)
ORDER BY c.Customer_ID;

-- ============================================
-- Reports & Analytics
-- ============================================

-- 18. Retrieve the top 10 best-selling health products across all branches
SELECT 
    hp.Product_ID,
    hp.Product_Name,
    hp.Category,
    SUM(sd.Quantity) AS Total_Quantity_Sold,
    SUM(sd.Subtotal) AS Total_Revenue
FROM Sale_Details sd
JOIN Health_Products hp ON sd.Product_ID = hp.Product_ID
GROUP BY hp.Product_ID, hp.Product_Name, hp.Category
ORDER BY Total_Quantity_Sold DESC
LIMIT 10;

-- 19. Retrieve the most popular health products sold in each branch
SELECT 
    b.Branch_ID,
    b.Branch_Name,
    hp.Product_Name,
    hp.Category,
    SUM(sd.Quantity) AS Total_Sold,
    SUM(sd.Subtotal) AS Total_Revenue
FROM Sales s
JOIN Sale_Details sd ON s.Sale_ID = sd.Sale_ID
JOIN Health_Products hp ON sd.Product_ID = hp.Product_ID
JOIN Branches b ON s.Branch_ID = b.Branch_ID
GROUP BY b.Branch_ID, b.Branch_Name, hp.Product_ID, hp.Product_Name, hp.Category
ORDER BY b.Branch_Name, Total_Sold DESC;

-- 20. Retrieve the profit margin for each product
SELECT 
    hp.Product_ID,
    hp.Product_Name,
    hp.Category,
    hp.Cost_Price,
    hp.Price AS Selling_Price,
    (hp.Price - hp.Cost_Price) AS Profit_Per_Unit,
    ROUND(((hp.Price - hp.Cost_Price) / hp.Price) * 100, 2) AS Profit_Margin_Percentage
FROM Health_Products hp
ORDER BY Profit_Margin_Percentage DESC;

-- 21. Retrieve total revenue and total expenses for each branch
SELECT 
    b.Branch_ID,
    b.Branch_Name,
	 COALESCE(SUM(s.Total_Price), 0) AS Total_Revenue,
	 COALESCE(SUM(p.Total_Cost), 0) AS Total_Expenses,
	 COALESCE(SUM(e.Salary), 0) AS Salary_Expenses,
    (COALESCE(SUM(s.Total_Price), 0) - 
     COALESCE(SUM(p.Total_Cost), 0) - 
     COALESCE(SUM(e.Salary), 0)) AS Net_Profit
FROM Branches b
LEFT JOIN Sales s ON b.Branch_ID = s.Branch_ID
LEFT JOIN Purchases p ON b.Branch_ID = p.Branch_ID
LEFT JOIN Employees e ON b.Branch_ID = e.Branch_ID
GROUP BY b.Branch_ID, b.Branch_Name
ORDER BY Net_Profit DESC;

-- ============================================
-- Reporting
-- ============================================

-- 22. Retrieve all inventory transfers and stock updates per product, sorted by update date
SELECT 
    hp.Product_ID,
    hp.Product_Name,
    hp.Category,
    b.Branch_Name,
    i.Quantity,
    i.Entry_Date AS Update_Date,
    'Stock Entry' AS Transaction_Type
FROM Inventory i
JOIN Health_Products hp ON i.Product_ID = hp.Product_ID
JOIN Branches b ON i.Branch_ID = b.Branch_ID
ORDER BY i.Entry_Date DESC, hp.Product_Name;  
  
#====================
# calculate the age 
# SELECT TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) AS age
# FROM your_table
#========================
/*CREATE TABLE Diet_Plans (
    Plan_ID INT PRIMARY KEY AUTO_INCREMENT,
    Customer_ID INT NOT NULL,
    Specialist_ID INT NOT NULL,
    Plan_Name VARCHAR(100) NOT NULL,
    Created_Date DATE NOT NULL DEFAULT CURRENT_DATE,
    Start_Date DATE NOT NULL,
    End_Date DATE NOT NULL,
    Calories_Per_Day DECIMAL(8,2),
    Notes TEXT,
    Status ENUM('Active', 'Completed', 'Cancelled') DEFAULT 'Active',
    CONSTRAINT FK_DietPlan_Customer 
        FOREIGN KEY (Customer_ID) REFERENCES Customers(Customer_ID),
    CONSTRAINT FK_DietPlan_Specialist 
        FOREIGN KEY (Specialist_ID) REFERENCES Employees(Employee_ID),
    CONSTRAINT CHK_DietPlan_Dates 
        CHECK (End_Date > Start_Date)
);
*/

-- ============================================
-- CREATE INDEXES FOR PERFORMANCE
-- ============================================
CREATE INDEX idx_Employees_Branch ON Employees(Branch_ID);
CREATE INDEX idx_Employees_Position ON Employees(Position);
CREATE INDEX idx_Products_Category ON Health_Products(Category);
CREATE INDEX idx_Products_Supplier ON Health_Products(Supplier_ID);
CREATE INDEX idx_Inventory_Branch ON Inventory(Branch_ID);
CREATE INDEX idx_Inventory_Product ON Inventory(Product_ID);
CREATE INDEX idx_Sales_Date ON Sales(Sale_Date);
CREATE INDEX idx_Sales_Customer ON Sales(Customer_ID);
CREATE INDEX idx_Sales_Employee ON Sales(Employee_ID);
CREATE INDEX idx_Sales_Branch ON Sales(Branch_ID);
CREATE INDEX idx_Purchases_Date ON Purchases(Purchase_Date);
CREATE INDEX idx_Purchases_Supplier ON Purchases(Supplier_ID);
CREATE INDEX idx_Purchases_Branch ON Purchases(Branch_ID);
-- CREATE INDEX idx_Appointments_Date ON Appointments(Appointment_Date);
-- CREATE INDEX idx_Appointments_Customer ON Appointments(Customer_ID);
-- CREATE INDEX idx_Appointments_Specialist ON Appointments(Specialist_ID);