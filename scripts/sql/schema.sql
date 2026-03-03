-- Single table for all flight data
CREATE TABLE flights (
    id BIGSERIAL PRIMARY KEY,
    flight_date DATE NOT NULL,
    flight_time TIME,
    time_of_day VARCHAR(20),
    airline_cd VARCHAR(10),
    flight_no VARCHAR(20),
    departure_station_cd VARCHAR(10),
    arrival_station_cd VARCHAR(10),
    arrival_country VARCHAR(100),
    arrival_region VARCHAR(50),
    haul VARCHAR(20),
    aircraft_type VARCHAR(50),
    first_class_seats INTEGER DEFAULT 0,
    business_class_seats INTEGER DEFAULT 0,
    economy_seats INTEGER DEFAULT 0,
    tier1_eligible_pax INTEGER DEFAULT 0,
    tier2_eligible_pax INTEGER DEFAULT 0,
    tier3_eligible_pax INTEGER DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    UNIQUE(flight_date, flight_no, departure_station_cd, arrival_station_cd)
);

-- Create indexes
CREATE INDEX idx_flights_date ON flights(flight_date);
CREATE INDEX idx_flights_airline ON flights(airline_cd);
CREATE INDEX idx_flights_departure ON flights(departure_station_cd);
CREATE INDEX idx_flights_arrival ON flights(arrival_station_cd);
CREATE INDEX idx_flights_haul ON flights(haul);

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO postgres;