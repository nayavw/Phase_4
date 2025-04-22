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
        airport_id = request.form['airport_id']
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        location_id = request.form['location_id']

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.callproc('add_airport', [airport_id, name, city, state, country, location_id])
            conn.commit()
            flash('Airport added successfully!')
        except Exception as e:
            flash(f'Error: {str(e)}')
        finally:
            cursor.close()
            conn.close()
        return redirect('/add_airport')

    return render_template('add_airport.html')

@app.route('/add_person', methods=['GET', 'POST'])
def add_person():
    if request.method == 'POST':
        person_id = request.form['person_id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        location_id = request.form['location_id']  # ✅ This comes earlier now
        tax_id = request.form['tax_id']
        experience = request.form.get('experience') or None
        miles = request.form.get('miles') or None
        funds = request.form.get('funds') or None

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # ✅ Correct argument order:
            cursor.callproc('add_person', [
                person_id,      # 1
                first_name,     # 2
                last_name,      # 3
                location_id,    # 4 ✅ moved up
                tax_id,         # 5
                experience,     # 6
                miles,          # 7
                funds           # 8
            ])

            conn.commit()
            flash('Person added successfully!')
        except Exception as e:
            flash(f'Error: {str(e)}')
        finally:
            cursor.close()
            conn.close()

        return redirect('/add_person')

    return render_template('add_person.html')



@app.route('/add_airplane', methods=['GET', 'POST'])
def add_airplane():
    if request.method == 'POST':
        airline_id = request.form['airline_id']
        tail_num = request.form['tail_num']
        seat_cap = request.form['seat_cap']
        speed = request.form['speed']
        location_id = request.form['location_id']
        plane_type = request.form['plane_type']
        maintained = request.form.get('maintained') or None
        model = request.form.get('model') or None
        is_neo = request.form.get('is_neo') == 'on'

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.callproc('add_airplane', [
                airline_id,     # 1
                tail_num,       # 2
                seat_cap,       # 3
                speed,          # 4
                location_id,    # 5
                plane_type,     # 6
                maintained,     # 7
                model,          # 8
                is_neo          # 9
            ])
            conn.commit()
            flash('Airplane added successfully!')
        except Exception as e:
            flash(f'Error: {str(e)}')
        finally:
            cursor.close()
            conn.close()

        return redirect('/add_airplane')

    return render_template('add_airplane.html')


@app.route('/grant_or_revoke_pilot_license', methods=['GET', 'POST'])
def grant_or_revoke_pilot_license():
    if request.method == 'POST':
        license_type = request.form['license_type']
        person_id = request.form['person_id']

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # ✅ correct argument order
            cursor.callproc('grant_or_revoke_pilot_license', [
                person_id,      # now goes to ip_personID
                license_type    # now goes to ip_license
            ])

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
