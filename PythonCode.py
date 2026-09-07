from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import hashlib
import os
from functools import wraps

app = Flask(__name__)

@app.route('/test-template')
def test_template():
    import os
    template_path = os.path.join(app.template_folder, 'queries', 'all_queries.html')
    return f"""
    <h1>Template Debug Info</h1>
    <p>Template folder: {app.template_folder}</p>
    <p>Looking for: {template_path}</p>
    <p>File exists: {os.path.exists(template_path)}</p>
    <p>Current directory: {os.getcwd()}</p>
    """

app.secret_key = os.environ.get('SECRET_KEY', 'nutri_health_secret_key_2026')


DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', '068000'),
    'database': os.environ.get('DB_NAME', 'nutri_health_db')
}

ROLE_PERMISSIONS = {
    'Branch_Manager': {
        # Full access to everything
        'dashboard', 'branches', 'branch_details', 'employees', 'customers', 
        'products', 'inventory', 'sales', 'sale_details', 'purchases', 'suppliers',
        'reports', 'all_queries', 
        'add_branch', 'edit_branch', 'delete_branch',
        'add_employee', 'edit_employee', 'delete_employee',
        'add_customer', 'edit_customer', 'delete_customer',
        'add_product', 'edit_product', 'delete_product',
        'add_inventory', 'edit_inventory', 'delete_inventory',
        'add_sale', 'edit_sale', 'delete_sale',
        'add_purchase', 'edit_purchase',
        'top_products_report', 'branch_performance_report', 
        'inactive_customers_report', 'product_profit_margins',
        'branch_revenue_expenses', 'management_summary'
    },
    
    'Nutrition_Specialist': {
        
        'dashboard', 'customers', 'products',
        'add_customer', 'edit_customer', 'view_customer_details',
        'customer_consultations', 'customer_categories',
        'diet_plans', 'appointments'
        
    },
    
    'Cashier': {
      
        'dashboard', 'customers', 'products', 'inventory', 'sales', 'sale_details',
        'add_customer', 'add_sale', 'view_customer_details',
        'products_by_category'
        
        
    },
    
    'Warehouse_Keeper': {
        
        'dashboard', 'products', 'inventory', 'purchases',
        'add_inventory', 'edit_inventory', 'delete_inventory',
        'low_stock_query', 'inventory_updates', 'products_by_category',
        'category_summary', 'receive_purchase'
        
    }
}

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    """Decorator to require specific roles or check function permissions"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page', 'warning')
                return redirect(url_for('login'))
            
            user_role = session.get('role')
            function_name = f.__name__
            
            
            allowed_functions = ROLE_PERMISSIONS.get(user_role, set())
            
            if user_role not in allowed_roles and function_name not in allowed_functions:
                flash('You do not have permission to access this page', 'danger')
                return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

#================================================
def execute_query(query, params=None, commit=False, fetchone=False, fetchall=False):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            if commit:
                conn.commit()
            if fetchone:
                return cursor.fetchone()
            if fetchall:
                return cursor.fetchall()
            return True
        except Error as e:
            print(f"Query error: {e}")
            flash(f"Database error: {str(e)}", 'danger')
            return None
        finally:
            cursor.close()
            conn.close()
    return None



@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login with password verification"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            
            
            query = """
                SELECT ua.*, e.Employee_Name, e.Position 
                FROM UserAccount ua
                JOIN Employees e ON ua.Employee_ID = e.Employee_ID
                WHERE ua.User_Name = %s
            """
            cursor.execute(query, (username,))
            user = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            
            if user and user['User_Password'] == hash_password(password):
                
                session['user_id'] = user['User_ID']
                session['username'] = user['User_Name']
                session['role'] = user['Role']
                session['employee_name'] = user['Employee_Name']
                
                flash(f'Welcome, {user["Employee_Name"]}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password', 'danger')
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('index'))



@app.route('/dashboard')
def dashboard():
    """Main dashboard with statistics"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'danger')
        return redirect(url_for('index'))
    
    cursor = conn.cursor(dictionary=True)
    
   
    stats = {}
    
    # Total branches
    cursor.execute("SELECT COUNT(*) as count FROM Branches")
    stats['total_branches'] = cursor.fetchone()['count']
    
    # Total employees
    cursor.execute("SELECT COUNT(*) as count FROM Employees")
    stats['total_employees'] = cursor.fetchone()['count']
    
    # Total customers
    cursor.execute("SELECT COUNT(*) as count FROM Customers")
    stats['total_customers'] = cursor.fetchone()['count']
    
    # Total products
    cursor.execute("SELECT COUNT(*) as count FROM Health_Products")
    stats['total_products'] = cursor.fetchone()['count']
    
    # Total sales today
    cursor.execute("""
        SELECT COUNT(*) as count, COALESCE(SUM(Total_Price), 0) as amount 
        FROM Sales 
        WHERE Sale_Date = CURDATE()
    """)
    today_sales = cursor.fetchone()
    stats['today_sales_count'] = today_sales['count']
    stats['today_sales_amount'] = float(today_sales['amount'])
    
    # Recent sales
    cursor.execute("""
        SELECT s.Sale_ID, s.Sale_Date, 
               CONCAT(c.Customer_FirstName, ' ', c.Customer_LastName) as Customer_Name,
               b.Branch_Name, s.Total_Price
        FROM Sales s
        JOIN Customers c ON s.Customer_ID = c.Customer_ID
        JOIN Branches b ON s.Branch_ID = b.Branch_ID
        ORDER BY s.Sale_Date DESC, s.Sale_ID DESC
        LIMIT 5
    """)
    recent_sales = cursor.fetchall()
    
    # Low stock products
    cursor.execute("""
        SELECT b.Branch_Name, hp.Product_Name, i.Quantity
        FROM Inventory i
        JOIN Health_Products hp ON i.Product_ID = hp.Product_ID
        JOIN Branches b ON i.Branch_ID = b.Branch_ID
        WHERE i.Quantity < 50
        ORDER BY i.Quantity ASC
        LIMIT 5
    """)
    low_stock = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('dashboard.html', stats=stats, 
                         recent_sales=recent_sales, low_stock=low_stock)

# ==================== Branch Management ====================

@app.route('/branches')
@role_required('Branch_Manager')
def branches():
    """List all branches"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT b.*, e.Employee_Name as Manager_Name
        FROM Branches b
        LEFT JOIN Employees e ON b.Manager_ID = e.Employee_ID
        ORDER BY b.Branch_ID
    """)
    branches_list = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('branches.html', branches=branches_list)

@app.route('/branch/<int:branch_id>')
def branch_details(branch_id):
    """Branch details with employees and statistics"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Branch info
    cursor.execute("""
        SELECT b.*, e.Employee_Name as Manager_Name
        FROM Branches b
        LEFT JOIN Employees e ON b.Manager_ID = e.Employee_ID
        WHERE b.Branch_ID = %s
    """, (branch_id,))
    branch = cursor.fetchone()
    
    # Branch employees
    cursor.execute("""
        SELECT Employee_ID, Employee_Name, Position, Salary, Phone
        FROM Employees
        WHERE Branch_ID = %s
        ORDER BY Employee_Name
    """, (branch_id,))
    employees = cursor.fetchall()
    
    # Branch statistics
    cursor.execute("""
        SELECT 
            COUNT(DISTINCT s.Sale_ID) as Total_Sales,
            COALESCE(SUM(s.Total_Price), 0) as Total_Revenue
        FROM Sales s
        WHERE s.Branch_ID = %s
    """, (branch_id,))
    stats = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return render_template('branch_details.html', branch=branch, 
                         employees=employees, stats=stats)

@app.route('/add_branch', methods=['GET', 'POST'])
def add_branch():
    """Add new branch with proper manager handling"""
    if 'user_id' not in session:
        flash('Please log in first', 'danger')
        return redirect(url_for('login'))
    
    # Get list of employees who can be managers
    employees = execute_query(
        "SELECT Employee_ID, Employee_Name, Position FROM Employees ORDER BY Employee_Name",
        fetchall=True
    ) or []
    
    if request.method == 'POST':
        branch_name = request.form.get('branch_name', '').strip()
        city = request.form.get('city', '').strip()
        address = request.form.get('address', '').strip()
        phone = request.form.get('phone', '').strip()
        manager_id = request.form.get('manager_id') or None
        
        if not branch_name or not city or not phone:
            flash('Branch Name, City and Phone are required', 'danger')
            return render_template('add_branch.html', employees=employees)
        
        insert_query = """
            INSERT INTO Branches 
            (Branch_Name, City, Address, Phone, Manager_ID)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (branch_name, city, address, phone, manager_id)
        
        if execute_query(insert_query, params, commit=True):
            flash('Branch added successfully', 'success')
            return redirect(url_for('branches'))
        else:
            flash('Failed to add branch (phone may already exist)', 'danger')
    
    return render_template('add_branch.html', employees=employees)

@app.route('/edit_branch/<int:branch_id>', methods=['GET', 'POST'])
def edit_branch(branch_id):
    """Edit branch with proper manager update handling"""
    if 'user_id' not in session:
        flash('Please log in first', 'danger')
        return redirect(url_for('login'))
    
    # Get list of employees for manager dropdown
    employees = execute_query(
        "SELECT Employee_ID, Employee_Name, Position FROM Employees ORDER BY Employee_Name",
        fetchall=True
    ) or []
    
    # Fetch current branch data
    branch = execute_query(
        """
        SELECT b.*, e.Employee_Name AS Manager_Name
        FROM Branches b
        LEFT JOIN Employees e ON b.Manager_ID = e.Employee_ID
        WHERE b.Branch_ID = %s
        """,
        (branch_id,),
        fetchone=True
    )
    
    if not branch:
        flash('Branch not found', 'danger')
        return redirect(url_for('branches'))
    
    if request.method == 'POST':
        branch_name = request.form.get('branch_name', '').strip()
        city = request.form.get('city', '').strip()
        address = request.form.get('address', '').strip()
        phone = request.form.get('phone', '').strip()
        manager_id = request.form.get('manager_id') or None
        
        if not branch_name or not city or not phone:
            flash('Branch Name, City and Phone are required', 'danger')
            return render_template('edit_branch.html', 
                                   branch=branch, 
                                   employees=employees)
        
        update_query = """
            UPDATE Branches 
            SET Branch_Name = %s, City = %s, Address = %s, 
                Phone = %s, Manager_ID = %s
            WHERE Branch_ID = %s
        """
        params = (branch_name, city, address, phone, manager_id, branch_id)
        
        if execute_query(update_query, params, commit=True):
            flash('Branch updated successfully', 'success')
            return redirect(url_for('branches'))
        else:
            flash('Failed to update branch. Phone may already exist.', 'danger')
    
    return render_template('edit_branch.html', 
                           branch=branch, 
                           employees=employees)

@app.route('/delete_branch/<int:branch_id>', methods=['POST'])
def delete_branch(branch_id):
    """Delete a branch"""
    if 'user_id' not in session:
        flash('Please log in first', 'danger')
        return redirect(url_for('login'))
    
    # Check if branch has employees
    employees = execute_query(
        "SELECT COUNT(*) as count FROM Employees WHERE Branch_ID = %s",
        (branch_id,),
        fetchone=True
    )
    
    if employees and employees['count'] > 0:
        flash('Cannot delete branch with employees. Reassign employees first.', 'danger')
        return redirect(url_for('branches'))
    
    if execute_query("DELETE FROM Branches WHERE Branch_ID = %s", (branch_id,), commit=True):
        flash('Branch deleted successfully', 'success')
    else:
        flash('Failed to delete branch', 'danger')
    
    return redirect(url_for('branches'))

# ==================== Employee Management ====================

@app.route('/employees')
def employees():
    """List all employees"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT e.*, b.Branch_Name
        FROM Employees e
        JOIN Branches b ON e.Branch_ID = b.Branch_ID
        ORDER BY e.Employee_Name
    """)
    employees_list = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('employees.html', employees=employees_list)

@app.route('/employee/add', methods=['GET', 'POST'])
def add_employee():
    """Add new employee"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    branches = execute_query(
        "SELECT Branch_ID, Branch_Name FROM Branches ORDER BY Branch_Name",
        fetchall=True
    ) or []
    
    if request.method == 'POST':
        employee_name = request.form['employee_name']
        position = request.form['position']
        branch_id = request.form['branch_id']
        salary = request.form['salary']
        phone = request.form['phone']
        address = request.form.get('address', '')
        
        insert_query = """
            INSERT INTO Employees 
            (Employee_Name, Position, Branch_ID, Salary, Phone, Address)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (employee_name, position, branch_id, salary, phone, address)
        
        if execute_query(insert_query, params, commit=True):
            flash('Employee added successfully', 'success')
            return redirect(url_for('employees'))
        else:
            flash('Failed to add employee (phone may already exist)', 'danger')
    
    return render_template('add_employee.html', branches=branches)

@app.route('/employee/edit/<int:employee_id>', methods=['GET', 'POST'])
def edit_employee(employee_id):
    """Edit existing employee"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    branches = execute_query(
        "SELECT Branch_ID, Branch_Name FROM Branches ORDER BY Branch_Name",
        fetchall=True
    ) or []
    
    employee = execute_query(
        "SELECT * FROM Employees WHERE Employee_ID = %s",
        (employee_id,),
        fetchone=True
    )
    
    if not employee:
        flash('Employee not found', 'danger')
        return redirect(url_for('employees'))
    
    if request.method == 'POST':
        employee_name = request.form['employee_name']
        position = request.form['position']
        branch_id = request.form['branch_id']
        salary = request.form['salary']
        phone = request.form['phone']
        address = request.form.get('address', '')
        
        update_query = """
            UPDATE Employees 
            SET Employee_Name = %s, Position = %s, Branch_ID = %s, 
                Salary = %s, Phone = %s, Address = %s
            WHERE Employee_ID = %s
        """
        params = (employee_name, position, branch_id, salary, phone, address, employee_id)
        
        if execute_query(update_query, params, commit=True):
            flash('Employee updated successfully', 'success')
            return redirect(url_for('employees'))
        else:
            flash('Failed to update employee', 'danger')
    
    return render_template('edit_employee.html', employee=employee, branches=branches)

@app.route('/employee/delete/<int:employee_id>', methods=['POST'])
def delete_employee(employee_id):
    """Delete an employee"""
    if 'user_id' not in session:
        flash('Please log in first', 'danger')
        return redirect(url_for('login'))
    
    # Check if employee is a manager
    is_manager = execute_query(
        "SELECT COUNT(*) as count FROM Branches WHERE Manager_ID = %s",
        (employee_id,),
        fetchone=True
    )
    
    if is_manager and is_manager['count'] > 0:
        flash('Cannot delete employee who is a branch manager. Reassign manager first.', 'danger')
        return redirect(url_for('employees'))
    
    if execute_query("DELETE FROM Employees WHERE Employee_ID = %s", (employee_id,), commit=True):
        flash('Employee deleted successfully', 'success')
    else:
        flash('Failed to delete employee', 'danger')
    
    return redirect(url_for('employees'))

# ==================== Customer Management ====================

@app.route('/customers')
def customers():
    """List all customers"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT c.*, 
               COUNT(DISTINCT s.Sale_ID) as Total_Purchases,
               COALESCE(SUM(s.Total_Price), 0) as Total_Spent,
               MAX(s.Sale_Date) as Last_Purchase
        FROM Customers c
        LEFT JOIN Sales s ON c.Customer_ID = s.Customer_ID
        GROUP BY c.Customer_ID
        ORDER BY c.Customer_ID DESC
    """)
    customers_list = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('customers.html', customers=customers_list)

@app.route('/customer/add', methods=['GET', 'POST'])
def add_customer():
    """Add new customer"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone = request.form['phone']
        address = request.form.get('address', '')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO Customers (Customer_FirstName, Customer_LastName, Phone, Address)
                VALUES (%s, %s, %s, %s)
            """, (first_name, last_name, phone, address))
            conn.commit()
            flash('Customer added successfully', 'success')
            return redirect(url_for('customers'))
        except Error as e:
            flash(f'Error adding customer: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()
    
    return render_template('add_customer.html')

@app.route('/customer/edit/<int:customer_id>', methods=['GET', 'POST'])
def edit_customer(customer_id):
    """Edit existing customer"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone = request.form['phone']
        address = request.form.get('address', '')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE Customers 
                SET Customer_FirstName = %s, Customer_LastName = %s, 
                    Phone = %s, Address = %s
                WHERE Customer_ID = %s
            """, (first_name, last_name, phone, address, customer_id))
            conn.commit()
            flash('Customer updated successfully', 'success')
            return redirect(url_for('customers'))
        except Error as e:
            flash(f'Error updating customer: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()
    
    # GET request - fetch customer data
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Customers WHERE Customer_ID = %s", (customer_id,))
    customer = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not customer:
        flash('Customer not found', 'danger')
        return redirect(url_for('customers'))
    
    return render_template('edit_customer.html', customer=customer)

@app.route('/customer/delete/<int:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    """Delete a customer"""
    if 'user_id' not in session:
        flash('Please log in first', 'danger')
        return redirect(url_for('login'))
    
    # Check if customer has sales
    has_sales = execute_query(
        "SELECT COUNT(*) as count FROM Sales WHERE Customer_ID = %s",
        (customer_id,),
        fetchone=True
    )
    
    if has_sales and has_sales['count'] > 0:
        flash('Cannot delete customer with existing sales records', 'danger')
        return redirect(url_for('customers'))
    
    if execute_query("DELETE FROM Customers WHERE Customer_ID = %s", (customer_id,), commit=True):
        flash('Customer deleted successfully', 'success')
    else:
        flash('Failed to delete customer', 'danger')
    
    return redirect(url_for('customers'))

# ==================== Product Management ====================

@app.route('/products')
def products():
    """List all products"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT hp.*, s.Supplier_Name,
               (hp.Price - hp.Cost_Price) as Profit,
               ROUND(((hp.Price - hp.Cost_Price) / hp.Price) * 100, 2) as Margin
        FROM Health_Products hp
        JOIN Suppliers s ON hp.Supplier_ID = s.Supplier_ID
        ORDER BY hp.Product_Name
    """)
    products_list = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('products.html', products=products_list)

@app.route('/product/add', methods=['GET', 'POST'])
def add_product():
    """Add new product"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get suppliers for dropdown
    suppliers = execute_query(
        "SELECT Supplier_ID, Supplier_Name FROM Suppliers ORDER BY Supplier_Name",
        fetchall=True
    ) or []
    
    if request.method == 'POST':
        product_name = request.form['name']
        category = request.form['category']
        price = request.form['price']
        cost_price = request.form['cost_price']
        expiry_date = request.form.get('expiry_date') or None
        supplier_id = request.form['supplier_id']
        description = request.form.get('description', '')
        
        insert_query = """
            INSERT INTO Health_Products 
            (Product_Name, Category, Price, Cost_Price, Expiry_Date, Supplier_ID, Description)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (product_name, category, price, cost_price, expiry_date, supplier_id, description)
        
        if execute_query(insert_query, params, commit=True):
            flash('Product added successfully', 'success')
            return redirect(url_for('products'))
        else:
            flash('Failed to add product', 'danger')
    
    return render_template('add_product.html', suppliers=suppliers)

@app.route('/product/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    """Edit existing product"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get suppliers for dropdown
    suppliers = execute_query(
        "SELECT Supplier_ID, Supplier_Name FROM Suppliers ORDER BY Supplier_Name",
        fetchall=True
    ) or []
    
    # Get product data
    product = execute_query(
        "SELECT * FROM Health_Products WHERE Product_ID = %s",
        (product_id,),
        fetchone=True
    )
    
    if not product:
        flash('Product not found', 'danger')
        return redirect(url_for('products'))
    
    if request.method == 'POST':
        product_name = request.form['name']
        category = request.form['category']
        price = request.form['price']
        cost_price = request.form['cost_price']
        expiry_date = request.form.get('expiry_date') or None
        supplier_id = request.form['supplier_id']
        description = request.form.get('description', '')
        
        update_query = """
            UPDATE Health_Products 
            SET Product_Name = %s, Category = %s, Price = %s, Cost_Price = %s,
                Expiry_Date = %s, Supplier_ID = %s, Description = %s
            WHERE Product_ID = %s
        """
        params = (product_name, category, price, cost_price, expiry_date, 
                 supplier_id, description, product_id)
        
        if execute_query(update_query, params, commit=True):
            flash('Product updated successfully', 'success')
            return redirect(url_for('products'))
        else:
            flash('Failed to update product', 'danger')
    
    return render_template('edit_product.html', product=product, suppliers=suppliers)

@app.route('/product/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    """Delete a product"""
    if 'user_id' not in session:
        flash('Please log in first', 'danger')
        return redirect(url_for('login'))
    
    # Check if product exists in inventory
    in_inventory = execute_query(
        "SELECT COUNT(*) as count FROM Inventory WHERE Product_ID = %s",
        (product_id,),
        fetchone=True
    )
    
    if in_inventory and in_inventory['count'] > 0:
        flash('Cannot delete product that exists in inventory', 'danger')
        return redirect(url_for('products'))
    
    # Check if product exists in sales
    in_sales = execute_query(
        "SELECT COUNT(*) as count FROM Sale_Details WHERE Product_ID = %s",
        (product_id,),
        fetchone=True
    )
    
    if in_sales and in_sales['count'] > 0:
        flash('Cannot delete product that has been sold', 'danger')
        return redirect(url_for('products'))
    
    if execute_query("DELETE FROM Health_Products WHERE Product_ID = %s", (product_id,), commit=True):
        flash('Product deleted successfully', 'success')
    else:
        flash('Failed to delete product', 'danger')
    
    return redirect(url_for('products'))

# ==================== Inventory Management ====================

@app.route('/inventory')
def inventory():
    """Inventory overview"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    branch_id = request.args.get('branch_id', type=int)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get all branches for filter
    cursor.execute("SELECT Branch_ID, Branch_Name FROM Branches ORDER BY Branch_Name")
    branches_list = cursor.fetchall()
    
    # Build query based on filter
    if branch_id:
        query = """
            SELECT i.*, hp.Product_Name, hp.Category, hp.Price,
                   b.Branch_Name, s.Supplier_Name
            FROM Inventory i
            JOIN Health_Products hp ON i.Product_ID = hp.Product_ID
            JOIN Branches b ON i.Branch_ID = b.Branch_ID
            JOIN Suppliers s ON hp.Supplier_ID = s.Supplier_ID
            WHERE i.Branch_ID = %s
            ORDER BY hp.Category, hp.Product_Name
        """
        cursor.execute(query, (branch_id,))
    else:
        query = """
            SELECT i.*, hp.Product_Name, hp.Category, hp.Price,
                   b.Branch_Name, s.Supplier_Name
            FROM Inventory i
            JOIN Health_Products hp ON i.Product_ID = hp.Product_ID
            JOIN Branches b ON i.Branch_ID = b.Branch_ID
            JOIN Suppliers s ON hp.Supplier_ID = s.Supplier_ID
            ORDER BY b.Branch_Name, hp.Category, hp.Product_Name
        """
        cursor.execute(query)
    
    inventory_list = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('inventory.html', inventory=inventory_list, 
                         branches=branches_list, selected_branch=branch_id)


@app.route('/inventory/add', methods=['GET', 'POST'])
def add_inventory():
    """Add new inventory item"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get branches and products for dropdowns
    branches = execute_query(
        "SELECT Branch_ID, Branch_Name FROM Branches ORDER BY Branch_Name",
        fetchall=True
    ) or []
    
    products = execute_query(
        "SELECT Product_ID, Product_Name, Category FROM Health_Products ORDER BY Product_Name",
        fetchall=True
    ) or []
    
    if request.method == 'POST':
        branch_id = request.form['branch_id']
        product_id = request.form['product_id']
        quantity = request.form['quantity']
        entry_date = request.form.get('entry_date') or None
        
        # Check if this combination already exists
        existing = execute_query(
            """SELECT Inventory_ID FROM Inventory 
               WHERE Branch_ID = %s AND Product_ID = %s""",
            (branch_id, product_id),
            fetchone=True
        )
        
        if existing:
            flash('This product already exists in inventory for this branch. Use Edit to update quantity.', 'warning')
            return redirect(url_for('inventory'))
        
        insert_query = """
            INSERT INTO Inventory 
            (Branch_ID, Product_ID, Quantity, Entry_Date)
            VALUES (%s, %s, %s, %s)
        """
        params = (branch_id, product_id, quantity, entry_date)
        
        if execute_query(insert_query, params, commit=True):
            flash('Inventory item added successfully', 'success')
            return redirect(url_for('inventory'))
        else:
            flash('Failed to add inventory item', 'danger')
    
    from datetime import date
    today = date.today().strftime('%Y-%m-%d')
    
    return render_template('add_inventory.html', branches=branches, 
                         products=products, today=today)

@app.route('/inventory/edit/<int:inventory_id>', methods=['GET', 'POST'])
def edit_inventory(inventory_id):
    """Edit existing inventory item"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get branches and products for dropdowns
    branches = execute_query(
        "SELECT Branch_ID, Branch_Name FROM Branches ORDER BY Branch_Name",
        fetchall=True
    ) or []
    
    products = execute_query(
        "SELECT Product_ID, Product_Name, Category FROM Health_Products ORDER BY Product_Name",
        fetchall=True
    ) or []
    
    # Get inventory data
    inventory = execute_query(
        "SELECT * FROM Inventory WHERE Inventory_ID = %s",
        (inventory_id,),
        fetchone=True
    )
    
    if not inventory:
        flash('Inventory item not found', 'danger')
        return redirect(url_for('inventory'))
    
    if request.method == 'POST':
        branch_id = request.form['branch_id']
        product_id = request.form['product_id']
        quantity = request.form['quantity']
        entry_date = request.form.get('entry_date') or None
        
        update_query = """
            UPDATE Inventory 
            SET Branch_ID = %s, Product_ID = %s, Quantity = %s, Entry_Date = %s
            WHERE Inventory_ID = %s
        """
        params = (branch_id, product_id, quantity, entry_date, inventory_id)
        
        if execute_query(update_query, params, commit=True):
            flash('Inventory updated successfully', 'success')
            return redirect(url_for('inventory'))
        else:
            flash('Failed to update inventory', 'danger')
    
    return render_template('edit_inventory.html', inventory=inventory, 
                         branches=branches, products=products)

@app.route('/inventory/delete/<int:inventory_id>', methods=['POST'])
def delete_inventory(inventory_id):
    """Delete an inventory item"""
    if 'user_id' not in session:
        flash('Please log in first', 'danger')
        return redirect(url_for('login'))
    
    if execute_query("DELETE FROM Inventory WHERE Inventory_ID = %s", 
                    (inventory_id,), commit=True):
        flash('Inventory item deleted successfully', 'success')
    else:
        flash('Failed to delete inventory item', 'danger')
    
    return redirect(url_for('inventory'))
# ==================== Sales Management ====================

@app.route('/sales')
def sales():
    """List all sales"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if start_date and end_date:
        query = """
            SELECT s.*, 
                   CONCAT(c.Customer_FirstName, ' ', c.Customer_LastName) as Customer_Name,
                   e.Employee_Name, b.Branch_Name
            FROM Sales s
            JOIN Customers c ON s.Customer_ID = c.Customer_ID
            JOIN Employees e ON s.Employee_ID = e.Employee_ID
            JOIN Branches b ON s.Branch_ID = b.Branch_ID
            WHERE s.Sale_Date BETWEEN %s AND %s
            ORDER BY s.Sale_Date DESC, s.Sale_ID DESC
        """
        cursor.execute(query, (start_date, end_date))
    else:
        query = """
            SELECT s.*, 
                   CONCAT(c.Customer_FirstName, ' ', c.Customer_LastName) as Customer_Name,
                   e.Employee_Name, b.Branch_Name
            FROM Sales s
            JOIN Customers c ON s.Customer_ID = c.Customer_ID
            JOIN Employees e ON s.Employee_ID = e.Employee_ID
            JOIN Branches b ON s.Branch_ID = b.Branch_ID
            ORDER BY s.Sale_Date DESC, s.Sale_ID DESC
            LIMIT 50
        """
        cursor.execute(query)
    
    sales_list = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('sales.html', sales=sales_list, 
                         start_date=start_date, end_date=end_date)

@app.route('/sale/<int:sale_id>')
def sale_details(sale_id):
    """Sale details with items"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Sale header
    cursor.execute("""
        SELECT s.*, 
               CONCAT(c.Customer_FirstName, ' ', c.Customer_LastName) as Customer_Name,
               c.Phone as Customer_Phone,
               e.Employee_Name, b.Branch_Name
        FROM Sales s
        JOIN Customers c ON s.Customer_ID = c.Customer_ID
        JOIN Employees e ON s.Employee_ID = e.Employee_ID
        JOIN Branches b ON s.Branch_ID = b.Branch_ID
        WHERE s.Sale_ID = %s
    """, (sale_id,))
    sale = cursor.fetchone()
    
    # Sale items
    cursor.execute("""
        SELECT sd.*, hp.Product_Name, hp.Category
        FROM Sale_Details sd
        JOIN Health_Products hp ON sd.Product_ID = hp.Product_ID
        WHERE sd.Sale_ID = %s
    """, (sale_id,))
    items = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('sale_details.html', sale=sale, items=items)

# ==================== Reports ====================

@app.route('/reports')
def reports():
    """Reports dashboard"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('reports.html')

@app.route('/reports/top-products')
def top_products_report():
    """Top selling products report"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT hp.Product_ID, hp.Product_Name, hp.Category,
               SUM(sd.Quantity) as Total_Sold,
               SUM(sd.Subtotal) as Total_Revenue,
               COUNT(DISTINCT sd.Sale_ID) as Number_Of_Sales
        FROM Sale_Details sd
        JOIN Health_Products hp ON sd.Product_ID = hp.Product_ID
        GROUP BY hp.Product_ID
        ORDER BY Total_Sold DESC
        LIMIT 20
    """)
    products = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('reports/top_products.html', products=products)

@app.route('/reports/branch-performance')
def branch_performance_report():
    """Branch performance report"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT b.Branch_ID, b.Branch_Name,
               COALESCE(COUNT(DISTINCT s.Sale_ID), 0) as Total_Sales,
               COALESCE(SUM(s.Total_Price), 0) as Total_Revenue,
               COALESCE(SUM(p.Total_Cost), 0) as Total_Expenses,
               COALESCE(SUM(e.Salary), 0) as Salary_Expenses,
               (COALESCE(SUM(s.Total_Price), 0) - 
                COALESCE(SUM(p.Total_Cost), 0) - 
                COALESCE(SUM(e.Salary), 0)) as Net_Profit
        FROM Branches b
        LEFT JOIN Sales s ON b.Branch_ID = s.Branch_ID
        LEFT JOIN Purchases p ON b.Branch_ID = p.Branch_ID
        LEFT JOIN Employees e ON b.Branch_ID = e.Branch_ID
        GROUP BY b.Branch_ID, b.Branch_Name
        ORDER BY Net_Profit DESC
    """)
    branches = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('reports/branch_performance.html', branches=branches)

@app.route('/reports/inactive-customers')
def inactive_customers_report():
    """Inactive customers report"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT c.Customer_ID,
               CONCAT(c.Customer_FirstName, ' ', c.Customer_LastName) as Customer_Name,
               c.Phone, c.Join_Date,
               MAX(s.Sale_Date) as Last_Purchase,
               DATEDIFF(CURDATE(), MAX(s.Sale_Date)) as Days_Inactive
        FROM Customers c
        LEFT JOIN Sales s ON c.Customer_ID = s.Customer_ID
        GROUP BY c.Customer_ID
        HAVING MAX(s.Sale_Date) < DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
            OR MAX(s.Sale_Date) IS NULL
        ORDER BY Days_Inactive DESC
    """)
    customers = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('reports/inactive_customers.html', customers=customers)

# ==================== COMPLETE Query Routes - All Requirements ====================

@app.route('/queries/all-queries')
def all_queries():
    """Index page showing all available queries"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('queries/all_queries.html')

# ==================== Branches & Employees Queries ====================

@app.route('/queries/branches-by-city')
def branches_by_city():
    """Query 1: Retrieve details of all branches located in a specific city"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    city = request.args.get('city')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get all cities for dropdown
    cursor.execute("SELECT DISTINCT City FROM Branches ORDER BY City")
    cities = cursor.fetchall()
    
    branches = []
    if city:
        # Get branches in specific city
        cursor.execute("""
            SELECT Branch_ID, Branch_Name, City, Address, Phone
            FROM Branches
            WHERE City = %s
            ORDER BY Branch_Name
        """, (city,))
        branches = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('queries/branches_by_city.html', 
                         branches=branches, cities=cities, selected_city=city)

@app.route('/queries/branch-employees')
def branch_employees_query():
    """Query 2: Retrieve names, positions, and salaries of staff at a branch"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    branch_id = request.args.get('branch_id', type=int)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get all branches for dropdown
    cursor.execute("SELECT Branch_ID, Branch_Name FROM Branches ORDER BY Branch_Name")
    branches = cursor.fetchall()
    
    branch = None
    employees = []
    if branch_id:
        # Get branch info
        cursor.execute("SELECT * FROM Branches WHERE Branch_ID = %s", (branch_id,))
        branch = cursor.fetchone()
        
        # Get employees sorted by name
        cursor.execute("""
            SELECT Employee_Name, Position, Salary, Phone
            FROM Employees
            WHERE Branch_ID = %s
            ORDER BY Employee_Name
        """, (branch_id,))
        employees = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('queries/branch_employees.html', 
                         branch=branch, employees=employees, branches=branches,
                         selected_branch=branch_id)

@app.route('/queries/branch-managers')
def branch_managers():
    """Query 3: Retrieve manager name for each branch, sorted by branch number"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT b.Branch_ID, b.Branch_Name, b.City,
               e.Employee_Name AS Manager_Name
        FROM Branches b
        LEFT JOIN Employees e ON b.Manager_ID = e.Employee_ID
        ORDER BY b.Branch_ID
    """)
    branches = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('queries/branch_managers.html', branches=branches)

@app.route('/queries/employee-count')
def employee_count():
    """Query 4: Retrieve total number of employees per branch"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT b.Branch_ID, b.Branch_Name, b.City,
               COUNT(e.Employee_ID) AS Total_Employees
        FROM Branches b
        LEFT JOIN Employees e ON b.Branch_ID = e.Branch_ID
        GROUP BY b.Branch_ID, b.Branch_Name, b.City
        ORDER BY Total_Employees DESC
    """)
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('queries/employee_count.html', results=results)

@app.route('/queries/salary-expenses')
def salary_expenses():
    """Query 5: Retrieve total salary expenses per branch"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT b.Branch_ID, b.Branch_Name, b.City,
               COALESCE(SUM(e.Salary), 0) AS Total_Salary_Expenses,
               COUNT(e.Employee_ID) AS Employee_Count
        FROM Branches b
        LEFT JOIN Employees e ON b.Branch_ID = e.Branch_ID
        GROUP BY b.Branch_ID, b.Branch_Name, b.City
        ORDER BY Total_Salary_Expenses DESC
    """)
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('queries/salary_expenses.html', results=results)

@app.route('/queries/recent-hires')
def recent_hires():
    """Query 6: Retrieve employees hired during the last year"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT e.Employee_ID, e.Employee_Name, e.Position, 
               e.Hire_Date, b.Branch_Name,
               DATEDIFF(CURDATE(), e.Hire_Date) AS Days_Since_Hire
        FROM Employees e
        JOIN Branches b ON e.Branch_ID = b.Branch_ID
        WHERE e.Hire_Date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
        ORDER BY e.Hire_Date DESC
    """)
    employees = cursor.fetchall()
    
    cursor.execute("""
        SELECT COUNT(*) AS Count
        FROM Employees
        WHERE Hire_Date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
    """)
    count = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return render_template('queries/recent_hires.html', 
                         employees=employees, count=count['Count'])

# ==================== Inventory Queries ====================

@app.route('/queries/products-by-category')
def products_by_category():
    """Query 7: Retrieve products at specific branch sorted by category"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    branch_id = request.args.get('branch_id', type=int)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get branches for dropdown
    cursor.execute("SELECT Branch_ID, Branch_Name FROM Branches ORDER BY Branch_Name")
    branches = cursor.fetchall()
    
    products = []
    branch_name = None
    if branch_id:
        # Get branch name
        cursor.execute("SELECT Branch_Name FROM Branches WHERE Branch_ID = %s", (branch_id,))
        branch_result = cursor.fetchone()
        if branch_result:
            branch_name = branch_result['Branch_Name']
        
        # Get products at branch
        cursor.execute("""
            SELECT hp.Product_Name, hp.Category, i.Quantity, hp.Price,
                   s.Supplier_Name
            FROM Inventory i
            JOIN Health_Products hp ON i.Product_ID = hp.Product_ID
            JOIN Suppliers s ON hp.Supplier_ID = s.Supplier_ID
            WHERE i.Branch_ID = %s AND i.Quantity > 0
            ORDER BY hp.Category, hp.Product_Name
        """, (branch_id,))
        products = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('queries/products_by_category.html', 
                         products=products, branches=branches, 
                         selected_branch=branch_id, branch_name=branch_name)

@app.route('/queries/category-summary')
def category_summary():
    """Query 8: Total products in each category at branch, sorted by supplier"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    branch_id = request.args.get('branch_id', type=int)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT Branch_ID, Branch_Name FROM Branches ORDER BY Branch_Name")
    branches = cursor.fetchall()
    
    results = []
    branch_name = None
    if branch_id:
        cursor.execute("SELECT Branch_Name FROM Branches WHERE Branch_ID = %s", (branch_id,))
        branch_result = cursor.fetchone()
        if branch_result:
            branch_name = branch_result['Branch_Name']
            
        cursor.execute("""
            SELECT hp.Category, s.Supplier_Name,
                   COUNT(DISTINCT hp.Product_ID) AS Total_Products,
                   SUM(i.Quantity) AS Total_Quantity
            FROM Inventory i
            JOIN Health_Products hp ON i.Product_ID = hp.Product_ID
            JOIN Suppliers s ON hp.Supplier_ID = s.Supplier_ID
            WHERE i.Branch_ID = %s
            GROUP BY hp.Category, s.Supplier_Name
            ORDER BY s.Supplier_Name, hp.Category
        """, (branch_id,))
        results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('queries/category_summary.html', 
                         results=results, branches=branches, 
                         selected_branch=branch_id, branch_name=branch_name)

@app.route('/queries/low-stock')
def low_stock_query():
    """Query 9: Products below minimum stock level (50)"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT b.Branch_Name, hp.Product_Name, hp.Category, 
               i.Quantity, s.Supplier_Name
        FROM Inventory i
        JOIN Health_Products hp ON i.Product_ID = hp.Product_ID
        JOIN Branches b ON i.Branch_ID = b.Branch_ID
        JOIN Suppliers s ON hp.Supplier_ID = s.Supplier_ID
        WHERE i.Quantity < 50
        ORDER BY i.Quantity ASC, b.Branch_Name
    """)
    products = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('queries/low_stock.html', products=products)

# ==================== Sales & Purchases Queries ====================

@app.route('/queries/sales-by-period')
def sales_by_period():
    """Query 10: Total sales for each branch in specific period"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    results = []
    if start_date and end_date:
        cursor.execute("""
            SELECT b.Branch_ID, b.Branch_Name, b.City,
                   COUNT(s.Sale_ID) AS Total_Sales_Count,
                   COALESCE(SUM(s.Total_Price), 0) AS Total_Sales_Amount
            FROM Branches b
            LEFT JOIN Sales s ON b.Branch_ID = s.Branch_ID 
                AND s.Sale_Date BETWEEN %s AND %s
            GROUP BY b.Branch_ID, b.Branch_Name, b.City
            ORDER BY Total_Sales_Amount DESC
        """, (start_date, end_date))
        results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('queries/sales_by_period.html', 
                         results=results, start_date=start_date, end_date=end_date)

@app.route('/queries/branch-sales')
def branch_sales():
    """Query 11: All sales made by a specific branch, sorted by sale date"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    branch_id = request.args.get('branch_id', type=int)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get all branches for dropdown
    cursor.execute("SELECT Branch_ID, Branch_Name FROM Branches ORDER BY Branch_Name")
    branches = cursor.fetchall()
    
    sales = []
    branch_name = None
    total_amount = 0
    if branch_id:
        # Get branch name
        cursor.execute("SELECT Branch_Name FROM Branches WHERE Branch_ID = %s", (branch_id,))
        branch_result = cursor.fetchone()
        if branch_result:
            branch_name = branch_result['Branch_Name']
        
        # Get all sales for the branch
        cursor.execute("""
            SELECT s.Sale_ID, s.Sale_Date,
                   CONCAT(c.Customer_FirstName, ' ', c.Customer_LastName) AS Customer_Name,
                   e.Employee_Name, s.Total_Price
            FROM Sales s
            JOIN Customers c ON s.Customer_ID = c.Customer_ID
            JOIN Employees e ON s.Employee_ID = e.Employee_ID
            WHERE s.Branch_ID = %s
            ORDER BY s.Sale_Date DESC, s.Sale_ID DESC
        """, (branch_id,))
        sales = cursor.fetchall()
        
        # Calculate total
        if sales:
            total_amount = sum(float(sale['Total_Price']) for sale in sales)
    
    cursor.close()
    conn.close()
    
    return render_template('queries/branch_sales.html', 
                         sales=sales, branches=branches, 
                         selected_branch=branch_id, branch_name=branch_name,
                         total_amount=total_amount)

@app.route('/queries/purchases-sales-summary')
def purchases_sales_summary():
    """Query 12: Total purchases and sales per branch, sorted by branch name"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT b.Branch_ID, b.Branch_Name, b.City,
               COALESCE(SUM(p.Total_Cost), 0) AS Total_Purchases,
               COALESCE(SUM(s.Total_Price), 0) AS Total_Sales,
               COALESCE(SUM(s.Total_Price), 0) - COALESCE(SUM(p.Total_Cost), 0) AS Net_Profit
        FROM Branches b
        LEFT JOIN Purchases p ON b.Branch_ID = p.Branch_ID
        LEFT JOIN Sales s ON b.Branch_ID = s.Branch_ID
        GROUP BY b.Branch_ID, b.Branch_Name, b.City
        ORDER BY b.Branch_Name
    """)
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('queries/purchases_sales_summary.html', results=results)

@app.route('/queries/employee-sales')
def employee_sales():
    """Query 13: Sales handled by specific employee in date range"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    employee_id = request.args.get('employee_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get all employees
    cursor.execute("""
        SELECT e.Employee_ID, e.Employee_Name, e.Position, b.Branch_Name
        FROM Employees e
        JOIN Branches b ON e.Branch_ID = b.Branch_ID
        ORDER BY e.Employee_Name
    """)
    employees = cursor.fetchall()
    
    sales = []
    employee_info = None
    total_amount = 0
    if employee_id and start_date and end_date:
        # Get employee info
        cursor.execute("""
            SELECT e.Employee_Name, e.Position, b.Branch_Name
            FROM Employees e
            JOIN Branches b ON e.Branch_ID = b.Branch_ID
            WHERE e.Employee_ID = %s
        """, (employee_id,))
        employee_info = cursor.fetchone()
        
        # Get sales by employee
        cursor.execute("""
            SELECT s.Sale_ID, s.Sale_Date,
                   CONCAT(c.Customer_FirstName, ' ', c.Customer_LastName) AS Customer_Name,
                   s.Total_Price
            FROM Sales s
            JOIN Customers c ON s.Customer_ID = c.Customer_ID
            WHERE s.Employee_ID = %s
              AND s.Sale_Date BETWEEN %s AND %s
            ORDER BY s.Sale_Date DESC
        """, (employee_id, start_date, end_date))
        sales = cursor.fetchall()
        
        if sales:
            total_amount = sum(float(sale['Total_Price']) for sale in sales)
    
    cursor.close()
    conn.close()
    
    return render_template('queries/employee_sales.html', 
                         sales=sales, employees=employees,
                         selected_employee=employee_id,
                         start_date=start_date, end_date=end_date,
                         employee_info=employee_info, total_amount=total_amount)

@app.route('/queries/supplier-purchases')
def supplier_purchases():
    """Query 14: Purchases from each supplier during last quarter"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT sup.Supplier_ID, sup.Supplier_Name, sup.Phone,
               COUNT(p.Purchase_ID) AS Total_Purchases,
               COALESCE(SUM(p.Total_Cost), 0) AS Total_Amount
        FROM Suppliers sup
        LEFT JOIN Purchases p ON sup.Supplier_ID = p.Supplier_ID
            AND p.Purchase_Date >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
        GROUP BY sup.Supplier_ID, sup.Supplier_Name, sup.Phone
        ORDER BY Total_Amount DESC
    """)
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('queries/supplier_purchases.html', results=results)

# ==================== Customer Queries ====================

@app.route('/queries/customer-consultations')
def customer_consultations():
    """Query 16: Number of consultations/visits each customer received"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT c.Customer_ID,
               CONCAT(c.Customer_FirstName, ' ', c.Customer_LastName) AS Customer_Name,
               c.Phone, c.Join_Date,
               COUNT(DISTINCT s.Sale_ID) AS Total_Visits,
               COUNT(DISTINCT DATE(s.Sale_Date)) AS Unique_Visit_Days,
               MAX(s.Sale_Date) AS Last_Visit
        FROM Customers c
        LEFT JOIN Sales s ON c.Customer_ID = s.Customer_ID
        GROUP BY c.Customer_ID
        ORDER BY Total_Visits DESC
    """)
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('queries/customer_consultations.html', results=results)

@app.route('/queries/customer-categories')
def customer_categories():
    """Query 17: Product categories most frequently purchased by each customer"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT c.Customer_ID,
               CONCAT(c.Customer_FirstName, ' ', c.Customer_LastName) AS Customer_Name,
               hp.Category,
               COUNT(sd.Product_ID) AS Purchase_Count,
               SUM(sd.Quantity) AS Total_Quantity,
               SUM(sd.Subtotal) AS Total_Spent
        FROM Customers c
        JOIN Sales s ON c.Customer_ID = s.Customer_ID
        JOIN Sale_Details sd ON s.Sale_ID = sd.Sale_ID
        JOIN Health_Products hp ON sd.Product_ID = hp.Product_ID
        GROUP BY c.Customer_ID, c.Customer_FirstName, c.Customer_LastName, hp.Category
        ORDER BY c.Customer_ID, Purchase_Count DESC
    """)
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('queries/customer_categories.html', results=results)

# ==================== Reports & Analytics Queries ====================

@app.route('/queries/top-selling-products')
def top_selling_products():
    """Query 18: Top 10 best-selling health products across all branches"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT hp.Product_ID, hp.Product_Name, hp.Category,
               SUM(sd.Quantity) AS Total_Quantity_Sold,
               SUM(sd.Subtotal) AS Total_Revenue,
               COUNT(DISTINCT sd.Sale_ID) AS Number_Of_Sales
        FROM Sale_Details sd
        JOIN Health_Products hp ON sd.Product_ID = hp.Product_ID
        GROUP BY hp.Product_ID, hp.Product_Name, hp.Category
        ORDER BY Total_Quantity_Sold DESC
        LIMIT 10
    """)
    products = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('queries/top_selling_products.html', products=products)

@app.route('/queries/popular-products-by-branch')
def popular_products_by_branch():
    """Query 19: Most popular health products sold in each branch"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT b.Branch_ID, b.Branch_Name, b.City,
               hp.Product_Name, hp.Category,
               SUM(sd.Quantity) AS Total_Sold,
               SUM(sd.Subtotal) AS Total_Revenue
        FROM Sales s
        JOIN Sale_Details sd ON s.Sale_ID = sd.Sale_ID
        JOIN Health_Products hp ON sd.Product_ID = hp.Product_ID
        JOIN Branches b ON s.Branch_ID = b.Branch_ID
        GROUP BY b.Branch_ID, b.Branch_Name, b.City, hp.Product_ID, hp.Product_Name, hp.Category
        ORDER BY b.Branch_Name, Total_Sold DESC
    """)
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('queries/popular_products_by_branch.html', results=results)

@app.route('/queries/product-profit-margins')
def product_profit_margins():
    """Query 20: Profit margin for each product"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT hp.Product_ID, hp.Product_Name, hp.Category,
               s.Supplier_Name,
               hp.Cost_Price, hp.Price AS Selling_Price,
               (hp.Price - hp.Cost_Price) AS Profit_Per_Unit,
               ROUND(((hp.Price - hp.Cost_Price) / hp.Price) * 100, 2) AS Profit_Margin_Percentage
        FROM Health_Products hp
        JOIN Suppliers s ON hp.Supplier_ID = s.Supplier_ID
        ORDER BY Profit_Margin_Percentage DESC
    """)
    products = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('queries/product_profit_margins.html', products=products)

@app.route('/queries/branch-revenue-expenses')
def branch_revenue_expenses():
    """Query 21: Total revenue and expenses for each branch"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT b.Branch_ID, b.Branch_Name, b.City,
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
        GROUP BY b.Branch_ID, b.Branch_Name, b.City
        ORDER BY Net_Profit DESC
    """)
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('queries/branch_revenue_expenses.html', results=results)

@app.route('/queries/management-summary')
def management_summary():
    """Query 22: Summary of sales, purchases, and profit per branch for management"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT 
            b.Branch_ID, b.Branch_Name, b.City,
            COALESCE(sales.Total_Sales_Count, 0) AS Total_Sales_Transactions,
            COALESCE(sales.Total_Revenue, 0) AS Total_Sales_Revenue,
            COALESCE(purchases.Total_Purchase_Count, 0) AS Total_Purchase_Transactions,
            COALESCE(purchases.Total_Expenses, 0) AS Total_Purchase_Cost,
            (COALESCE(sales.Total_Revenue, 0) - COALESCE(purchases.Total_Expenses, 0)) AS Gross_Profit,
            COALESCE(salaries.Salary_Expenses, 0) AS Total_Salaries,
            (COALESCE(sales.Total_Revenue, 0) - 
             COALESCE(purchases.Total_Expenses, 0) - 
             COALESCE(salaries.Salary_Expenses, 0)) AS Net_Profit,
            CASE 
                WHEN COALESCE(sales.Total_Revenue, 0) > 0 
                THEN ROUND(((COALESCE(sales.Total_Revenue, 0) - 
                             COALESCE(purchases.Total_Expenses, 0) - 
                             COALESCE(salaries.Salary_Expenses, 0)) / 
                            COALESCE(sales.Total_Revenue, 0)) * 100, 2)
                ELSE 0
            END AS Profit_Margin_Percentage
        FROM Branches b
        LEFT JOIN (
            SELECT Branch_ID, 
                   COUNT(Sale_ID) AS Total_Sales_Count,
                   SUM(Total_Price) AS Total_Revenue
            FROM Sales
            GROUP BY Branch_ID
        ) sales ON b.Branch_ID = sales.Branch_ID
        LEFT JOIN (
            SELECT Branch_ID, 
                   COUNT(Purchase_ID) AS Total_Purchase_Count,
                   SUM(Total_Cost) AS Total_Expenses
            FROM Purchases
            GROUP BY Branch_ID
        ) purchases ON b.Branch_ID = purchases.Branch_ID
        LEFT JOIN (
            SELECT Branch_ID, SUM(Salary) AS Salary_Expenses
            FROM Employees
            GROUP BY Branch_ID
        ) salaries ON b.Branch_ID = salaries.Branch_ID
        ORDER BY Net_Profit DESC
    """)
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('queries/management_summary.html', results=results)

@app.route('/queries/inventory-updates')
def inventory_updates():
    """Query 23: All inventory transfers and stock updates per product"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT hp.Product_ID, hp.Product_Name, hp.Category,
               b.Branch_Name, i.Quantity, i.Entry_Date AS Update_Date,
               'Stock Entry' AS Transaction_Type,
               s.Supplier_Name
        FROM Inventory i
        JOIN Health_Products hp ON i.Product_ID = hp.Product_ID
        JOIN Branches b ON i.Branch_ID = b.Branch_ID
        JOIN Suppliers s ON hp.Supplier_ID = s.Supplier_ID
        ORDER BY i.Entry_Date DESC, hp.Product_Name
    """)
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('queries/inventory_updates.html', results=results)

@app.context_processor
def utility_processor():
    """Make permission checking available in templates"""
    def has_permission(function_name):
        if 'role' not in session:
            return False
        user_role = session.get('role')
        allowed_functions = ROLE_PERMISSIONS.get(user_role, set())
        return function_name in allowed_functions
    
    return dict(has_permission=has_permission)

# ==================== Run Application ====================

if __name__ == '__main__':
    app.run(debug=True, port=5000)