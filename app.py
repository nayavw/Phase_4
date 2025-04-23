from flask import Flask, render_template, request, redirect, flash
from db.db import get_db_connection

app = Flask(__name__)
app.secret_key = 'sams_secret'

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/add_airport', methods=['GET', 'POST'])
def add_airport():
    if request.method == 'POST':
        airport_id = request.form['airport_id'].strip()
        name = request.form['name'].strip()
        city = request.form['city'].strip()
        state = request.form['state'].strip()
        country = request.form['country'].strip()
        location_id = request.form['location_id'].strip()

        # Basic validation before hitting the DB
        if not airport_id or len(airport_id) != 3:
            flash("Airport ID must be exactly 3 characters.")
            return redirect('/add_airport')
        if not city or not state or not country or not location_id:
            flash("City, state, country, and location ID are required.")
            return redirect('/add_airport')

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Check if airport ID already exists
            cursor.execute("SELECT 1 FROM airport WHERE airportID = %s", (airport_id,))
            if cursor.fetchone():
                flash("Airport ID already exists.")
                return redirect('/add_airport')

            # Check if location ID already exists
            cursor.execute("SELECT 1 FROM location WHERE locationID = %s", (location_id,))
            if cursor.fetchone():
                flash("Location ID is already in use.")
                return redirect('/add_airport')

            # Call the stored procedure if all validations pass
            cursor.callproc('add_airport', [airport_id, name, city, state, country, location_id])
            conn.commit()
            flash('Airport added successfully!')
        except Exception as e:
            flash(f'Unexpected Error: {str(e)}')
        finally:
            cursor.close()
            conn.close()
        return redirect('/add_airport')

    return render_template('add_airport.html')


@app.route('/add_person', methods=['GET', 'POST'])
def add_person():
    if request.method == 'POST':
        person_id = request.form['person_id'].strip()
        first_name = request.form['first_name'].strip()
        last_name = request.form['last_name'].strip()
        location_id = request.form['location_id'].strip()
        tax_id = request.form['tax_id'].strip()
        experience = request.form.get('experience')
        miles = request.form.get('miles')
        funds = request.form.get('funds')

        # Normalize optional integers
        experience = int(experience) if experience else None
        miles = int(miles) if miles else None
        funds = float(funds) if funds else None

        # Step 1: Basic validation
        if not person_id:
            flash("Person ID is required.")
            return redirect('/add_person')
        if not first_name:
            flash("First name is required.")
            return redirect('/add_person')
        if not location_id:
            flash("Location ID is required.")
            return redirect('/add_person')

        # Step 2: Check that roles are mutually exclusive and complete
        is_pilot = tax_id or experience is not None
        is_passenger = miles is not None or funds is not None

        if is_pilot and is_passenger:
            flash("A person cannot be both a pilot and a passenger.")
            return redirect('/add_person')

        if not is_pilot or not is_passenger:
            flash("A person must be a pilot or a passenger.")
            return redirect('/add_person')

        if (tax_id and experience is None) or (not tax_id and experience is not None):
            flash("Pilot must have both Tax ID and Experience.")
            return redirect('/add_person')

        if (miles is not None and funds is None) or (miles is None and funds is not None):
            flash("Passenger must have both Miles and Funds.")
            return redirect('/add_person')

        if experience is not None and experience < 0:
            flash("Experience must be non-negative.")
            return redirect('/add_person')

        if miles is not None and miles < 0:
            flash("Miles must be non-negative.")
            return redirect('/add_person')

        if funds is not None and funds < 0:
            flash("Funds must be non-negative.")
            return redirect('/add_person')

        if tax_id:
            tax_id_pattern = r'^\d{3}-\d{2}-\d{4}$'
            if not re.match(tax_id_pattern, tax_id):
                flash("Tax ID is in the wrong format.")
                return redirect('/add_person')

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Check if person ID already exists
            cursor.execute("SELECT * FROM person WHERE personID = %s", (person_id,))
            if cursor.fetchone():
                flash("Person ID already exists.")
                return redirect('/add_person')

            # Check if location ID exists
            cursor.execute("SELECT * FROM location WHERE locationID = %s", (location_id,))
            if not cursor.fetchone():
                flash("Location ID does not exist.")
                return redirect('/add_person')

            # Call the procedure
            cursor.callproc('add_person', [
                person_id,
                first_name,
                last_name,
                location_id,
                tax_id if tax_id else None,
                experience,
                miles,
                funds
            ])
            conn.commit()
            flash('Person added successfully!')

        except Exception as e:
            flash(f'Unexpected error: {str(e)}')
        finally:
            cursor.close()
            conn.close()

        return redirect('/add_person')

    return render_template('add_person.html')


@app.route('/add_airplane', methods=['GET', 'POST'])
def add_airplane():
    if request.method == 'POST':
        airline_id = request.form['airline_id']
        tail_num = request.form['tail_num'].strip()
        seat_cap = request.form['seat_cap']
        speed = request.form['speed']
        location_id = request.form['location_id'].strip()
        plane_type = request.form['plane_type'].strip().lower()
        model = request.form.get('model') or None
        is_neo = request.form.get('is_neo') == 'on'

        # Boolean checkbox: will be present if checked
        maintained = request.form.get('maintained')
        maintained = maintained.lower() in ['true', 'on', '1'] if maintained else None

        try:
            seat_cap = int(seat_cap)
            speed = int(speed)

            if seat_cap <= 0 or speed <= 0:
                flash("Seat capacity and speed must be greater than 0.")
                return redirect('/add_airplane')

            # Boeing-specific validation
            if "boeing" in plane_type:
                if not model:
                    flash("Boeing planes must have a model specified.")
                    return redirect('/add_airplane')
                if maintained is None:
                    flash("Boeing planes must have the 'maintained' box explicitly checked or left unchecked.")
                    return redirect('/add_airplane')

            conn = get_db_connection()
            cursor = conn.cursor()

            # Check if airline exists
            cursor.execute("SELECT COUNT(*) FROM airline WHERE airline_id = %s", (airline_id,))
            if cursor.fetchone()[0] == 0:
                flash("Airline ID does not exist.")
                return redirect('/add_airplane')

            # Check if location is already used
            cursor.execute("SELECT COUNT(*) FROM location WHERE location_id = %s", (location_id,))
            if cursor.fetchone()[0] > 0:
                flash("Location ID already in use.")
                return redirect('/add_airplane')

            cursor.callproc('add_airplane', [
                airline_id,
                tail_num,
                seat_cap,
                speed,
                location_id,
                plane_type,
                maintained,
                model,
                is_neo
            ])
            conn.commit()
            flash('Airplane added successfully!')

        except ValueError:
            flash("Seat capacity and speed must be integers.")
        except Exception as e:
            flash(f"Error: {str(e)}")
        finally:
            cursor.close()
            conn.close()

        return redirect('/add_airplane')

    return render_template('add_airplane.html')



@app.route('/grant_or_revoke_pilot_license', methods=['GET', 'POST'])
def grant_or_revoke_pilot_license():
    if request.method == 'POST':
        license_type = request.form['license_type'].strip()
        person_id = request.form['person_id'].strip()

        if not person_id:
            flash("Person ID is required.")
            return redirect('/grant_or_revoke_pilot_license')
        if not license_type:
            flash("License type is required.")
            return redirect('/grant_or_revoke_pilot_license')

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM pilot WHERE personID = %s", (person_id,))
            if not cursor.fetchone():
                flash("Person ID does not exist or is not a pilot.")
                return redirect('/grant_or_revoke_pilot_license')

            # Step 3: Call the stored procedure
            cursor.callproc('grant_or_revoke_pilot_license', [person_id, license_type])
            conn.commit()
            flash('License granted or revoked successfully!')

        except Exception as e:
            flash(f'Error: {str(e)}')
        finally:
            cursor.close()
            conn.close()

        return redirect('/grant_or_revoke_pilot_license')

    return render_template('grant_or_revoke_pilot_license.html')


@app.route('/offer_flight', methods=['GET', 'POST'])
def offer_flight():
    if request.method == 'POST':
        flight_id = request.form['flight_id']
        route_id = request.form['route_id']
        support_airline = request.form['support_airline']
        support_tail = request.form['support_tail']
        progress = request.form['progress']
        next_time = request.form['next_time']
        cost = request.form['cost']

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.callproc('offer_flight', [
                flight_id,
                route_id,
                support_airline,
                support_tail,
                progress,
                next_time,
                cost
            ])
            conn.commit()
            flash('Flight offered successfully!')
        except Exception as e:
            flash(f'Error: {str(e)}')
        finally:
            cursor.close()
            conn.close()

        return redirect('/offer_flight')

    return render_template('offer_flight.html')


@app.route('/assign_pilot', methods=['GET', 'POST'])
def assign_pilot():
    if request.method == 'POST':
        flight_id = request.form['flight_id']
        person_id = request.form['person_id']

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.callproc('assign_pilot', [flight_id, person_id])
            conn.commit()
            flash('Pilot assigned successfully!')
        except Exception as e:
            flash(f'Error: {str(e)}')
        finally:
            cursor.close()
            conn.close()

        return redirect('/assign_pilot')

    return render_template('assign_pilot.html')


@app.route('/flight_takeoff', methods=['GET', 'POST'])
def flight_takeoff():
    if request.method == 'POST':
        flight_id = request.form['flight_id']

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.callproc('flight_takeoff', [flight_id])
            conn.commit()
            flash('Flight took off successfully!')
        except Exception as e:
            flash(f'Error: {str(e)}')
        finally:
            cursor.close()
            conn.close()

        return redirect('/flight_takeoff')

    return render_template('flight_takeoff.html')


@app.route('/flight_landing', methods=['GET', 'POST'])
def flight_landing():
    if request.method == 'POST':
        flight_id = request.form['flight_id']

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.callproc('flight_landing', [flight_id])
            conn.commit()
            flash('Flight landed successfully!')
        except Exception as e:
            flash(f'Error: {str(e)}')
        finally:
            cursor.close()
            conn.close()

        return redirect('/flight_landing')

    return render_template('flight_landing.html')


@app.route('/passengers_board', methods=['GET', 'POST'])
def passengers_board():
    if request.method == 'POST':
        flight_id = request.form['flight_id']

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.callproc('passengers_board', [flight_id])
            conn.commit()
            flash('Passengers boarded successfully!')
        except Exception as e:
            flash(f'Error: {str(e)}')
        finally:
            cursor.close()
            conn.close()

        return redirect('/passengers_board')

    return render_template('passengers_board.html')


@app.route('/passengers_disembark', methods=['GET', 'POST'])
def passengers_disembark():
    if request.method == 'POST':
        flight_id = request.form['flight_id']

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.callproc('passengers_disembark', [flight_id])
            conn.commit()
            flash('Passengers disembarked successfully!')
        except Exception as e:
            flash(f'Error: {str(e)}')
        finally:
            cursor.close()
            conn.close()

        return redirect('/passengers_disembark')

    return render_template('passengers_disembark.html')


@app.route('/recycle_crew', methods=['GET', 'POST'])
def recycle_crew():
    if request.method == 'POST':
        flight_id = request.form['flight_id']

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.callproc('recycle_crew', [flight_id])
            conn.commit()
            flash('Crew recycled successfully!')
        except Exception as e:
            flash(f'Error: {str(e)}')
        finally:
            cursor.close()
            conn.close()

        return redirect('/recycle_crew')

    return render_template('recycle_crew.html')


@app.route('/retire_flight', methods=['GET', 'POST'])
def retire_flight():
    if request.method == 'POST':
        flight_id = request.form['flight_id']

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.callproc('retire_flight', [flight_id])
            conn.commit()
            flash('Flight retired successfully!')
        except Exception as e:
            flash(f'Error: {str(e)}')
        finally:
            cursor.close()
            conn.close()

        return redirect('/retire_flight')

    return render_template('retire_flight.html')


@app.route('/simulation_cycle', methods=['GET', 'POST'])
def simulation_cycle():
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.callproc('simulation_cycle')
            conn.commit()
            flash('Simulation cycle executed successfully!')
        except Exception as e:
            flash(f'Error: {str(e)}')
        finally:
            cursor.close()
            conn.close()

        return redirect('/simulation_cycle')

    return render_template('simulation_cycle.html')


@app.route('/flights_in_the_air')
def flights_in_the_air():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM flights_in_the_air')

        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        return render_template('flights_in_the_air.html', rows=results, columns=columns)

    except Exception as e:
        flash(f'Error: {str(e)}')
        return render_template('flights_in_the_air.html', rows=[], columns=[])

    finally:
        cursor.close()
        conn.close()


@app.route('/flights_on_the_ground')
def flights_on_the_ground():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM flights_on_the_ground')
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        return render_template('flights_on_the_ground.html', rows=rows, columns=columns)

    except Exception as e:
        flash(f'Error: {str(e)}')
        return render_template('flights_on_the_ground.html', rows=[], columns=[])

    finally:
        cursor.close()
        conn.close()



@app.route('/people_in_the_air')
def people_in_the_air():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM people_in_the_air')
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        return render_template('people_in_the_air.html', rows=rows, columns=columns)

    except Exception as e:
        flash(f'Error: {str(e)}')
        return render_template('people_in_the_air.html', rows=[], columns=[])

    finally:
        cursor.close()
        conn.close()



@app.route('/people_on_the_ground')
def people_on_the_ground():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM people_on_the_ground')
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        return render_template('people_on_the_ground.html', rows=rows, columns=columns)

    except Exception as e:
        flash(f'Error: {str(e)}')
        return render_template('people_on_the_ground.html', rows=[], columns=[])

    finally:
        cursor.close()
        conn.close()



@app.route('/route_summary')
def route_summary():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM route_summary')
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        return render_template('route_summary.html', rows=rows, columns=columns)

    except Exception as e:
        flash(f'Error: {str(e)}')
        return render_template('route_summary.html', rows=[], columns=[])

    finally:
        cursor.close()
        conn.close()



@app.route('/alternative_airports')
def alternative_airports():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM alternative_airports')
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        return render_template('alternative_airports.html', rows=rows, columns=columns)

    except Exception as e:
        flash(f'Error: {str(e)}')
        return render_template('alternative_airports.html', rows=[], columns=[])

    finally:
        cursor.close()
        conn.close()



@app.route('/top_frequent_fliers')
def top_frequent_fliers():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM top_frequent_fliers')
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        return render_template('top_frequent_fliers.html', rows=rows, columns=columns)

    except Exception as e:
        flash(f'Error: {str(e)}')
        return render_template('top_frequent_fliers.html', rows=[], columns=[])

    finally:
        cursor.close()
        conn.close()
