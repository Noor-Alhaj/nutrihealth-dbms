# NutriHealth — Multi-Branch Health Store Management System

A database course project: a normalized MySQL database for a chain of health &
nutrition stores, wrapped in a Flask web application with role-based access
control, full CRUD screens, 22 analytical SQL queries, and management reports.

![ER Diagram](er-diagram.png)

---

## Overview

NutriHealth models the day-to-day operations of a health-product retail chain
across five branches: staff and branch management, customer records, product
catalog and suppliers, per-branch inventory, sales with line items, and
purchase orders from suppliers.

The project has two halves:

- **`NutriHealthDatabase.sql`** — the schema (11 tables), referential-integrity
  constraints, `CHECK` constraints, performance indexes, seed data, and the 22
  required analytical queries.
- **`PythonCode.py`** — a Flask application (~2000 lines) that exposes the
  database through a web UI: authentication, four user roles with different
  permissions, CRUD for every major entity, and a page for each analytical
  query and report.

---

## Database Design

### Tables

| Table | Purpose |
| --- | --- |
| `Branches` | Store locations; `Manager_ID` self-references an employee |
| `Employees` | Staff, position, salary, hire date, assigned branch |
| `Customers` | Customer records with join date |
| `Suppliers` | Vendors, payment terms, delivery lead time |
| `Health_Products` | Catalog with category, price, cost price, expiry, supplier |
| `Inventory` | Per-branch stock quantity per product |
| `Sales` | Sale header: date, customer, employee, branch, total |
| `Sale_Details` | Sale line items: product, quantity, unit price, subtotal |
| `Purchases` | Purchase header: date, supplier, branch, total cost |
| `Purchase_Details` | Purchase line items |
| `UserAccount` | Login credentials and role, one per employee |

### Design decisions

- **Header/detail split** for both `Sales` and `Purchases` so a single
  transaction can contain many products, keeping the schema in 3NF.
- **Circular relationship** between `Branches` and `Employees` resolved by
  creating the tables first, then adding the `fk_manager` foreign key with
  `ALTER TABLE`. Deleting a manager sets `Manager_ID` to `NULL` rather than
  cascading the delete.
- **Referential actions** chosen per relationship: `ON UPDATE CASCADE`
  everywhere, `ON DELETE CASCADE` only where a child row is meaningless without
  its parent (inventory rows for a deleted branch, user account for a deleted
  employee).
- **Composite attributes** from the ER diagram (customer name, phone) flattened
  into separate columns; phone numbers are `UNIQUE` across employees,
  customers, suppliers, and branches.
- **`CHECK` constraints** enforce `Price > 0` and `Cost_Price > 0`.
- **13 indexes** on foreign keys and date columns used in `WHERE`/`GROUP BY`
  clauses of the analytical queries.

---

## Analytical Queries (22)

Every query below is in `NutriHealthDatabase.sql` and has a corresponding page
in the web app.

**Branches & employees**

1. Branch details filtered by city
2. Staff names, positions, and salaries at a branch
3. Manager name per branch
4. Employee headcount per branch
5. Total salary expenses per branch
6. Employees hired in the last year

**Products & inventory**

7. Products available at a branch, sorted by category
8. Product count per category at a branch
9. Products below minimum stock level
10. Category summary per branch

**Sales & purchases**

11. Total sales per branch over a date range
12. All sales for a branch, sorted by date
13. Purchases vs. sales per branch
14. Sales handled by a specific employee in a date range
15. Purchases per supplier for the last quarter

**Customers**

16. Inactive customers (no purchase in 6 months)
17. Consultations received per customer
18. Product categories most frequently bought per customer

**Performance & management**

19. Top 10 best-selling products chain-wide
20. Most popular product per branch
21. Profit margin per product
22. Revenue, expenses, salaries, and net profit per branch, plus an inventory
    stock-movement report

Techniques used across these: multi-table `JOIN`s, `LEFT JOIN` with
`COALESCE` for zero-row groups, `GROUP BY` with `HAVING`, correlated
subqueries, `NOT EXISTS` for the inactive-customer query, window-style
ranking via grouped aggregates, `DATE_SUB`/`INTERVAL` date arithmetic, and
computed columns for profit margin.

---

## Web Application

### Role-based access control

Permissions are declared in a single `ROLE_PERMISSIONS` dictionary and enforced
by two decorators, `@login_required` and `@role_required`. The same dictionary
is exposed to Jinja templates through a `has_permission()` context processor, so
the navigation menu only renders links the current user is allowed to open.

| Role | Access |
| --- | --- |
| **Branch Manager** | Everything: all CRUD, all queries, all reports |
| **Nutrition Specialist** | Customers and products, consultations, customer categories |
| **Cashier** | Sales entry, customers, products, inventory lookup |
| **Warehouse Keeper** | Inventory CRUD, purchases, low-stock and stock-movement views |

Passwords are stored as SHA-256 hashes, never in plain text.

### Features

- Dashboard with chain-wide KPIs
- CRUD for branches, employees, customers, products, and inventory
- Sales browser with drill-down into line items
- Three management reports: top products, branch performance, inactive customers
- One page per analytical query, several with date-range or branch filters
- Flash-message feedback and centralized error handling in `execute_query()`

---

## Setup

### Requirements

- Python 3.8+
- MySQL 8.0+ (the schema uses `DEFAULT (CURRENT_DATE)`, which needs 8.0)

### 1. Create the database

```bash
mysql -u root -p < NutriHealthDatabase.sql
```

This drops and recreates `nutri_health_db`, creates all tables and indexes, and
loads the seed data.

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the connection

The app reads its configuration from environment variables:

```bash
# Windows PowerShell
$env:DB_HOST="localhost"
$env:DB_USER="root"
$env:DB_PASSWORD="your_mysql_password"
$env:DB_NAME="nutri_health_db"
$env:SECRET_KEY="any_random_string"
```

```bash
# macOS / Linux
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD=your_mysql_password
export DB_NAME=nutri_health_db
export SECRET_KEY=any_random_string
```

### 4. Run

```bash
python PythonCode.py
```

Open <http://localhost:5000>.

### Demo accounts

All seeded accounts use the password `password123`.

| Username | Role |
| --- | --- |
| `ahmad_m` | Branch Manager |
| `fatima_a` | Nutrition Specialist |
| `mohammed_k` | Cashier |
| `sara_a` | Warehouse Keeper |

---

## Project Structure

```
.
├── NutriHealthDatabase.sql          # Schema, constraints, indexes, seed data, 22 queries
├── PythonCode.py                    # Flask application
├── requirements.txt
├── er-diagram.drawio                # Editable ER diagram (draw.io source)
├── er-diagram.png                   # Exported ER diagram
├── static/
│   └── css/
│       └── style.css
└── templates/
    ├── base.html                    # Layout with permission-aware navigation
    ├── index.html, login.html, dashboard.html
    ├── branches.html, employees.html, customers.html,
    │   products.html, inventory.html, sales.html    # List views
    ├── add_*.html, edit_*.html                      # Forms
    ├── branch_details.html, sale_details.html       # Detail views
    ├── queries/                                     # One page per analytical query
    └── reports/                                     # Management reports
```

---

## Tech Stack

MySQL 8 · Python 3 · Flask · Jinja2 · `mysql-connector-python` · Bootstrap-styled
CSS · draw.io for the ER diagram
