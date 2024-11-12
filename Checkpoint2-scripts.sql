-- drivers who only prefer zelle or wire transfer.
SELECT * FROM Drivers
WHERE payment_type = 'Zelle' OR payment_type = 'Wire Transfer';

-- Insurance whos expiration year is in 2026
SELECT * FROM Insurance
WHERE strftime('%Y', expiry_date) = '2026';

-- Find dispatchers who prefer zelle, and work for specific carrier.
SELECT * FROM Dispatchers
WHERE payment_type = 'Zelle' AND carrier_id IS NOT NULL;

-- Select brokers whose credit score is either A or B
SELECT * FROM Brokers
WHERE credit_score IN ('A', 'B');

