-- CS4400: Introduction to Database Systems: Monday, March 3, 2025
-- Simple Airline Management System Course Project Mechanics [TEMPLATE] (v0)
-- Views, Functions & Stored Procedures

/* This is a standard preamble for most of our scripts.  The intent is to establish
a consistent environment for the database behavior. */
set global transaction isolation level serializable;
set global SQL_MODE = 'ANSI,TRADITIONAL';
set names utf8mb4;
set SQL_SAFE_UPDATES = 0;

set @thisDatabase = 'flight_tracking';
use flight_tracking;
-- -----------------------------------------------------------------------------
-- stored procedures and views
-- -----------------------------------------------------------------------------
/* Standard Procedure: If one or more of the necessary conditions for a procedure to
be executed is false, then simply have the procedure halt execution without changing
the database state. Do NOT display any error messages, etc. */

-- [_] supporting functions, views and stored procedures
-- -----------------------------------------------------------------------------
/* Helpful library capabilities to simplify the implementation of the required
views and procedures. */
-- -----------------------------------------------------------------------------
drop function if exists leg_time;
delimiter //
create function leg_time (ip_distance integer, ip_speed integer)
	returns time reads sql data
begin
	declare total_time decimal(10,2);
    declare hours, minutes integer default 0;
    set total_time = ip_distance / ip_speed;
    set hours = truncate(total_time, 0);
    set minutes = truncate((total_time - hours) * 60, 0);
    return maketime(hours, minutes, 0);
end //
delimiter ;

-- [1] add_airplane()
-- -----------------------------------------------------------------------------
/* This stored procedure creates a new airplane.  A new airplane must be sponsored
by an existing airline, and must have a unique tail number for that airline.
username.  An airplane must also have a non-zero seat capacity and speed. An airplane
might also have other factors depending on it's type, like the model and the engine.  
Finally, an airplane must have a new and database-wide unique location
since it will be used to carry passengers. */
-- -----------------------------------------------------------------------------
drop procedure if exists add_airplane;
delimiter //
create procedure add_airplane (in ip_airlineID varchar(50), in ip_tail_num varchar(50),
	in ip_seat_capacity integer, in ip_speed integer, in ip_locationID varchar(50),
    in ip_plane_type varchar(100), in ip_maintenanced boolean, in ip_model varchar(50),
    in ip_neo boolean)
sp_main: begin

	-- Ensure that the plane type is valid: Boeing, Airbus, or neither
    -- Ensure that the type-specific attributes are accurate for the type
    -- Ensure that the airplane and location values are new and unique
    -- Add airplane and location into respective tables


    if ip_airlineID is null or TRIM(ip_airlineID) = '' 
       or ip_tail_num is null or TRIM(ip_tail_num) = ''
       or ip_locationID is null or TRIM(ip_locationID) = ''
       or ip_seat_capacity is null or ip_speed is null then
         leave sp_main;
    end if;
    
    if ip_seat_capacity <= 0 or ip_speed <= 0 then
         leave sp_main;
    end if;
    
    if not exists(select * from airline where airlineID = TRIM(ip_airlineID)) then
         leave sp_main;
    end if;
    
    if exists(select * from airplane 
              where airlineID = TRIM(ip_airlineID) 
                and tail_num = TRIM(ip_tail_num)) then
         leave sp_main;
    end if;
    
    if exists(select * from location where locationID = TRIM(ip_locationID)) then
         leave sp_main;
    end if;
    
    if ip_plane_type is null or TRIM(ip_plane_type) = '' then
         if ip_model is not null or ip_neo is not null then
              leave sp_main;
         end if;
    else
         if UPPER(TRIM(ip_plane_type)) = 'BOEING' then
              if ip_model is null or TRIM(ip_model) = '' or ip_neo is not null then
                   leave sp_main;
              end if;
         elseif UPPER(TRIM(ip_plane_type)) = 'AIRBUS' then
              if ip_neo is null then
                   leave sp_main;
              end if;
              if ip_model is not null and TRIM(ip_model) <> '' then
                   leave sp_main;
              end if;
         else
              if (ip_model is not null and TRIM(ip_model) <> '') or ip_neo is not null then
                   leave sp_main;
              end if;
         end if;
    end if;
    
    insert into location (locationID) values (TRIM(ip_locationID));
    insert into airplane (
        airlineID, tail_num, seat_capacity, speed,
        locationID, plane_type, maintenanced, model, neo
    ) values (
        TRIM(ip_airlineID), TRIM(ip_tail_num), ip_seat_capacity, ip_speed,
        TRIM(ip_locationID), TRIM(ip_plane_type), ip_maintenanced, ip_model, ip_neo
    );
    
end //
delimiter ;

-- [2] add_airport()
-- -----------------------------------------------------------------------------
/* This stored procedure creates a new airport.  A new airport must have a unique
identifier along with a new and database-wide unique location if it will be used
to support airplane takeoffs and landings.  An airport may have a longer, more
descriptive name.  An airport must also have a city, state, and country designation. */
-- -----------------------------------------------------------------------------
drop procedure if exists add_airport;
delimiter //
create procedure add_airport (in ip_airportID char(3), in ip_airport_name varchar(200),
    in ip_city varchar(100), in ip_state varchar(100), in ip_country char(3), in ip_locationID varchar(50))
sp_main: begin

    if ip_airportID is null or TRIM(ip_airportID) = '' or LENGTH(TRIM(ip_airportID)) <> 3
       or ip_city is null or TRIM(ip_city) = ''
       or ip_state is null or TRIM(ip_state) = ''
       or ip_country is null or TRIM(ip_country) = ''
       or ip_locationID is null or TRIM(ip_locationID) = '' then
         leave sp_main;
    end if;
    
    if exists(select * from airport where airportID = TRIM(ip_airportID)) then
         leave sp_main;
    end if;
    if exists(select * from location where locationID = TRIM(ip_locationID)) then
         leave sp_main;
    end if;
    
    insert into location (locationID) values (TRIM(ip_locationID));
    insert into airport (airportID, airport_name, city, state, country, locationID)
    values (TRIM(ip_airportID), ip_airport_name, TRIM(ip_city), TRIM(ip_state), TRIM(ip_country), TRIM(ip_locationID));
end //
delimiter ;


-- [3] add_person()
-- -----------------------------------------------------------------------------
/* This stored procedure creates a new person.  A new person must reference a unique
identifier along with a database-wide unique location used to determine where the
person is currently located: either at an airport, or on an airplane, at any given
time.  A person must have a first name, and might also have a last name.

A person can hold a pilot role or a passenger role (exclusively).  As a pilot,
a person must have a tax identifier to receive pay, and an experience level.  As a
passenger, a person will have some amount of frequent flyer miles, along with a
certain amount of funds needed to purchase tickets for flights. */
-- -----------------------------------------------------------------------------
drop procedure if exists add_person;
delimiter //
create procedure add_person (in ip_personID varchar(50), in ip_first_name varchar(100),
    in ip_last_name varchar(100), in ip_locationID varchar(50), in ip_taxID varchar(50),
    in ip_experience integer, in ip_miles integer, in ip_funds integer)
sp_main: begin

    if ip_personID is null or TRIM(ip_personID) = '' 
       or ip_first_name is null or TRIM(ip_first_name) = '' 
       or ip_locationID is null or TRIM(ip_locationID) = '' then
         leave sp_main;
    end if;
    
    if not exists(select * from location where locationID = TRIM(ip_locationID)) then
         leave sp_main;
    end if;
    
    if exists(select * from person where personID = TRIM(ip_personID)) then
         leave sp_main;
    end if;
    
    if ((ip_taxID is not null or ip_experience is not null) and (ip_miles is not null or ip_funds is not null)) then
         leave sp_main;
    end if;
    if ( (ip_taxID is not null and ip_experience is null) or (ip_taxID is null and ip_experience is not null) ) then
         leave sp_main;
    end if;
    if ( (ip_miles is not null and ip_funds is null) or (ip_miles is null and ip_funds is not null) ) then
         leave sp_main;
    end if;
    
    if ip_experience is not null and ip_experience < 0 then
         leave sp_main;
    end if;
    if ip_miles is not null and ip_miles < 0 then
         leave sp_main;
    end if;
    if ip_funds is not null and ip_funds < 0 then
         leave sp_main;
    end if;
    
    insert into person (personID, first_name, last_name, locationID)
    values (TRIM(ip_personID), TRIM(ip_first_name), ip_last_name, TRIM(ip_locationID));
    
    if ip_taxID is not null and ip_experience is not null then
         if TRIM(ip_taxID) = '' then
             leave sp_main;
         end if;
         insert into pilot (personID, taxID, experience)
         values (TRIM(ip_personID), TRIM(ip_taxID), ip_experience);
    end if;
    
    if ip_miles is not null and ip_funds is not null then
         insert into passenger (personID, miles, funds)
         values (TRIM(ip_personID), ip_miles, ip_funds);
    end if;
    
end //
delimiter ;

-- [4] grant_or_revoke_pilot_license()
-- -----------------------------------------------------------------------------
/* This stored procedure inverts the status of a pilot license.  If the license
doesn't exist, it must be created; and, if it aready exists, then it must be removed. */
-- -----------------------------------------------------------------------------
drop procedure if exists grant_or_revoke_pilot_license;
delimiter //
create procedure grant_or_revoke_pilot_license (in ip_personID varchar(50), in ip_license varchar(100))
sp_main: begin

    if ip_personID is null or TRIM(ip_personID) = '' 
       or ip_license is null or TRIM(ip_license) = '' then
        leave sp_main;
    end if;
    
    if not exists(select * from pilot where personID = TRIM(ip_personID)) then
        leave sp_main;
    end if;
    
    if exists(select * from pilot_licenses 
              where personID = TRIM(ip_personID) 
                and license = TRIM(ip_license)) then
        delete from pilot_licenses 
        where personID = TRIM(ip_personID) and license = TRIM(ip_license);
    else
        insert into pilot_licenses (personID, license)
        values (TRIM(ip_personID), TRIM(ip_license));
    end if;
end //
delimiter ;

-- [5] offer_flight()
-- -----------------------------------------------------------------------------
/* This stored procedure creates a new flight.  The flight can be defined before
an airplane has been assigned for support, but it must have a valid route.  And
the airplane, if designated, must not be in use by another flight.  The flight
can be started at any valid location along the route except for the final stop,
and it will begin on the ground.  You must also include when the flight will
takeoff along with its cost. */
-- -----------------------------------------------------------------------------
drop procedure if exists offer_flight;
delimiter //
create procedure offer_flight (in ip_flightID varchar(50), in ip_routeID varchar(50),
    in ip_support_airline varchar(50), in ip_support_tail varchar(50), in ip_progress integer,
    in ip_next_time time, in ip_cost integer)
sp_main: begin

	-- Ensure that the airplane exists
    -- Ensure that the route exists
    -- Ensure that the progress is less than the length of the route
    -- Create the flight with the airplane starting in on the ground
    
    if ip_flightID is null or TRIM(ip_flightID) = '' 
       or ip_routeID is null or TRIM(ip_routeID) = '' 
       or ip_next_time is null 
       or ip_progress is null 
       or ip_cost is null then
        leave sp_main;
    end if;
    
    if ip_cost < 0 then
        leave sp_main;
    end if;
    
    if not exists(select * from route where routeID = TRIM(ip_routeID)) then
        leave sp_main;
    end if;
    
    if exists(select * from flight where flightID = TRIM(ip_flightID)) then
        leave sp_main;
    end if;
    
    if ip_progress < 0 
       or ip_progress >= (select count(*) from route_path where routeID = TRIM(ip_routeID)) then
        leave sp_main;
    end if;
    
    if ip_support_airline is not null and ip_support_tail is not null then
        if TRIM(ip_support_airline) = '' or TRIM(ip_support_tail) = '' then
            leave sp_main;
        end if;
        if not exists(select * from airplane 
                      where airlineID = TRIM(ip_support_airline) 
                        and tail_num = TRIM(ip_support_tail)) then
            leave sp_main;
        end if;
        if exists(select * from flight 
                  where support_airline = TRIM(ip_support_airline) 
                    and support_tail = TRIM(ip_support_tail)) then
            leave sp_main;
        end if;
    end if;
    
    insert into flight (
        flightID, routeID, support_airline, support_tail, progress, airplane_status, next_time, cost
    )
    values (
        TRIM(ip_flightID), TRIM(ip_routeID), 
        case when ip_support_airline is not null then TRIM(ip_support_airline) else null end,
        case when ip_support_tail is not null then TRIM(ip_support_tail) else null end,
        ip_progress, 'on_ground', ip_next_time, ip_cost
    );
end //
delimiter ;

-- [6] flight_landing()
-- -----------------------------------------------------------------------------
/* This stored procedure updates the state for a flight landing at the next airport
along it's route.  The time for the flight should be moved one hour into the future
to allow for the flight to be checked, refueled, restocked, etc. for the next leg
of travel.  Also, the pilots of the flight should receive increased experience, and
the passengers should have their frequent flyer miles updated. */
-- -----------------------------------------------------------------------------
drop procedure if exists flight_landing;
delimiter //
create procedure flight_landing (in ip_flightID varchar(50))
sp_main: begin

	-- Ensure that the flight exists
    -- Ensure that the flight is in the air
    
    -- Increment the pilot's experience by 1
    -- Increment the frequent flyer miles of all passengers on the plane
    -- Update the status of the flight and increment the next time to 1 hour later
		-- Hint: use addtime()
        
    declare leg_distance int;

    if ip_flightID is null or TRIM(ip_flightID) = '' then
        leave sp_main;
    end if;
    
    if not exists(select * from flight 
                  where flightID = TRIM(ip_flightID) 
                    and airplane_status = 'in_flight') then
        leave sp_main;
    end if;
    
    select l.distance into leg_distance
    from flight f
    join route_path rp on f.routeID = rp.routeID and rp.sequence = f.progress
    join leg l on rp.legID = l.legID
    where f.flightID = TRIM(ip_flightID);
    
    if leg_distance is null or leg_distance <= 0 then
        leave sp_main;
    end if;
    
    update pilot
    set experience = experience + 1
    where commanding_flight = TRIM(ip_flightID);
    
    update passenger
    set miles = miles + leg_distance
    where personID in (
        select p.personID
        from flight f
        join airplane a on f.support_airline = a.airlineID and f.support_tail = a.tail_num
        join person p on p.locationID = a.locationID
        where f.flightID = TRIM(ip_flightID)
    );
    
    update flight
    set airplane_status = 'on_ground',
        next_time = addtime(next_time, '01:00:00')
    where flightID = TRIM(ip_flightID);
end //
delimiter ;

-- [7] flight_takeoff()
-- -----------------------------------------------------------------------------
/* This stored procedure updates the state for a flight taking off from its current
airport towards the next airport along it's route.  The time for the next leg of
the flight must be calculated based on the distance and the speed of the airplane.
And we must also ensure that Airbus and general planes have at least one pilot
assigned, while Boeing must have a minimum of two pilots. If the flight cannot take
off because of a pilot shortage, then the flight must be delayed for 30 minutes. */
-- -----------------------------------------------------------------------------
drop procedure if exists flight_takeoff;
delimiter //
create procedure flight_takeoff (in ip_flightID varchar(50))
sp_main: begin

	-- Ensure that the flight exists
    -- Ensure that the flight is on the ground
    -- Ensure that the flight has another leg to fly
    -- Ensure that there are enough pilots (1 for Airbus and general, 2 for Boeing)
		-- If there are not enough, move next time to 30 minutes later
        
	-- Increment the progress and set the status to in flight
    -- Calculate the flight time using the speed of airplane and distance of leg
    -- Update the next time using the flight time
    
   declare leg_distance int;
    declare plane_speed int;
    declare plane_type varchar(100);
    declare pilot_count int;
    declare leg_duration time;

    if ip_flightID is null or TRIM(ip_flightID) = '' then
        leave sp_main;
    end if;
    
    if not exists(select * from flight 
                  where flightID = TRIM(ip_flightID) 
                    and airplane_status = 'on_ground') then
        leave sp_main;
    end if;
    
    if (select progress from flight where flightID = TRIM(ip_flightID))
       >= (select count(*) from route_path 
           where routeID = (select routeID from flight where flightID = TRIM(ip_flightID))) then
        leave sp_main;
    end if;
    
    if not exists(select * from flight 
                  where flightID = TRIM(ip_flightID)
                    and support_airline is not null 
                    and support_tail is not null) then
        leave sp_main;
    end if;
    
    select a.speed, a.plane_type into plane_speed, plane_type
    from flight f
    join airplane a on f.support_airline = a.airlineID and f.support_tail = a.tail_num
    where f.flightID = TRIM(ip_flightID);
    
    if plane_speed is null or plane_speed <= 0 then
        leave sp_main;
    end if;
    
    select count(*) into pilot_count
    from pilot
    where commanding_flight = TRIM(ip_flightID);
    
    if (UPPER(TRIM(plane_type)) = 'BOEING' and pilot_count < 2)
       or ((UPPER(TRIM(plane_type)) = 'AIRBUS' or plane_type is null) and pilot_count < 1) then
        update flight
        set next_time = addtime(next_time, '00:30:00')
        where flightID = TRIM(ip_flightID);
        leave sp_main;
    end if;
    
    select l.distance into leg_distance
    from flight f
    join route_path rp on f.routeID = rp.routeID and f.progress = rp.sequence - 1
    join leg l on rp.legID = l.legID
    where f.flightID = TRIM(ip_flightID);
    
    if leg_distance is null or leg_distance <= 0 then
        leave sp_main;
    end if;
    
    set leg_duration = leg_time(leg_distance, plane_speed);
    
    update flight
    set progress = progress + 1,
        airplane_status = 'in_flight',
        next_time = addtime(next_time, leg_duration)
    where flightID = TRIM(ip_flightID);
end //
delimiter ;


-- [8] passengers_board()
-- -----------------------------------------------------------------------------
/* This stored procedure updates the state for passengers getting on a flight at
its current airport.  The passengers must be at the same airport as the flight,
and the flight must be heading towards that passenger's desired destination.
Also, each passenger must have enough funds to cover the flight.  Finally, there
must be enough seats to accommodate all boarding passengers. */
-- -----------------------------------------------------------------------------
drop procedure if exists passengers_board;
delimiter //
create procedure passengers_board (in ip_flightID varchar(50))
sp_main: begin

	-- Ensure the flight exists
    -- Ensure that the flight is on the ground
    -- Ensure that the flight has further legs to be flown
    
    -- Determine the number of passengers attempting to board the flight
    -- Use the following to check:
		-- The airport the airplane is currently located at
        -- The passengers are located at that airport
        -- The passenger's immediate next destination matches that of the flight
        -- The passenger has enough funds to afford the flight
        

    declare seat_capacity int;
    declare current_plane_location varchar(50);
    declare flight_cost int;
    declare next_destination char(3);
    declare num_eligible int;

    if ip_flightID is null or TRIM(ip_flightID) = '' then
        leave sp_main;
    end if;
    
    if not exists(select * from flight 
                  where flightID = TRIM(ip_flightID) 
                    and airplane_status = 'on_ground') then
        leave sp_main;
    end if;
    
    if (select progress from flight where flightID = TRIM(ip_flightID))
       >= (select count(*) from route_path 
           where routeID = (select routeID from flight where flightID = TRIM(ip_flightID))) then
        leave sp_main;
    end if;
    
    select a.locationID, a.seat_capacity into current_plane_location, seat_capacity
    from flight f
    join airplane a on f.support_airline = a.airlineID and f.support_tail = a.tail_num
    where f.flightID = TRIM(ip_flightID);
    
    if current_plane_location is null or seat_capacity is null then
        leave sp_main;
    end if;
    
    select cost into flight_cost from flight where flightID = TRIM(ip_flightID);
    if flight_cost is null or flight_cost < 0 then
        leave sp_main;
    end if;
    
    select l.arrival into next_destination
    from flight f
    join route_path rp on f.routeID = rp.routeID and f.progress = rp.sequence - 1
    join leg l on rp.legID = l.legID
    where f.flightID = TRIM(ip_flightID);
    
    if next_destination is null then
        leave sp_main;
    end if;
    
    create temporary table if not exists temp_boarding_passengers (personID varchar(50));
    
    insert into temp_boarding_passengers
    select p.personID
    from passenger p
    join person pe on p.personID = pe.personID
    join passenger_vacations v on p.personID = v.personID and v.sequence = 1
    where pe.locationID = (
        select ap.locationID
        from airport ap
        join leg l on ap.airportID = l.departure
        join route_path rp on l.legID = rp.legID
        join flight f on f.routeID = rp.routeID
        where f.flightID = TRIM(ip_flightID) and rp.sequence = f.progress + 1
        limit 1
    )
    and v.airportID = next_destination
    and p.funds >= flight_cost;
    
    select count(*) into num_eligible from temp_boarding_passengers;
    
    set seat_capacity = seat_capacity - (
        select count(*) from person where locationID = current_plane_location
    );
    
    if num_eligible > seat_capacity then
        drop temporary table if exists temp_boarding_passengers;
        leave sp_main;
    end if;
    
    update passenger
    set funds = funds - flight_cost
    where personID in (select personID from temp_boarding_passengers);
    
    update person
    set locationID = current_plane_location
    where personID in (select personID from temp_boarding_passengers);
    
    delete from passenger_vacations
    where (personID, sequence) in (
        select personID, 1 from temp_boarding_passengers
    );
    
    update passenger_vacations
    set sequence = sequence - 1
    where personID in (select personID from temp_boarding_passengers);
    
    drop temporary table if exists temp_boarding_passengers;
end //
delimiter ;


-- [9] passengers_disembark()
-- -----------------------------------------------------------------------------
/* This stored procedure updates the state for passengers getting off of a flight
at its current airport.  The passengers must be on that flight, and the flight must
be located at the destination airport as referenced by the ticket. */
-- -----------------------------------------------------------------------------
drop procedure if exists passengers_disembark;
delimiter //
create procedure passengers_disembark (in ip_flightID varchar(50))
sp_main: begin

	-- Ensure the flight exists
    -- Ensure that the flight is in the air
    
    -- Determine the list of passengers who are disembarking
	-- Use the following to check:
		-- Passengers must be on the plane supporting the flight
        -- Passenger has reached their immediate next destionation airport
        
	-- Move the appropriate passengers to the airport
    -- Update the vacation plans of the passengers
    
    declare plane_location varchar(50);
    declare arrival_airport char(3);
    declare arrival_airport_location varchar(50);

    if ip_flightID is null or TRIM(ip_flightID) = '' then
         leave sp_main;
    end if;
    
    if not exists (
         select * from flight 
         where flightID = TRIM(ip_flightID) and airplane_status = 'on_ground'
    ) then
         leave sp_main;
    end if;
    
    select a.locationID into plane_location
    from flight f
    join airplane a on f.support_airline = a.airlineID and f.support_tail = a.tail_num
    where f.flightID = TRIM(ip_flightID)
    limit 1;
    
    if plane_location is null or TRIM(plane_location) = '' then
         leave sp_main;
    end if;
    
    select l.arrival into arrival_airport
    from flight f
    join route_path rp on f.routeID = rp.routeID and rp.sequence = f.progress
    join leg l on rp.legID = l.legID
    where f.flightID = TRIM(ip_flightID)
    limit 1;
    
    if arrival_airport is null or TRIM(arrival_airport) = '' then
         leave sp_main;
    end if;
    
    select locationID into arrival_airport_location
    from airport
    where airportID = TRIM(arrival_airport)
    limit 1;
    
    if arrival_airport_location is null or TRIM(arrival_airport_location) = '' then
         leave sp_main;
    end if;
    
    create temporary table if not exists temp_disembark (personID varchar(50));
    
    insert into temp_disembark
    select p.personID
    from passenger p
    join person pe on p.personID = pe.personID
    join passenger_vacations v on p.personID = v.personID and v.sequence = 1
    where pe.locationID = TRIM(plane_location)
      and v.airportID = TRIM(arrival_airport);
    
    if (select count(*) from temp_disembark) = 0 then
         drop temporary table if exists temp_disembark;
         leave sp_main;
    end if;
    
    update person
    set locationID = TRIM(arrival_airport_location)
    where personID in (select personID from temp_disembark);
    
    delete from passenger_vacations
    where (personID, sequence) in (
         select personID, 1 from temp_disembark
    );
    
    update passenger_vacations
    set sequence = sequence - 1
    where personID in (select personID from temp_disembark);
    
    drop temporary table if exists temp_disembark;
end //
delimiter ;

-- [10] assign_pilot()
-- -----------------------------------------------------------------------------
/* This stored procedure assigns a pilot as part of the flight crew for a given
flight.  The pilot being assigned must have a license for that type of airplane,
and must be at the same location as the flight.  Also, a pilot can only support
one flight (i.e. one airplane) at a time.  The pilot must be assigned to the flight
and have their location updated for the appropriate airplane. */
-- -----------------------------------------------------------------------------
drop procedure if exists assign_pilot;
delimiter //
create procedure assign_pilot (in ip_flightID varchar(50), ip_personID varchar(50))
sp_main: begin

	-- Ensure the flight exists
    -- Ensure that the flight is on the ground
    -- Ensure that the flight has further legs to be flown
    
    -- Ensure that the pilot exists and is not already assigned
	-- Ensure that the pilot has the appropriate license
    -- Ensure the pilot is located at the airport of the plane that is supporting the flight
    
	declare plane_type varchar(100);
    declare plane_location varchar(50);
    declare pilot_location varchar(50);
    declare license_ok int default 0;

    if ip_flightID is null or TRIM(ip_flightID) = '' 
       or ip_personID is null or TRIM(ip_personID) = '' then
         leave sp_main;
    end if;

    if not exists (
        select * from flight
        where flightID = TRIM(ip_flightID) and airplane_status = 'on_ground'
    ) then
         leave sp_main;
    end if;

    if (
        select progress from flight where flightID = TRIM(ip_flightID)
    ) >= (
        select count(*) from route_path where routeID = (
            select routeID from flight where flightID = TRIM(ip_flightID)
        )
    ) then
         leave sp_main;
    end if;

    if not exists (
        select * from pilot where personID = TRIM(ip_personID) and commanding_flight is null
    ) then
         leave sp_main;
    end if;

    select a.plane_type, a.locationID 
      into plane_type, plane_location
    from flight f
    join airplane a on f.support_airline = a.airlineID and f.support_tail = a.tail_num
    where f.flightID = TRIM(ip_flightID)
    limit 1;

    if plane_type is null then
        select count(*) into license_ok
        from pilot_licenses
        where personID = TRIM(ip_personID) and UPPER(license) = 'GENERAL';
    else
        select count(*) into license_ok
        from pilot_licenses
        where personID = TRIM(ip_personID) and UPPER(license) = UPPER(plane_type);
    end if;
    
    if license_ok = 0 then
         leave sp_main;
    end if;

    select locationID into pilot_location 
    from person 
    where personID = TRIM(ip_personID)
    limit 1;

    if not exists (
         select * from airport where locationID = TRIM(pilot_location)
    ) then
         leave sp_main;
    end if;

    update pilot
    set commanding_flight = TRIM(ip_flightID)
    where personID = TRIM(ip_personID);

    update person
    set locationID = TRIM(plane_location)
    where personID = TRIM(ip_personID);
    
end //
delimiter ;


-- [11] recycle_crew()
-- -----------------------------------------------------------------------------
/* This stored procedure releases the assignments for a given flight crew.  The
flight must have ended, and all passengers must have disembarked. */
-- -----------------------------------------------------------------------------
drop procedure if exists recycle_crew;
delimiter //
create procedure recycle_crew (in ip_flightID varchar(50))
sp_main: begin
DECLARE v_routeID VARCHAR(50);
    DECLARE v_progress INT;
    DECLARE v_total_legs INT;
    DECLARE v_airlineID VARCHAR(50);
    DECLARE v_tail_num VARCHAR(50);
    DECLARE v_status VARCHAR(100);
    DECLARE v_passengers INT;
    DECLARE v_arrival_airport CHAR(3);
    DECLARE v_new_location VARCHAR(50);

    if ip_flightID is null or TRIM(ip_flightID) = '' then
         leave sp_main;
    end if;
    
    if not exists (select 1 from flight where flightID = TRIM(ip_flightID)) then
         leave sp_main;
    end if;
    
    select routeID, progress, support_airline, support_tail, airplane_status
      into v_routeID, v_progress, v_airlineID, v_tail_num, v_status
    from flight
    where flightID = TRIM(ip_flightID)
    limit 1;
    
    if v_status <> 'on_ground' then
         leave sp_main;
    end if;
    
    select count(*) into v_total_legs 
    from route_path 
    where routeID = TRIM(v_routeID);
    
    if v_progress < v_total_legs then
         leave sp_main;
    end if;
    
    select l.arrival into v_arrival_airport
    from route_path rp
    join leg l on rp.legID = l.legID
    where rp.routeID = TRIM(v_routeID) and rp.sequence = v_total_legs
    limit 1;
    
    if v_arrival_airport is null or TRIM(v_arrival_airport) = '' then
         leave sp_main;
    end if;
    
    select locationID into v_new_location
    from airport
    where airportID = TRIM(v_arrival_airport)
    limit 1;
    
    if v_new_location is null or TRIM(v_new_location) = '' then
         leave sp_main;
    end if;
    
    select count(*) into v_passengers
    from passenger ps
    join person p on ps.personID = p.personID
    where p.locationID = TRIM(v_new_location);
    
    if v_passengers > 0 then
         leave sp_main;
    end if;
    
    update person p
    join pilot pl on p.personID = pl.personID
    set p.locationID = TRIM(v_new_location)
    where pl.commanding_flight = TRIM(ip_flightID);
    
    update pilot
    set commanding_flight = null
    where commanding_flight = TRIM(ip_flightID);
end //
delimiter ;

-- [12] retire_flight()
-- -----------------------------------------------------------------------------
/* This stored procedure removes a flight that has ended from the system.  The
flight must be on the ground, and either be at the start its route, or at the
end of its route.  And the flight must be empty - no pilots or passengers. */
-- -----------------------------------------------------------------------------
drop procedure if exists retire_flight;
delimiter //
create procedure retire_flight (in ip_flightID varchar(50))
sp_main: begin
DECLARE v_routeID VARCHAR(50);
    DECLARE v_progress INT;
    DECLARE v_total_legs INT;
    DECLARE v_airlineID VARCHAR(50);
    DECLARE v_tail_num VARCHAR(50);
    DECLARE v_passengers INT;
    DECLARE v_pilots INT;
    DECLARE v_status VARCHAR(100);

    if ip_flightID is null or TRIM(ip_flightID) = '' then
         leave sp_main;
    end if;
    
    if not exists(select 1 from flight where flightID = TRIM(ip_flightID)) then
         leave sp_main;
    end if;
    
    select routeID, progress, support_airline, support_tail, airplane_status
      into v_routeID, v_progress, v_airlineID, v_tail_num, v_status
    from flight
    where flightID = TRIM(ip_flightID)
    limit 1;
    
    if v_status <> 'on_ground' then
         leave sp_main;
    end if;
    
    select count(*) into v_total_legs
    from route_path
    where routeID = TRIM(v_routeID);
    
    if v_progress <> 0 and v_progress <> v_total_legs then
         leave sp_main;
    end if;
    
    select count(*) into v_passengers
    from passenger ps
    join person p on ps.personID = p.personID
    where p.locationID = (
         select locationID from airplane 
         where airlineID = TRIM(v_airlineID) and tail_num = TRIM(v_tail_num)
         limit 1
    );
    
    if v_passengers > 0 then
         leave sp_main;
    end if;
    
    select count(*) into v_pilots
    from pilot
    where commanding_flight = TRIM(ip_flightID);
    
    if v_pilots > 0 then
         leave sp_main;
    end if;
    
    delete from flight
    where flightID = TRIM(ip_flightID);
end //
delimiter ;

-- [13] simulation_cycle()
-- -----------------------------------------------------------------------------
/* This stored procedure executes the next step in the simulation cycle.  The flight
with the smallest next time in chronological order must be identified and selected.
If multiple flights have the same time, then flights that are landing should be
preferred over flights that are taking off.  Similarly, flights with the lowest
identifier in alphabetical order should also be preferred.

If an airplane is in flight and waiting to land, then the flight should be allowed
to land, passengers allowed to disembark, and the time advanced by one hour until
the next takeoff to allow for preparations.

If an airplane is on the ground and waiting to takeoff, then the passengers should
be allowed to board, and the time should be advanced to represent when the airplane
will land at its next location based on the leg distance and airplane speed.

If an airplane is on the ground and has reached the end of its route, then the
flight crew should be recycled to allow rest, and the flight itself should be
retired from the system. */
-- -----------------------------------------------------------------------------
drop procedure if exists simulation_cycle;
delimiter //
create procedure simulation_cycle ()
sp_main: begin
DECLARE v_flightID VARCHAR(50);
    DECLARE v_status VARCHAR(20);
    DECLARE v_next_time TIME;
    DECLARE v_routeID VARCHAR(50);
    DECLARE v_progress INT;
    DECLARE v_total_legs INT;
    DECLARE v_airlineID VARCHAR(50);
    DECLARE v_tail_num VARCHAR(50);
    DECLARE v_legDistance INT;
    DECLARE v_speed INT;
    DECLARE v_duration_secs INT;
    DECLARE v_new_next_time TIME;
    DECLARE v_leg_distance INT;
    DECLARE v_arrival_airport CHAR(3);
    DECLARE v_new_location VARCHAR(50);

    -- Select the flight with the smallest next_time.
    select flightID, airplane_status, next_time, routeID, progress, support_airline, support_tail
      into v_flightID, v_status, v_next_time, v_routeID, v_progress, v_airlineID, v_tail_num
    from flight
    order by next_time asc,
             case when airplane_status = 'in_flight' then 0 else 1 end,
             flightID asc
    limit 1;
    
    if v_flightID is null or TRIM(v_flightID) = '' then
         leave sp_main;
    end if;
    
    if v_status = 'in_flight' then
         -- Landing branch:
         select l.distance into v_legDistance
         from route_path rp
         join leg l on rp.legID = l.legID
         where rp.routeID = TRIM(v_routeID) and rp.sequence = v_progress
         limit 1;
         
         if v_legDistance is null or v_legDistance <= 0 then
              leave sp_main;
         end if;
         
         update pilot
         set experience = experience + 1
         where commanding_flight = TRIM(v_flightID);
         
         update passenger ps
         join person p on ps.personID = p.personID
         set ps.miles = ps.miles + v_legDistance
         where p.locationID = (
             select locationID from airplane
             where airlineID = TRIM(v_airlineID) and tail_num = TRIM(v_tail_num)
             limit 1
         );
         
         select l.arrival into v_arrival_airport
         from route_path rp
         join leg l on rp.legID = l.legID
         where rp.routeID = TRIM(v_routeID) and rp.sequence = v_progress
         limit 1;
         
         if v_arrival_airport is null or TRIM(v_arrival_airport) = '' then
              leave sp_main;
         end if;
         
         select locationID into v_new_location
         from airport
         where airportID = TRIM(v_arrival_airport)
         limit 1;
         
         if v_new_location is null or TRIM(v_new_location) = '' then
              leave sp_main;
         end if;
         
         update person p
         join passenger_vacations pv on p.personID = pv.personID and pv.sequence = 1
         join passenger ps on p.personID = ps.personID
         set p.locationID = TRIM(v_new_location)
         where p.locationID = (
             select locationID from airplane
             where airlineID = TRIM(v_airlineID) and tail_num = TRIM(v_tail_num)
             limit 1
         )
         and pv.airportID = TRIM(v_arrival_airport);
         
         call passengers_disembark(v_flightID);
         
         update flight
         set airplane_status = 'on_ground',
             next_time = addtime(v_next_time, '01:00:00')
         where flightID = TRIM(v_flightID);
         
    elseif v_status = 'on_ground' then
         select count(*) into v_total_legs
         from route_path
         where routeID = TRIM(v_routeID);
         
         if v_progress = v_total_legs then
              call recycle_crew(v_flightID);
              call retire_flight(v_flightID);
         else
              call passengers_board(v_flightID);
              
              select l.distance into v_legDistance
              from route_path rp
              join leg l on rp.legID = l.legID
              where rp.routeID = TRIM(v_routeID) and rp.sequence = (v_progress + 1)
              limit 1;
              
              if v_legDistance is null or v_legDistance <= 0 then
                   leave sp_main;
              end if;
              
              select speed into v_speed
              from airplane
              where airlineID = TRIM(v_airlineID) and tail_num = TRIM(v_tail_num)
              limit 1;
              
              if v_speed is null or v_speed <= 0 then
                   leave sp_main;
              end if;
              
              set v_duration_secs = floor((v_legDistance / v_speed) * 3600);
              set v_new_next_time = addtime(v_next_time, sec_to_time(v_duration_secs));
              
              update flight
              set airplane_status = 'in_flight',
                  progress = progress + 1,
                  next_time = v_new_next_time
              where flightID = TRIM(v_flightID);
         end if;
    else
         leave sp_main;
    end if;
end //
delimiter ;

-- [14] flights_in_the_air()
-- -----------------------------------------------------------------------------
/* This view describes where flights that are currently airborne are located. 
We need to display what airports these flights are departing from, what airports 
they are arriving at, the number of flights that are flying between the 
departure and arrival airport, the list of those flights (ordered by their 
flight IDs), the earliest and latest arrival times for the destinations and the 
list of planes (by their respective flight IDs) flying these flights. */
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW flights_in_the_air AS
SELECT 
    TRIM(l.departure) AS departure_airport,
    TRIM(l.arrival) AS arrival_airport,
    COUNT(*) AS num_flights,
    GROUP_CONCAT(f.flightID ORDER BY f.flightID) AS flight_list,
    MIN(f.next_time) AS earliest_arrival,
    MAX(f.next_time) AS latest_arrival,
    GROUP_CONCAT(a.locationID ORDER BY f.flightID) AS plane_locations
FROM flight f
JOIN route_path rp ON f.routeID = rp.routeID AND rp.sequence = f.progress
JOIN leg l ON rp.legID = l.legID
JOIN airplane a ON f.support_airline = a.airlineID AND f.support_tail = a.tail_num
WHERE f.airplane_status = 'in_flight'
  AND l.departure IS NOT NULL
  AND l.arrival IS NOT NULL
  AND a.locationID IS NOT NULL
GROUP BY TRIM(l.departure), TRIM(l.arrival);

-- [15] flights_on_the_ground()
-- ------------------------------------------------------------------------------
/* This view describes where flights that are currently on the ground are 
located. We need to display what airports these flights are departing from, how 
many flights are departing from each airport, the list of flights departing from 
each airport (ordered by their flight IDs), the earliest and latest arrival time 
amongst all of these flights at each airport, and the list of planes (by their 
respective flight IDs) that are departing from each airport.*/
-- ------------------------------------------------------------------------------
CREATE OR REPLACE VIEW flights_on_the_ground AS
SELECT 
    LOWER(current_airport) AS departing_from,
    COUNT(*) AS num_flights,
    GROUP_CONCAT(flightID ORDER BY flightID) AS flight_list,
    MIN(next_time) AS earliest_arrival,
    MAX(next_time) AS latest_arrival,
    GROUP_CONCAT(airplane_location ORDER BY flightID) AS airplane_list
FROM (
    SELECT 
         f.flightID,
         f.next_time,
         f.airplane_status,
         f.progress,
         f.routeID,
         f.support_airline,
         f.support_tail,
         a.locationID AS airplane_location,
         CASE 
           WHEN f.progress = 0 THEN 
             (SELECT TRIM(l.departure)
              FROM route_path rp 
              JOIN leg l ON rp.legID = l.legID
              WHERE rp.routeID = f.routeID 
                AND rp.sequence = 1
                AND l.departure IS NOT NULL)
           ELSE 
             (SELECT TRIM(l.arrival)
              FROM route_path rp 
              JOIN leg l ON rp.legID = l.legID
              WHERE rp.routeID = f.routeID 
                AND rp.sequence = f.progress
                AND l.arrival IS NOT NULL)
         END AS current_airport
    FROM flight f
    JOIN airplane a ON f.support_airline = a.airlineID AND f.support_tail = a.tail_num
    WHERE f.airplane_status = 'on_ground'
      AND a.locationID IS NOT NULL
) AS sub
WHERE current_airport IS NOT NULL
GROUP BY LOWER(current_airport);



-- [16] people_in_the_air()
-- -----------------------------------------------------------------------------
/* This view describes where people who are currently airborne are located. We 
need to display what airports these people are departing from, what airports 
they are arriving at, the list of planes (by the location id) flying these 
people, the list of flights these people are on (by flight ID), the earliest 
and latest arrival times of these people, the number of these people that are 
pilots, the number of these people that are passengers, the total number of 
people on the airplane, and the list of these people by their person id. */
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW people_in_the_air AS
SELECT 
    TRIM(l.departure) AS departing_from,
    TRIM(l.arrival) AS arriving_at,
    COUNT(DISTINCT a.locationID) AS num_airplanes,
    GROUP_CONCAT(DISTINCT a.locationID ORDER BY a.locationID) AS airplane_list,
    GROUP_CONCAT(DISTINCT f.flightID ORDER BY f.flightID) AS flight_list,
    MIN(f.next_time) AS earliest_arrival,
    MAX(f.next_time) AS latest_arrival,
    SUM(CASE WHEN p.personID IN (SELECT personID FROM pilot) THEN 1 ELSE 0 END) AS num_pilots,
    SUM(CASE WHEN p.personID IN (SELECT personID FROM passenger) THEN 1 ELSE 0 END) AS num_passengers,
    COUNT(DISTINCT p.personID) AS joint_pilots_passengers,
    GROUP_CONCAT(DISTINCT p.personID ORDER BY p.personID) AS person_list
FROM flight f
JOIN airplane a ON f.support_airline = a.airlineID AND f.support_tail = a.tail_num
JOIN route_path rp ON f.routeID = rp.routeID AND rp.sequence = f.progress
JOIN leg l ON rp.legID = l.legID
JOIN person p ON p.locationID = a.locationID
WHERE f.airplane_status = 'in_flight'
  AND l.departure IS NOT NULL
  AND l.arrival IS NOT NULL
  AND a.locationID IS NOT NULL
GROUP BY TRIM(l.departure), TRIM(l.arrival);



-- [17] people_on_the_ground()
-- -----------------------------------------------------------------------------
/* This view describes where people who are currently on the ground (in airports) are located.
It displays the airport ID, the airport's locationID, airport name, city, state, country,
the number of pilots and passengers at the airport, the total number of people, and a list of person IDs.
*/
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW people_on_the_ground AS
SELECT 
    a.airportID AS departing_from,
    a.locationID,
    a.airport_name,
    a.city,
    a.state,
    a.country,
    SUM(CASE WHEN p.personID IN (SELECT personID FROM pilot) THEN 1 ELSE 0 END) AS num_pilots,
    SUM(CASE WHEN p.personID IN (SELECT personID FROM passenger) THEN 1 ELSE 0 END) AS num_passengers,
    COUNT(*) AS total_people,
    GROUP_CONCAT(p.personID ORDER BY p.personID) AS person_list
FROM airport a
JOIN person p ON p.locationID = a.locationID
WHERE a.airportID IS NOT NULL
  AND a.locationID IS NOT NULL
  AND a.airport_name IS NOT NULL
  AND a.city IS NOT NULL
  AND a.state IS NOT NULL
  AND a.country IS NOT NULL
GROUP BY a.airportID, a.locationID, a.airport_name, a.city, a.state, a.country;


-- [18] route_summary()
-- -----------------------------------------------------------------------------
/* This view gives a summary of every route. It includes the route ID, number of legs,
the leg sequence (as a comma‐separated list of leg IDs), total distance, number of flights on the route,
a list of flight IDs, and the sequence of departure airports along the route.
*/
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW route_summary AS
SELECT 
    r.routeID AS route,
    COUNT(rp.sequence) AS num_legs,
    GROUP_CONCAT(rp.legID ORDER BY rp.sequence) AS leg_sequence,
    SUM(l.distance) AS route_length,
    (SELECT COUNT(*) FROM flight f WHERE f.routeID = r.routeID) AS num_flights,
    (SELECT GROUP_CONCAT(f.flightID ORDER BY f.flightID) FROM flight f WHERE f.routeID = r.routeID) AS flight_list,
    GROUP_CONCAT(CONCAT(TRIM(l.departure), '->', TRIM(l.arrival)) ORDER BY rp.sequence) AS airport_sequence
FROM route r
JOIN route_path rp ON r.routeID = rp.routeID
JOIN leg l ON rp.legID = l.legID
WHERE l.departure IS NOT NULL
  AND l.arrival IS NOT NULL
  AND l.distance IS NOT NULL
GROUP BY r.routeID;



-- [19] alternative_airports()
-- -----------------------------------------------------------------------------
/* This view displays airports that share the same city and state.
It specifies the city, state, country, the number of airports, and lists of airport IDs and airport names.
*/
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW alternative_airports AS
SELECT 
    TRIM(city) AS city,
    TRIM(state) AS state,
    TRIM(country) AS country,
    COUNT(*) AS num_airports,
    GROUP_CONCAT(airportID ORDER BY airportID) AS airport_code_list,
    GROUP_CONCAT(airport_name ORDER BY airportID) AS airport_name_list
FROM airport
WHERE city IS NOT NULL
  AND state IS NOT NULL
  AND country IS NOT NULL
GROUP BY TRIM(city), TRIM(state), TRIM(country)
HAVING COUNT(*) > 1;


-- extra view for phase IV
CREATE OR REPLACE VIEW top_frequent_fliers AS
SELECT 
    RANK() OVER (ORDER BY SUM(pa.miles) DESC) AS miles_rank,
    p.personID,
    p.first_name,
    p.last_name,
    SUM(pa.miles) AS total_miles
FROM person p
JOIN passenger pa ON p.personID = pa.personID
GROUP BY p.personID
ORDER BY total_miles DESC
LIMIT 5;







