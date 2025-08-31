-- Add column comments for circuits table
COMMENT ON COLUMN circuits.circuitid IS 'Unique identification number of the circuit';
COMMENT ON COLUMN circuits.circuitref IS 'Circuit reference name';
COMMENT ON COLUMN circuits.name IS 'Full name of circuit';
COMMENT ON COLUMN circuits.location IS 'Location of circuit';
COMMENT ON COLUMN circuits.country IS 'Country of circuit';
COMMENT ON COLUMN circuits.lat IS 'Latitude of location of circuit';
COMMENT ON COLUMN circuits.lng IS 'Longitude of location of circuit. Location coordinates: (lat, lng)';
COMMENT ON COLUMN circuits.alt IS 'Altitude of circuit (not useful)';
COMMENT ON COLUMN circuits.url IS 'URL for circuit information';

-- Add column comments for constructorresults table
COMMENT ON COLUMN constructorresults.constructorresultsid IS 'Constructor results identification number';
COMMENT ON COLUMN constructorresults.raceid IS 'Race identification number';
COMMENT ON COLUMN constructorresults.constructorid IS 'Constructor identification number';
COMMENT ON COLUMN constructorresults.points IS 'Points earned by constructor in the race';
COMMENT ON COLUMN constructorresults.status IS 'Status of constructor result';

-- Add column comments for constructors table
COMMENT ON COLUMN constructors.constructorid IS 'The unique identification number identifying constructors';
COMMENT ON COLUMN constructors.constructorref IS 'Constructor reference name';
COMMENT ON COLUMN constructors.name IS 'Full name of the constructor';
COMMENT ON COLUMN constructors.nationality IS 'Nationality of the constructor';
COMMENT ON COLUMN constructors.url IS 'The introduction website of the constructor. How to find out the detailed introduction of the constructor: through its url';

-- Add column comments for constructorstandings table
COMMENT ON COLUMN constructorstandings.constructorstandingsid IS 'Unique identification of the constructor standing records';
COMMENT ON COLUMN constructorstandings.raceid IS 'Race identification number';
COMMENT ON COLUMN constructorstandings.constructorid IS 'Constructor identification number';
COMMENT ON COLUMN constructorstandings.points IS 'How many points acquired in each race';
COMMENT ON COLUMN constructorstandings.position IS 'Position or track of circuits';
COMMENT ON COLUMN constructorstandings.positiontext IS 'Position in text format (same with position, not quite useful)';
COMMENT ON COLUMN constructorstandings.wins IS 'Number of wins';

-- Add column comments for drivers table
COMMENT ON COLUMN drivers.driverid IS 'The unique identification number identifying each driver';
COMMENT ON COLUMN drivers.driverref IS 'Driver reference name';
COMMENT ON COLUMN drivers.number IS 'Driver number';
COMMENT ON COLUMN drivers.code IS 'Abbreviated code for drivers. If null or empty, it means it does not have code';
COMMENT ON COLUMN drivers.forename IS 'Driver forename';
COMMENT ON COLUMN drivers.surname IS 'Driver surname';
COMMENT ON COLUMN drivers.dob IS 'Date of birth';
COMMENT ON COLUMN drivers.nationality IS 'Nationality of drivers';
COMMENT ON COLUMN drivers.url IS 'The introduction website of the drivers';

-- Add column comments for driverstandings table
COMMENT ON COLUMN driverstandings.driverstandingsid IS 'The unique identification number identifying driver standing records';
COMMENT ON COLUMN driverstandings.raceid IS 'Race identification number';
COMMENT ON COLUMN driverstandings.driverid IS 'Driver identification number';
COMMENT ON COLUMN driverstandings.points IS 'How many points acquired in each race';
COMMENT ON COLUMN driverstandings.position IS 'Position or track of circuits';
COMMENT ON COLUMN driverstandings.wins IS 'Number of wins';
COMMENT ON COLUMN driverstandings.positiontext IS 'Position in text format (same with position, not quite useful)';

-- Add column comments for laptimes table
COMMENT ON COLUMN laptimes.raceid IS 'The identification number identifying race';
COMMENT ON COLUMN laptimes.driverid IS 'The identification number identifying each driver';
COMMENT ON COLUMN laptimes.lap IS 'Lap number';
COMMENT ON COLUMN laptimes.position IS 'Position or track of circuits';
COMMENT ON COLUMN laptimes.time IS 'Lap time in minutes/seconds format';
COMMENT ON COLUMN laptimes.milliseconds IS 'Lap time in milliseconds';

-- Add column comments for pitstops table
COMMENT ON COLUMN pitstops.raceid IS 'The identification number identifying race';
COMMENT ON COLUMN pitstops.driverid IS 'The identification number identifying each driver';
COMMENT ON COLUMN pitstops.stop IS 'Stop number';
COMMENT ON COLUMN pitstops.lap IS 'Lap number when pit stop occurred';
COMMENT ON COLUMN pitstops.time IS 'Exact time of pit stop';
COMMENT ON COLUMN pitstops.duration IS 'Duration time of pit stop in seconds';
COMMENT ON COLUMN pitstops.milliseconds IS 'Pit stop duration in milliseconds';

-- Add column comments for qualifying table
COMMENT ON COLUMN qualifying.qualifyid IS 'The unique identification number identifying qualifying. Sprint qualifying is essentially a short-form Grand Prix – a race that is one-third the number of laps of the main event on Sunday. However, the drivers are battling for positions on the grid for the start of Sunday race';
COMMENT ON COLUMN qualifying.raceid IS 'The identification number identifying each race';
COMMENT ON COLUMN qualifying.driverid IS 'The identification number identifying each driver';
COMMENT ON COLUMN qualifying.constructorid IS 'Constructor identification number';
COMMENT ON COLUMN qualifying.number IS 'Driver number';
COMMENT ON COLUMN qualifying.position IS 'Position or track of circuit';
COMMENT ON COLUMN qualifying.q1 IS 'Time in qualifying 1 in minutes/seconds format. Q1 lap times determine pole position and the order of the front 10 positions on the grid. The slowest driver in Q1 starts 10th, the next starts ninth and so on. All 20 F1 drivers participate in the first period, called Q1, with each trying to set the fastest time possible. Those in the top 15 move on to the next period of qualifying, called Q2. The five slowest drivers are eliminated and will start the race in the last five positions on the grid';
COMMENT ON COLUMN qualifying.q2 IS 'Time in qualifying 2 in minutes/seconds format. Only top 15 in the q1 has the record of q2. Q2 is slightly shorter but follows the same format. Drivers try to put down their best times to move on to Q1 as one of the 10 fastest cars. The five outside of the top 10 are eliminated and start the race from 11th to 15th based on their best lap time';
COMMENT ON COLUMN qualifying.q3 IS 'Time in qualifying 3 in minutes/seconds format. Only top 10 in the q2 has the record of q3';

-- Add column comments for races table
COMMENT ON COLUMN races.raceid IS 'The unique identification number identifying the race';
COMMENT ON COLUMN races.year IS 'Year of the race';
COMMENT ON COLUMN races.round IS 'Round number in the season';
COMMENT ON COLUMN races.circuitid IS 'Circuit identification number';
COMMENT ON COLUMN races.name IS 'Name of the race';
COMMENT ON COLUMN races.date IS 'Date of the race';
COMMENT ON COLUMN races.time IS 'Time of the location';
COMMENT ON COLUMN races.url IS 'Introduction of races';

-- Add column comments for results table
COMMENT ON COLUMN results.resultid IS 'The unique identification number identifying race result';
COMMENT ON COLUMN results.raceid IS 'The identification number identifying the race';
COMMENT ON COLUMN results.driverid IS 'The identification number identifying the driver';
COMMENT ON COLUMN results.constructorid IS 'The identification number identifying which constructors';
COMMENT ON COLUMN results.number IS 'Driver number';
COMMENT ON COLUMN results.grid IS 'The number identifying the area where cars are set into a grid formation in order to start the race';
COMMENT ON COLUMN results.position IS 'The finishing position or track of circuits';
COMMENT ON COLUMN results.positiontext IS 'Position in text format (not quite useful)';
COMMENT ON COLUMN results.positionorder IS 'The finishing order of positions';
COMMENT ON COLUMN results.points IS 'Points earned in the race';
COMMENT ON COLUMN results.laps IS 'Number of laps completed';
COMMENT ON COLUMN results.time IS 'Finish time. If the value exists, it means the driver finished the race. Only the time of the champion shows in the format of minutes:seconds.millisecond, the time of the other drivers shows as seconds.millisecond, which means their actual time is the time of the champion adding the value in this cell';
COMMENT ON COLUMN results.milliseconds IS 'The actual finishing time of drivers in milliseconds';
COMMENT ON COLUMN results.fastestlap IS 'Fastest lap number achieved during the race';
COMMENT ON COLUMN results.rank IS 'Starting rank positioned by fastest lap speed';
COMMENT ON COLUMN results.fastestlaptime IS 'Fastest lap time achieved. Faster (smaller in the value) fastestLapTime leads to higher rank (smaller is higher rank)';
COMMENT ON COLUMN results.fastestlapspeed IS 'Fastest lap speed in km/h';
COMMENT ON COLUMN results.statusid IS 'Status identification number. Its category description appears in the table status';

-- Add column comments for seasons table
COMMENT ON COLUMN seasons.year IS 'The unique identification number identifying the race';
COMMENT ON COLUMN seasons.url IS 'Website link of season race introduction';

-- Add column comments for status table
COMMENT ON COLUMN status.statusid IS 'The unique identification number identifying status';
COMMENT ON COLUMN status.status IS 'Full name of status';