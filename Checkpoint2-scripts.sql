
--(Use case 1)  an admin entering a new driver to the system and assigning them a truck.(each step is its own query)

-- 1) add the driver 'Ramiro Cuevas' 

INSERT INTO Drivers (name, phone_number, carrier_id, payment_type, bank_info, medical_card)
VALUES ('Ramiro Cuevas', '555-123-4567', 1, 'Wire Transfer', 'Bank of America', '101010');

-- 2) update the policy_provider for Ramiro Cuevas from null to 6

UPDATE Drivers
SET policy_provider = 6
WHERE name = 'Ramiro Cuevas';

-- 3) show all trucks not assigned to a driver ordered by lowest expenses

SELECT * FROM Trucks
WHERE driver_id IS NULL
ORDER BY expenses ASC;

-- 4) Add 'Ramiro Cuevas' to an available truck with the lowest expenses

UPDATE Trucks
SET driver_id = (SELECT driver_id FROM Drivers WHERE name = 'Ramiro Cuevas')
WHERE truck_id = 27;

-- 5) Show all trucks and their drivers( to verify) 

SELECT Trucks.truck_id, Trucks.make, Trucks.model, Drivers.name AS driver_name
FROM Trucks
LEFT JOIN Drivers ON Trucks.driver_id = Drivers.driver_id;

-- 6) show the insurance provider for the truck assigned to 'Ramiro Cuevas'

SELECT Insurance.name AS insurance_provider
FROM Trucks
JOIN Drivers ON Trucks.driver_id = Drivers.driver_id
JOIN Insurance ON Trucks.physical_insurance = Insurance.insurance_id
WHERE Drivers.name = 'Ramiro Cuevas';

-- 7) remove ramiro cuevas from the truck

UPDATE Trucks
SET driver_id = NULL
WHERE driver_id = (SELECT driver_id FROM (SELECT * FROM Drivers) WHERE name = 'Ramiro Cuevas');

-- 8) delete driver 'Ramiro Cuevas'

DELETE FROM Drivers
WHERE name = 'Ramiro Cuevas';



-- (use case 2) Update truck insurance expiring insurance policy

-- 9) look for any insuarance policies that will expire in the next month grouped by policy providers
SELECT Trucks.truck_id, Trucks.make, Trucks.model, Trucks.license_plate, 
       Insurance.name AS policy_provider, Trucks.policy_end_date, 
       Insurance.insurance_agent, Insurance.agent_phone_number
FROM Trucks
JOIN Insurance ON Trucks.physical_insurance = Insurance.insurance_id
WHERE Trucks.policy_end_date BETWEEN DATE('now') AND DATE('now', '+1 month')
ORDER BY Insurance.name, Trucks.policy_end_date;

-- 10) updated date by one year

UPDATE Trucks
SET policy_end_date = DATE(policy_end_date, '+1 year')
WHERE truck_id = 10;



-- (use case 3) Truck owner sells truck to a someone else 

-- 11) look up trucks (including all info) owned by a specific person ordered by expenses

SELECT * 
FROM Trucks
WHERE owner = 'Jane Smith' 
ORDER BY expenses;

-- 12) update owner of truck with new owner.

UPDATE Trucks
SET owner = 'Alice Brown'  
WHERE truck_id = 3;

-- 13) look up phone number of driver assigned to truck (to inform of change)

SELECT Trucks.truck_id, Trucks.make, Trucks.model, Trucks.owner, 
       Drivers.name AS driver_name, Drivers.phone_number
FROM Trucks
JOIN Drivers ON Trucks.driver_id = Drivers.driver_id
WHERE Trucks.truck_id = 3;



-- (Use case 4) Broker "Landstar" askes for a driver from texas to california.

-- 14) (before taking order) look up the broker's credit score

SELECT credit_score
FROM Brokers
WHERE company_name = 'Landstar';

-- 15) look up trucks with a destination to texas but no following destinaiton. also show the driver and their phone number

SELECT Trucks.truck_id, Trucks.make, Trucks.model, Trucks.license_plate, 
       Trucks.destination_state, Trucks.following_dest_state,
       Drivers.name AS driver_name, Drivers.phone_number
FROM Trucks
JOIN Drivers ON Trucks.driver_id = Drivers.driver_id
WHERE Trucks.destination_state = 'Texas' AND Trucks.following_dest_state IS NULL;

-- 16) set following destination to califonia for chosen truck

UPDATE Trucks
SET following_dest_state = 'California'
WHERE truck_id = 5;

-- 17) double check the truck has been assigned the following destination 

SELECT truck_id, make, model, license_plate, destination_state, following_dest_state
FROM Trucks
WHERE truck_id = 5;



--(use case 5) new dispatcher hired, divide up assigned brokers for more even work load.

-- 18) add new dispatcher info

INSERT INTO Dispatchers (name, phone_number, payment_type, bank_info)
VALUES ('Micheal Scott', '555-678-9101', 'Wire Transfer', 'Bank ABC');

-- 19) Show brokers grouped by the dispatcher they are assigned to

SELECT Dispatchers.dispatcher_id, Dispatchers.name AS dispatcher_name, 
       Brokers.broker_id, Brokers.company_name
FROM Brokers
JOIN Dispatchers ON Brokers.dispatcher_id = Dispatchers.dispatcher_id
ORDER BY Dispatchers.dispatcher_id;


-- 20) reassign 2 brokers to the new dispatcher.

UPDATE Brokers
SET dispatcher_id = (SELECT MAX(dispatcher_id) FROM Dispatchers)  -- Assigns to the new dispatcher
WHERE broker_id IN (4, 8);

-- 21) double check new assignments have been made correctly

SELECT Dispatchers.dispatcher_id, Dispatchers.name AS dispatcher_name, 
       Brokers.broker_id, Brokers.company_name
FROM Brokers
JOIN Dispatchers ON Brokers.dispatcher_id = Dispatchers.dispatcher_id
ORDER BY Dispatchers.dispatcher_id;

