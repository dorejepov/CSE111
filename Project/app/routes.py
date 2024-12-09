from flask import Blueprint, render_template, redirect, url_for, request, session
from app import get_cursor, get_db
import random
import string

def generate_temp_password(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

main_bp = Blueprint('main', __name__)

# Home page route
@main_bp.route('/')
def home():
    return render_template('index.html')

# Login route (handles both driver and dispatcher logins)
@main_bp.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    cursor = get_cursor()

    # Check if user exists in DriverPasswords table
    driver = cursor.execute("""
        SELECT * FROM DriverPasswords
        WHERE username = ? AND password = ?
    """, (username, password)).fetchone()

    if driver:
        session['driver_id'] = driver['driver_id']
        return redirect(url_for('main.driver_account'))

    # Check if user exists in DispatcherPasswords table
    dispatcher = cursor.execute("""
        SELECT * FROM DispatcherPasswords
        WHERE username = ? AND password = ?
    """, (username, password)).fetchone()

    if dispatcher:
        session['dispatcher_id'] = dispatcher['dispatcher_id']
        return redirect(url_for('main.dispatcher_dashboard'))

    # If neither, show error message
    error_message = "Invalid username or password"
    return render_template('index.html', error=error_message)

@main_bp.route('/driver/account', methods=['GET', 'POST'])
def driver_account():
    if 'driver_id' not in session:
        return redirect(url_for('main.home'))

    cursor = get_cursor()

    if request.method == 'POST':
        # Update driver information
        phone_number = request.form['phone_number']
        payment_type = request.form['payment_type']
        bank_info = request.form['bank_info']
        insurance_id = request.form['insurance_id']

        cursor.execute("""
            UPDATE Drivers
            SET phone_number = ?, payment_type = ?, bank_info = ?, insurance_id = ?
            WHERE driver_id = ?
        """, (phone_number, payment_type, bank_info, insurance_id, session['driver_id']))
        get_db().commit()

    # Fetch the driver's data
    driver = cursor.execute("""
        SELECT d.name, d.phone_number, d.payment_type, d.bank_info, d.medical_card, 
               d.insurance_id, d.policy_end_date, dp.username
        FROM Drivers d
        JOIN DriverPasswords dp ON d.driver_id = dp.driver_id
        WHERE d.driver_id = ?
    """, (session['driver_id'],)).fetchone()

    if not driver:
        return redirect(url_for('main.home'))

    # Fetch all available insurance options
    insurances = cursor.execute("""
        SELECT insurance_id, name FROM Insurance
    """).fetchall()

    return render_template('driver_account.html', driver=driver, insurances=insurances)




@main_bp.route('/dispatcher/dashboard')
def dispatcher_dashboard():
    if 'dispatcher_id' not in session:
        return redirect(url_for('main.home'))
    return render_template('dispatcher/dispatcher_dashboard.html')

@main_bp.route('/dispatcher/trucks')
def view_trucks():
    if 'dispatcher_id' not in session:
        return redirect(url_for('main.home'))

    cursor = get_cursor()
    trucks = cursor.execute("""
        SELECT t.truck_id, t.make, t.model, t.vin, t.license_plate, t.registration, 
               t.policy_end_date, d.name AS drivers_name
        FROM Trucks t
        LEFT JOIN Drivers d ON t.driver_id = d.driver_id
    """).fetchall()
    
    return render_template('dispatcher/trucks.html', trucks=trucks)



@main_bp.route('/dispatcher/drivers')
def view_drivers():
    if 'dispatcher_id' not in session:
        return redirect(url_for('main.home'))

    cursor = get_cursor()
    drivers = cursor.execute("""
        SELECT driver_id, name, phone_number, payment_type, bank_info
        FROM Drivers
    """).fetchall()

    return render_template('dispatcher/drivers.html', drivers=drivers)


@main_bp.route('/request-load', methods=['GET', 'POST'])
def request_load():
    cursor = get_cursor()

    if request.method == 'POST':
        # Get form data
        broker_id = request.form.get('broker')
        phone_number = request.form.get('phone_number')
        origin = request.form.get('origin')
        destination = request.form.get('destination')
        load_details = request.form.get('load_details')

        # Insert data into the LoadRequests table
        cursor.execute("""
            INSERT INTO LoadRequests (broker_id, phone_number, origin, destination, load_details)
            VALUES (?, ?, ?, ?, ?)
        """, (broker_id, phone_number, origin, destination, load_details))
        get_db().commit()

        return redirect(url_for('main.home'))

    # Fetch brokers for the dropdown
    brokers = cursor.execute("SELECT broker_id, company_name FROM Brokers").fetchall()

    return render_template('request_load.html', brokers=brokers)



@main_bp.route('/driver/logout')
def driver_logout():
    session.pop('driver_id', None)  # Remove driver_id from session
    return redirect(url_for('main.home'))  # Redirect to home page

@main_bp.route('/edit-driver-info', methods=['POST'])
def edit_driver_info():
    # Retrieve form data
    phone_number = request.form.get('phone_number')
    payment_type = request.form.get('payment_type')
    bank_info = request.form.get('bank_info')
    medical_card = request.form.get('medical_card')
    insurance_id = request.form.get('insurance_id')
    policy_end_date = request.form.get('policy_end_date')

    # Update the driver's information in the database
    cursor = get_cursor()
    cursor.execute("""
        UPDATE Drivers
        SET phone_number = ?, payment_type = ?, bank_info = ?, medical_card = ?, insurance_id = ?, policy_end_date = ?
        WHERE driver_id = ?
    """, (phone_number, payment_type, bank_info, medical_card, insurance_id, policy_end_date, session['driver_id']))
    get_db().commit()

    return redirect(url_for('main.driver_account'))


@main_bp.route('/dispatcher/account', methods=['GET', 'POST'])
def dispatcher_account():
    if 'dispatcher_id' not in session:
        return redirect(url_for('main.home'))

    cursor = get_cursor()

    if request.method == 'POST':
        # Update dispatcher information
        name = request.form['name']
        phone_number = request.form['phone_number']
        payment_type = request.form['payment_type']
        bank_info = request.form['bank_info']

        cursor.execute("""
            UPDATE Dispatchers
            SET name = ?, phone_number = ?, payment_type = ?, bank_info = ?
            WHERE dispatcher_id = ?
        """, (name, phone_number, payment_type, bank_info, session['dispatcher_id']))
        get_db().commit()

    # Fetch the dispatcher's data
    dispatcher = cursor.execute("""
        SELECT d.dispatcher_id, d.name, d.phone_number, d.payment_type, d.bank_info
        FROM Dispatchers d
        WHERE d.dispatcher_id = ?
    """, (session['dispatcher_id'],)).fetchone()

    if not dispatcher:
        return redirect(url_for('main.home'))

    return render_template('dispatcher/dispatcher_account.html', dispatcher=dispatcher)



@main_bp.route('/edit-dispatcher-info', methods=['POST'])
def edit_dispatcher_info():
    # Retrieve form data
    name = request.form.get('name')
    phone_number = request.form.get('phone_number')
    bank_info = request.form.get('bank_info')

    # Update the dispatcher's information in the database
    cursor = get_cursor()
    cursor.execute("""
        UPDATE Dispatchers
        SET name = ?, phone_number = ?, bank_info = ?
        WHERE dispatcher_id = ?
    """, (name, phone_number, bank_info, session['dispatcher_id']))
    get_db().commit()

    return redirect(url_for('main.dispatcher_account'))


@main_bp.route('/dispatcher/trucks/edit/<int:truck_id>', methods=['GET', 'POST'])
def edit_truck(truck_id):
    cursor = get_cursor()
    
    if request.method == 'POST':
        # Retrieve form data
        driver_id = request.form.get('driver_id')
        make = request.form.get('make')
        model = request.form.get('model')
        vin = request.form.get('vin')
        license_plate = request.form.get('license_plate')
        registration = request.form.get('registration')
        physical_insurance = request.form.get('physical_insurance')
        owner = request.form.get('owner')
        expenses = request.form.get('expenses')
        policy_end_date = request.form.get('policy_end_date')
        destination_state = request.form.get('destination_state')
        following_dest_state = request.form.get('following_dest_state')

        # If a new driver is assigned, remove them from their current truck
        if driver_id:
            cursor.execute("""
                UPDATE Trucks
                SET driver_id = NULL
                WHERE driver_id = ? AND truck_id != ?
            """, (driver_id, truck_id))

        # Update the current truck
        cursor.execute("""
            UPDATE Trucks
            SET make = ?, model = ?, vin = ?, license_plate = ?, registration = ?, physical_insurance = ?, 
                owner = ?, expenses = ?, driver_id = ?, policy_end_date = ?, destination_state = ?, following_dest_state = ?
            WHERE truck_id = ?
        """, (make, model, vin, license_plate, registration, physical_insurance, owner, expenses, driver_id,
              policy_end_date, destination_state, following_dest_state, truck_id))
        get_db().commit()

        return redirect(url_for('main.view_trucks'))

    # Fetch truck and driver data
    trucks = cursor.execute("SELECT * FROM Trucks WHERE truck_id = ?", (truck_id,)).fetchone()
    drivers = cursor.execute("""
        SELECT d.driver_id, d.name
        FROM Drivers d
    """).fetchall()

    return render_template('dispatcher/edit_truck.html', trucks=trucks, drivers=drivers)



@main_bp.route('/dispatcher/trucks/add', methods=['GET', 'POST'])
def add_truck():
    cursor = get_cursor()

    if request.method == 'POST':
        # Get form data
        make = request.form.get('make')
        model = request.form.get('model')
        vin = request.form.get('vin')
        license_plate = request.form.get('license_plate')
        registration = request.form.get('registration')
        physical_insurance = request.form.get('physical_insurance')
        owner = request.form.get('owner')
        expenses = request.form.get('expenses')
        driver_id = request.form.get('driver_id')
        policy_end_date = request.form.get('policy_end_date')
        destination_state = request.form.get('destination_state')
        following_dest_state = request.form.get('following_dest_state')

        # Insert new truck into the database
        cursor.execute("""
            INSERT INTO Trucks (make, model, vin, license_plate, registration, physical_insurance, owner, expenses, driver_id, policy_end_date, destination_state, following_dest_state)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (make, model, vin, license_plate, registration, physical_insurance, owner, expenses, driver_id, policy_end_date, destination_state, following_dest_state))
        get_db().commit()

        return redirect(url_for('main.view_trucks'))

    # Fetch necessary data for dropdowns
    drivers = cursor.execute("SELECT driver_id, name FROM Drivers").fetchall()
    insurances = cursor.execute("SELECT insurance_id, name FROM Insurance").fetchall()

    return render_template('dispatcher/add_truck.html', drivers=drivers, insurances=insurances)


@main_bp.route('/dispatcher/trucks/delete/<int:truck_id>', methods=['POST'])
def delete_truck(truck_id):
    cursor = get_cursor()

    # Delete the truck from the database
    cursor.execute("DELETE FROM Trucks WHERE truck_id = ?", (truck_id,))
    get_db().commit()

    return redirect(url_for('main.view_trucks'))

@main_bp.route('/dispatcher/drivers/applications')
def view_applications():
    if 'dispatcher_id' not in session:
        return redirect(url_for('main.home'))

    cursor = get_cursor()
    applications = cursor.execute("""
        SELECT * FROM Applications
    """).fetchall()

    return render_template('dispatcher/view_applications.html', applications=applications)
@main_bp.route('/dispatcher/drivers/applications/approve/<int:application_id>', methods=['POST'])
def approve_application(application_id):
    if 'dispatcher_id' not in session:
        return redirect(url_for('main.home'))

    cursor = get_cursor()
    # Fetch application details
    application = cursor.execute("""
        SELECT * FROM Applications WHERE application_id = ?
    """, (application_id,)).fetchone()

    if application:
        # Generate temporary password
        temp_password = generate_temp_password()

        # Insert into Drivers table
        cursor.execute("""
            INSERT INTO Drivers (name, phone_number, payment_type, bank_info)
            VALUES (?, ?, 'Pending', 'Pending')
        """, (application['name'], application['phone']))

        # Insert into DriverPasswords table
        driver_id = cursor.lastrowid  # Get the last inserted driver_id
        cursor.execute("""
            INSERT INTO DriverPasswords (driver_id, username, password)
            VALUES (?, ?, ?)
        """, (driver_id, application['name'], temp_password))

        # Delete application after approval
        cursor.execute("DELETE FROM Applications WHERE application_id = ?", (application_id,))
        get_db().commit()

    return redirect(url_for('main.view_applications'))


@main_bp.route('/dispatcher/drivers/applications/reject/<int:application_id>', methods=['POST'])
def reject_application(application_id):
    if 'dispatcher_id' not in session:
        return redirect(url_for('main.home'))

    cursor = get_cursor()
    # Delete application
    cursor.execute("DELETE FROM Applications WHERE application_id = ?", (application_id,))
    get_db().commit()

    return redirect(url_for('main.view_applications'))

@main_bp.route('/dispatcher/drivers/edit/<int:driver_id>', methods=['GET', 'POST'])
def edit_driver(driver_id):
    cursor = get_cursor()
    
    if request.method == 'POST':
        # Retrieve form data
        name = request.form['name']
        phone = request.form['phone']
        payment_type = request.form['payment_type']
        bank_info = request.form['bank_info']

        # Update the driver's information in the database
        cursor.execute("""
            UPDATE Drivers
            SET name = ?, phone_number = ?, payment_type = ?, bank_info = ?
            WHERE driver_id = ?
        """, (name, phone, payment_type, bank_info, driver_id))
        get_db().commit()
        return redirect(url_for('main.view_drivers'))

    # Fetch the driver's data
    driver = cursor.execute("SELECT * FROM Drivers WHERE driver_id = ?", (driver_id,)).fetchone()

    if not driver:
        return redirect(url_for('main.view_drivers'))

    return render_template('dispatcher/edit_driver.html', driver=driver)


@main_bp.route('/dispatcher/drivers/delete/<int:driver_id>', methods=['POST'])
def delete_driver(driver_id):
    cursor = get_cursor()

    # Delete the driver from the database
    cursor.execute("DELETE FROM Drivers WHERE driver_id = ?", (driver_id,))
    get_db().commit()

    return redirect(url_for('main.view_drivers'))

@main_bp.route('/apply', methods=['GET', 'POST'])
def apply():
    if request.method == 'POST':
        # Retrieve form data
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        years_of_exp = request.form['years_of_exp']

        # Insert application into the Applications table
        cursor = get_cursor()
        cursor.execute("""
            INSERT INTO Applications (name, email, phone, address, years_of_exp)
            VALUES (?, ?, ?, ?, ?)
        """, (name, email, phone, address, years_of_exp))
        get_db().commit()

        return redirect(url_for('main.home'))  # Redirect to home or confirmation page

    return render_template('apply.html')




@main_bp.route('/dispatcher/requests/approve/<int:request_id>', methods=['POST'])
def approve_request(request_id):
    if 'dispatcher_id' not in session:
        return redirect(url_for('main.home'))

    cursor = get_cursor()

    # Fetch the request details
    request = cursor.execute("""
        SELECT * FROM LoadRequests WHERE request_id = ?
    """, (request_id,)).fetchone()

    if not request:
        return redirect(url_for('main.view_requests'))

    # Mark the request as approved
    cursor.execute("""
        UPDATE LoadRequests
        SET status = 'Approved'
        WHERE request_id = ?
    """, (request_id,))
    get_db().commit()

    return redirect(url_for('main.view_requests'))


@main_bp.route('/dispatcher/requests/deny/<int:request_id>', methods=['POST'])
def deny_request(request_id):
    if 'dispatcher_id' not in session:
        return redirect(url_for('main.home'))

    cursor = get_cursor()

    # Mark the request as denied
    cursor.execute("""
        UPDATE LoadRequests
        SET status = 'Denied'
        WHERE request_id = ?
    """, (request_id,))
    get_db().commit()

    return redirect(url_for('main.view_requests'))


@main_bp.route('/dispatcher/requests', methods=['GET'])
def view_requests():
    if 'dispatcher_id' not in session:
        return redirect(url_for('main.home'))

    cursor = get_cursor()

    # Fetch pending requests with broker information
    requests = cursor.execute("""
        SELECT lr.request_id, b.company_name AS broker_company_name, lr.phone_number, lr.origin, lr.destination, lr.load_details
        FROM LoadRequests lr
        JOIN Brokers b ON lr.broker_id = b.broker_id
        WHERE lr.status = 'Pending'
    """).fetchall()

    # Fetch available trucks (no following destination)
    available_trucks = cursor.execute("""
        SELECT t.truck_id, t.make, t.model, d.name AS driver_name, d.phone_number AS driver_phone_number, t.destination_state
        FROM Trucks t
        LEFT JOIN Drivers d ON t.driver_id = d.driver_id
        WHERE t.following_dest_state IS NULL OR t.following_dest_state = ''
    """).fetchall()

    # Fetch approved loads where destination matches the truck's current destination
    approved_loads = cursor.execute("""
        SELECT lr.request_id, b.company_name AS broker_company_name, lr.origin, lr.destination, lr.assigned_truck, d.name AS driver_name, d.phone_number AS driver_phone
        FROM LoadRequests lr
        JOIN Brokers b ON lr.broker_id = b.broker_id
        JOIN Trucks t ON lr.assigned_truck = t.truck_id
        LEFT JOIN Drivers d ON t.driver_id = d.driver_id
        WHERE lr.status = 'Approved' AND lr.destination = t.destination_state
    """).fetchall()

    return render_template('dispatcher/view_requests.html', requests=requests, available_trucks=available_trucks, approved_loads=approved_loads)





@main_bp.route('/dispatcher/requests/assign', methods=['POST'])
def assign_request():
    try:
        request_id = request.form.get('request_id')
        truck_id = request.form.get('truck_id')

        if not request_id or not truck_id:
            raise ValueError("Request ID or Truck ID is missing.")

        cursor = get_cursor()

        # Fetch the destination from the LoadRequest
        load_request = cursor.execute("""
            SELECT destination FROM LoadRequests WHERE request_id = ?
        """, (request_id,)).fetchone()

        if not load_request:
            raise ValueError(f"No LoadRequest found with request_id {request_id}.")

        destination = load_request['destination']

        # Update the LoadRequest with the assigned truck and set the truck's following destination
        cursor.execute("""
            UPDATE LoadRequests
            SET status = 'Approved', assigned_truck = ?
            WHERE request_id = ?
        """, (truck_id, request_id))

        cursor.execute("""
            UPDATE Trucks
            SET following_dest_state = ?
            WHERE truck_id = ?
        """, (destination, truck_id))

        get_db().commit()

    except Exception as e:
        print(f"Error in assign_request: {e}")
        get_db().rollback()

    return redirect(url_for('main.view_requests'))



@main_bp.route('/dispatcher/requests/complete/<int:request_id>', methods=['POST'])
def complete_load(request_id):
    try:
        cursor = get_cursor()

        # Fetch the assigned truck and following destination
        load_request = cursor.execute("""
            SELECT assigned_truck, destination FROM LoadRequests WHERE request_id = ?
        """, (request_id,)).fetchone()

        if not load_request or not load_request['assigned_truck']:
            raise ValueError(f"No assigned truck found for request_id {request_id}.")

        truck_id = load_request['assigned_truck']
        new_destination = load_request['destination']

        # Update the truck's destination and clear the following destination
        cursor.execute("""
            UPDATE Trucks
            SET destination_state = ?, following_dest_state = NULL
            WHERE truck_id = ?
        """, (new_destination, truck_id))

        # Mark the load as completed
        cursor.execute("""
            UPDATE LoadRequests
            SET status = 'Completed'
            WHERE request_id = ?
        """, (request_id,))

        get_db().commit()

    except Exception as e:
        print(f"Error in complete_load: {e}")
        get_db().rollback()

    return redirect(url_for('main.view_requests'))

