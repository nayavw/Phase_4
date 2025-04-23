import re

import mysql
from flask import Flask, render_template, request, redirect, flash
from db.db import get_db_connection
from datetime import datetime

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

        if not airport_id or len(airport_id) != 3:
            flash("Airport ID must be exactly 3 characters.")
            return redirect('/add_airport')
        if not city or not state or not country or not location_id:
            flash("City, state, country, and location ID are required.")
            return redirect('/add_airport')

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM airport WHERE airportID = %s", (airport_id,))
            if cursor.fetchone():
                flash("Airport ID already exists.")
                return redirect('/add_airport')

            cursor.execute("SELECT * FROM location WHERE locationID = %s", (location_id,))
            if cursor.fetchone():
                flash("Location ID is already in use.")
                return redirect('/add_airport')

            cursor.callproc('add_airport', [airport_id, name, city, state, country, location_id])
            conn.commit()
            flash('Airport added successfully!')


        except mysql.connector.Error as err:
            flash(f"Database error: {err.msg}")

        except Exception as e:
            flash(f"An unexpected error occurred: {str(e)}")
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

        experience = int(experience) if experience else None
        miles = int(miles) if miles else None
        funds = float(funds) if funds else None

        if not person_id:
            flash("Person ID is required.")
            return redirect('/add_person')
        if not first_name:
            flash("First name is required.")
            return redirect('/add_person')
        if not location_id:
            flash("Location ID is required.")
            return redirect('/add_person')

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

            cursor.execute("SELECT * FROM person WHERE personID = %s", (person_id,))
            if cursor.fetchone():
                flash("Person ID already exists.")
                return redirect('/add_person')

            cursor.execute("SELECT * FROM location WHERE locationID = %s", (location_id,))
            if not cursor.fetchone():
                flash("Location ID does not exist.")
                return redirect('/add_person')

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


        except mysql.connector.Error as err:
            flash(f"Database error: {err.msg}")

        except Exception as e:
            flash(f"An unexpected error occurred: {str(e)}")
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

        maintained = request.form.get('maintained')
        maintained = maintained.lower() in ['true', 'on', '1'] if maintained else None

        try:
            seat_cap = int(seat_cap)
            speed = int(speed)

            if seat_cap <= 0 or speed <= 0:
                flash("Seat capacity and speed must be greater than 0.")
                return redirect('/add_airplane')

            if "boeing" in plane_type:
                if not model:
                    flash("Boeing planes must have a model specified.")
                    return redirect('/add_airplane')
                if maintained is None:
                    flash("Boeing planes must have the 'maintained' box explicitly checked or left unchecked.")
                    return redirect('/add_airplane')

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM airline WHERE airline_id = %s", (airline_id,))
            if cursor.fetchone()[0] == 0:
                flash("Airline ID does not exist.")
                return redirect('/add_airplane')

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

        except mysql.connector.Error as err:
            flash(f"Database error: {err.msg}")

        except Exception as e:
            flash(f"An unexpected error occurred: {str(e)}")
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

            cursor.callproc('grant_or_revoke_pilot_license', [person_id, license_type])
            conn.commit()
            flash('License granted or revoked successfully!')


        except mysql.connector.Error as err:
            flash(f"Database error: {err.msg}")

        except Exception as e:
            flash(f"An unexpected error occurred: {str(e)}")

        finally:
            cursor.close()
            conn.close()

        return redirect('/grant_or_revoke_pilot_license')

    return render_template('grant_or_revoke_pilot_license.html')


@app.route('/offer_flight', methods=['GET', 'POST'])
def offer_flight():
    if request.method == 'POST':
        flight_id = request.form['flight_id'].strip()
        route_id = request.form['route_id'].strip()
        support_airline = request.form['support_airline'].strip()
        support_tail = request.form['support_tail'].strip()
        progress = request.form['progress'].strip()
        next_time = request.form['next_time'].strip()
        cost = request.form['cost'].strip()

        if not flight_id:
            flash("Flight ID is required.")
            return redirect('/offer_flight')
        if not route_id:
            flash("Route ID is required.")
            return redirect('/offer_flight')
        if not progress.isdigit():
            flash("Progress must be a non-negative integer.")
            return redirect('/offer_flight')
        progress = int(progress)
        if not cost.isdigit():
            flash("Cost must be a non-negative integer.")
            return redirect('/offer_flight')
        cost = int(cost)
        if not next_time:
            flash("Next time is required.")
            return redirect('/offer_flight')

        try:
            datetime.strptime(next_time, '%H:%M:%S')
        except ValueError:
            flash("Next time must be in the correct format.")
            return redirect('/offer_flight')

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM flight WHERE flightID = %s", (flight_id,))
            if cursor.fetchone():
                flash("Flight ID already exists.")
                return redirect('/offer_flight')

            cursor.execute("SELECT * FROM route WHERE routeID = %s", (route_id,))
            if not cursor.fetchone():
                flash("Route ID does not exist.")
                return redirect('/offer_flight')

            cursor.execute("SELECT COUNT(*) AS stop_count FROM route_path WHERE routeID = %s", (route_id,))
            result = cursor.fetchone()
            if result:
                stop_count = result['stop_count']
                if progress < 0 or progress >= stop_count:
                    flash("Progress must be between 0 and the number of stops in the route minus one.")
                    return redirect('/offer_flight')
            else:
                flash("Unable to retrieve route path information.")
                return redirect('/offer_flight')

            if support_airline and support_tail:
                cursor.execute("""SELECT * FROM airplane WHERE airlineID = %s AND tail_num = %s
                """, (support_airline, support_tail))
                if not cursor.fetchone():
                    flash("Specified airplane does not exist.")
                    return redirect('/offer_flight')

                cursor.execute("""
                    SELECT * FROM flight WHERE support_airline = %s AND support_tail = %s""",
                    (support_airline, support_tail))
                if cursor.fetchone():
                    flash("Specified airplane is already assigned to another flight.")
                    return redirect('/offer_flight')
            elif support_airline or support_tail:
                flash("Both support airline and support tail must be provided together.")
                return redirect('/offer_flight')

            cursor.callproc('offer_flight', [
                flight_id,
                route_id,
                support_airline if support_airline else None,
                support_tail if support_tail else None,
                progress,
                next_time,
                cost
            ])
            conn.commit()
            flash('Flight offered successfully!')


        except mysql.connector.Error as err:
            flash(f"Database error: {err.msg}")

        except Exception as e:
            flash(f"An unexpected error occurred: {str(e)}")

        finally:
            cursor.close()
            conn.close()

        return redirect('/offer_flight')

    return render_template('offer_flight.html')


@app.route('/assign_pilot', methods=['GET', 'POST'])
def assign_pilot():
    if request.method == 'POST':
        flight_id = request.form.get('flight_id', '').strip()
        person_id = request.form.get('person_id', '').strip()

        if not flight_id:
            flash("Flight ID is required.")
            return redirect('/assign_pilot')
        if not person_id:
            flash("Pilot Person ID is required.")
            return redirect('/assign_pilot')

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT f.routeID, f.progress, f.support_airline, f.support_tail, a.plane_type, a.locationID AS plane_location
                FROM flight f
                LEFT JOIN airplane a ON f.support_airline = a.airlineID AND f.support_tail = a.tail_num
                WHERE f.flightID = %s AND f.airplane_status = 'on_ground'
            """, (flight_id,))
            flight = cursor.fetchone()
            if not flight:
                flash("Flight does not exist or is not on the ground.")
                return redirect('/assign_pilot')

            cursor.execute("""
                SELECT COUNT(*) AS total_legs
                FROM route_path
                WHERE routeID = %s
            """, (flight['routeID'],))
            route_info = cursor.fetchone()
            if flight['progress'] >= route_info['total_legs']:
                flash("Flight has already completed its route.")
                return redirect('/assign_pilot')

            cursor.execute("""
                SELECT p.personID, pe.locationID AS pilot_location
                FROM pilot p
                JOIN person pe ON p.personID = pe.personID
                WHERE p.personID = %s AND p.commanding_flight IS NULL
            """, (person_id,))
            pilot = cursor.fetchone()
            if not pilot:
                flash("Pilot does not exist or is already assigned to another flight.")
                return redirect('/assign_pilot')

            plane_type = flight['plane_type']
            required_license = 'GENERAL' if not plane_type else plane_type.upper()

            cursor.execute("""
                SELECT 1
                FROM pilot_licenses
                WHERE personID = %s AND UPPER(license) = %s
            """, (person_id, required_license))
            license_check = cursor.fetchone()
            if not license_check:
                flash(f"Pilot does not have the required {required_license} license.")
                return redirect('/assign_pilot')

            if pilot['pilot_location'] != flight['plane_location']:
                flash("Pilot is not at the same location as the airplane.")
                return redirect('/assign_pilot')

            cursor.callproc('assign_pilot', [flight_id, person_id])
            conn.commit()
            flash('Pilot assigned successfully!')


        except mysql.connector.Error as err:
            flash(f"Database error: {err.msg}")
        except Exception as e:
            flash(f"An unexpected error occurred: {str(e)}")
        finally:
            cursor.close()
            conn.close()

        return redirect('/assign_pilot')

    return render_template('assign_pilot.html')


@app.route('/flight_takeoff', methods=['GET', 'POST'])
def flight_takeoff():
    if request.method == 'POST':
        flight_id = request.form['flight_id'].strip()

        if not flight_id:
            flash("Flight ID is required.")
            return redirect('/flight_takeoff')

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT f.flightID, f.progress, COUNT(rp.sequence) AS total_legs
                FROM flight f
                JOIN route_path rp ON f.routeID = rp.routeID
                WHERE f.flightID = %s AND f.airplane_status = 'on_ground'
                GROUP BY f.flightID, f.progress
            """, (flight_id,))
            flight = cursor.fetchone()

            if not flight:
                flash("Flight does not exist or is not on the ground.")
                return redirect('/flight_takeoff')

            if flight['progress'] >= flight['total_legs']:
                flash("Flight has already completed its route.")
                return redirect('/flight_takeoff')

            cursor.execute("""
                SELECT support_airline, support_tail FROM flight
                WHERE flightID = %s AND support_airline IS NOT NULL AND support_tail IS NOT NULL
            """, (flight_id,))
            airplane = cursor.fetchone()

            if not airplane:
                flash("Flight does not have an assigned airplane.")
                return redirect('/flight_takeoff')

            cursor.execute("""
                SELECT a.plane_type FROM airplane a
                JOIN flight f ON a.airlineID = f.support_airline AND a.tail_num = f.support_tail
                WHERE f.flightID = %s
            """, (flight_id,))
            plane = cursor.fetchone()

            if not plane:
                flash("Assigned airplane details not found.")
                return redirect('/flight_takeoff')

            plane_type = plane['plane_type'].strip().upper()

            cursor.execute("""
                SELECT COUNT(*) AS pilot_count FROM pilot
                WHERE commanding_flight = %s
            """, (flight_id,))
            pilot_info = cursor.fetchone()
            pilot_count = pilot_info['pilot_count']

            required_pilots = 2 if plane_type == 'BOEING' else 1

            if pilot_count < required_pilots:
                flash(f"Not enough pilots assigned. {plane_type} requires {required_pilots} pilot(s). Flight will be delayed by 30 minutes.")
                cursor.callproc('flight_takeoff', [flight_id])
                conn.commit()
                return redirect('/flight_takeoff')

            cursor.callproc('flight_takeoff', [flight_id])
            conn.commit()
            flash('Flight took off successfully!')


        except mysql.connector.Error as err:
            flash(f"Database error: {err.msg}")

        except Exception as e:
            flash(f"An unexpected error occurred: {str(e)}")

        finally:
            cursor.close()
            conn.close()

    return render_template('flight_takeoff.html')


@app.route('/flight_landing', methods=['GET', 'POST'])
def flight_landing():
    if request.method == 'POST':
        flight_id = request.form['flight_id'].strip()

        if not flight_id:
            flash("Flight ID is required.")
            return redirect('/flight_landing')

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM flight 
                WHERE flightID = %s AND airplane_status = 'in_flight'
            """, (flight_id,))
            if not cursor.fetchone():
                flash("Flight does not exist or is not currently in flight.")
                return redirect('/flight_landing')

            cursor.callproc('flight_landing', [flight_id])
            conn.commit()
            flash('Flight landed successfully!')


        except mysql.connector.Error as err:
            flash(f"Database error: {err.msg}")

        except Exception as e:
            flash(f"An unexpected error occurred: {str(e)}")

        finally:
            cursor.close()
            conn.close()

        return redirect('/flight_landing')

    return render_template('flight_landing.html')



@app.route('/passengers_board', methods=['GET', 'POST'])
def passengers_board():
    if request.method == 'POST':
        flight_id = request.form.get('flight_id', '').strip()
        if not flight_id:
            flash("Flight ID is required.")
            return redirect('/passengers_board')

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT progress, routeID FROM flight
                WHERE flightID = %s AND airplane_status = 'on_ground'
            """, (flight_id,))
            flight = cursor.fetchone()
            if not flight:
                flash("Flight does not exist or is not on the ground.")
                return redirect('/passengers_board')

            progress = flight['progress']
            route_id = flight['routeID']

            cursor.execute("""
                SELECT COUNT(*) AS total_legs FROM route_path
                WHERE routeID = %s
            """, (route_id,))
            total_legs = cursor.fetchone()['total_legs']
            if progress >= total_legs:
                flash("Flight has completed all legs.")
                return redirect('/passengers_board')

            cursor.callproc('passengers_board', [flight_id])
            conn.commit()
            flash('Passengers boarded successfully!')

        except mysql.connector.Error as err:
            flash(f"Database error: {err.msg}")
        except Exception as e:
            flash(f"An unexpected error occurred: {str(e)}")
        finally:
            cursor.close()
            conn.close()

        return redirect('/passengers_board')

    return render_template('passengers_board.html')



@app.route('/passengers_disembark', methods=['GET', 'POST'])
def passengers_disembark():
    if request.method == 'POST':
        flight_id = request.form['flight_id'].strip()

        if not flight_id:
            flash("Flight ID is required.")
            return redirect('/passengers_disembark')

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT airplane_status FROM flight
                WHERE flightID = %s
            """, (flight_id,))
            flight = cursor.fetchone()

            if not flight:
                flash("Flight ID does not exist.")
                return redirect('/passengers_disembark')

            if flight['airplane_status'] != 'on_ground':
                flash("Flight must be on the ground to disembark passengers.")
                return redirect('/passengers_disembark')

            cursor.callproc('passengers_disembark', [flight_id])
            conn.commit()
            flash('Passengers disembarked successfully!')

        except mysql.connector.Error as err:
            flash(f"Database error: {err.msg}")
        except Exception as e:
            flash(f"An unexpected error occurred: {str(e)}")
        finally:
            cursor.close()
            conn.close()

        return redirect('/passengers_disembark')

    return render_template('passengers_disembark.html')


@app.route('/recycle_crew', methods=['GET', 'POST'])
def recycle_crew():
    if request.method == 'POST':
        flight_id = request.form['flight_id'].strip()

        if not flight_id:
            flash("Flight ID is required.")
            return redirect('/recycle_crew')

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT * FROM flight WHERE flightID = %s", (flight_id,))
            flight = cursor.fetchone()
            if not flight:
                flash("Flight ID does not exist.")
                return redirect('/recycle_crew')

            if flight['airplane_status'].lower() != 'on_ground':
                flash("Flight must be on the ground to recycle crew.")
                return redirect('/recycle_crew')

            cursor.execute("SELECT COUNT(*) AS total_legs FROM route_path WHERE routeID = %s", (flight['routeID'],))
            total_legs_result = cursor.fetchone()
            total_legs = total_legs_result['total_legs'] if total_legs_result else 0

            if flight['progress'] < total_legs:
                flash("Flight has not completed all legs of its route.")
                return redirect('/recycle_crew')

            cursor.execute("""
                SELECT l.arrival
                FROM route_path rp
                JOIN leg l ON rp.legID = l.legID
                WHERE rp.routeID = %s AND rp.sequence = %s
                LIMIT 1
            """, (flight['routeID'], total_legs))
            arrival_result = cursor.fetchone()
            if not arrival_result:
                flash("Unable to determine arrival airport.")
                return redirect('/recycle_crew')
            arrival_airport = arrival_result['arrival']

            cursor.execute("SELECT locationID FROM airport WHERE airportID = %s", (arrival_airport,))
            location_result = cursor.fetchone()
            if not location_result:
                flash("Arrival airport location not found.")
                return redirect('/recycle_crew')
            arrival_location = location_result['locationID']

            cursor.execute("""
                SELECT COUNT(*) AS passenger_count
                FROM passenger ps
                JOIN person p ON ps.personID = p.personID
                WHERE p.locationID = %s
            """, (arrival_location,))
            passenger_count_result = cursor.fetchone()
            passenger_count = passenger_count_result['passenger_count'] if passenger_count_result else 0

            if passenger_count > 0:
                flash("Passengers are still present at the arrival location.")
                return redirect('/recycle_crew')

            cursor.execute("""
                UPDATE person p
                JOIN pilot pl ON p.personID = pl.personID
                SET p.locationID = %s
                WHERE pl.commanding_flight = %s
            """, (arrival_location, flight_id))

            cursor.execute("""
                UPDATE pilot
                SET commanding_flight = NULL
                WHERE commanding_flight = %s
            """, (flight_id,))

            conn.commit()
            flash('Crew recycled successfully.')

        except Exception as e:
            flash(f"An error occurred: {str(e)}")
        finally:
            cursor.close()
            conn.close()

        return redirect('/recycle_crew')

    return render_template('recycle_crew.html')



@app.route('/retire_flight', methods=['GET', 'POST'])
def retire_flight():
    if request.method == 'POST':
        flight_id = request.form['flight_id'].strip()

        if not flight_id:
            flash("Flight ID is required.")
            return redirect('/retire_flight')

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT * FROM flight WHERE flightID = %s", (flight_id,))
            flight = cursor.fetchone()
            if not flight:
                flash("Flight ID does not exist.")
                return redirect('/retire_flight')

            if flight['airplane_status'] != 'on_ground':
                flash("Flight must be on the ground to be retired.")
                return redirect('/retire_flight')

            cursor.execute("SELECT COUNT(*) AS total_legs FROM route_path WHERE routeID = %s", (flight['routeID'],))
            result = cursor.fetchone()
            total_legs = result['total_legs'] if result else 0

            if flight['progress'] != 0 and flight['progress'] != total_legs:
                flash("Flight must be at the start or end of its route to be retired.")
                return redirect('/retire_flight')

            cursor.execute("""
                SELECT COUNT(*) AS passenger_count
                FROM passenger ps
                JOIN person p ON ps.personID = p.personID
                WHERE p.locationID = (
                    SELECT locationID FROM airplane
                    WHERE airlineID = %s AND tail_num = %s
                    LIMIT 1
                )
            """, (flight['support_airline'], flight['support_tail']))
            result = cursor.fetchone()
            if result and result['passenger_count'] > 0:
                flash("All passengers must have disembarked before retiring the flight.")
                return redirect('/retire_flight')

            cursor.execute("SELECT COUNT(*) AS pilot_count FROM pilot WHERE commanding_flight = %s", (flight_id,))
            result = cursor.fetchone()
            if result and result['pilot_count'] > 0:
                flash("All pilots must be unassigned before retiring the flight.")
                return redirect('/retire_flight')

            cursor.callproc('retire_flight', [flight_id])
            conn.commit()
            flash("Flight retired successfully!")

        except mysql.connector.Error as err:
            flash(f"Database error: {err.msg}")
        except Exception as e:
            flash(f"An unexpected error occurred: {str(e)}")
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

        except mysql.connector.Error as err:
            flash(f"Database error: {err.msg}")

        except Exception as e:
            flash(f"An unexpected error occurred: {str(e)}")
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
