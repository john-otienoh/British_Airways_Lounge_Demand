#!/usr/bin/env python3
import pandas as pd
import argparse
import os
import sys
import logging
from datetime import datetime

from connection import DatabaseConnection


logs_dir = 'logs'
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

log_filename = os.path.join(logs_dir, f'flight_loader{datetime.now().strftime("%Y%m%d")}.log')
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=log_filename,
    filemode='a'
)
logger = logging.getLogger(__name__)

class FlightDataLoader:
    """Load Flights from CSV to PostgreSQL"""
    def __init__(self, csv_path: str) -> None:
        self.csv_path = csv_path
        self.df = None
        self.table_name = 'flights'
        logger.info(f"FlightDataLoader initialized for {csv_path}")
    
    def load_csv(self):
        try:
            if not os.path.exists(self.csv_path):
                raise FileNotFoundError(f"CSV file not found: {self.csv_path}")
            logger.info(f"Loading CSV from {self.csv_path}")
            self.df = pd.read_csv(self.csv_path)
            logger.info(f"Loaded {len(self.df)} rows from CSV")
            print(f"The dataset {self.csv_path} has {self.df.shape[1]} columns and {self.df.shape[0]} rows.")
            return self.df
        except Exception as e:
            logger.error(f"Failed to load CSV: {e}")
    
    def clean_data(self):
        if self.df is None:
            raise ValueError("No data loaded")
        logger.info("Cleaning and preparing data...")

        df = self.df.copy()
        df.columns = [column.lower() for column in df.columns]

        if 'flight_date' in df.columns:
            df['flight_date'] = pd.to_datetime(df['flight_date'])
        
        if 'flight_time' in df.columns:
            df['flight_time'] = pd.to_datetime(df['flight_time'], format='%H:%M:%S').dt.time
        self.df = df
        logger.info(f"Data cleaning complete. {len(df)} rows ready for insertion")
        
        return self.df
    
    def insert_data(self, db: DatabaseConnection, batch_size: int = 1000):
        if self.df  is None:
            logger.warning("No data to insert")
            return 0, 0
        logger.info(f"Inserting {len(self.df)} rows in batches of {batch_size}...")

        insert_query = """
            INSERT INTO flights (
                flight_date, flight_time, time_of_day, airline_cd, flight_no,  -- Fixed column name
                departure_station_cd, arrival_station_cd, arrival_country, arrival_region,
                haul, aircraft_type, first_class_seats, business_class_seats, economy_seats,
                tier1_eligible_pax, tier2_eligible_pax, tier3_eligible_pax
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (flight_date, flight_no, departure_station_cd, arrival_station_cd) 
            DO NOTHING;
        """
        failed, success = 0, 0
        for start_idx in range(0, len(self.df), batch_size):
            batch = self.df.iloc[start_idx:start_idx + batch_size]
            
            try:
                for _, row in batch.iterrows():
                    params = (
                        row['flight_date'],
                        row['flight_time'],
                        row['time_of_day'],
                        row['airline_cd'],
                        row['flight_no'],
                        row['departure_station_cd'],
                        row['arrival_station_cd'],
                        row['arrival_country'],
                        row['arrival_region'],
                        row['haul'],
                        row['aircraft_type'],
                        int(row['first_class_seats']),
                        int(row['business_class_seats']),
                        int(row['economy_seats']),
                        int(row['tier1_eligible_pax']),
                        int(row['tier2_eligible_pax']),
                        int(row['tier3_eligible_pax'])
                    )
                    
                    db.execute_query(insert_query, params, fetch=False)
                    success += 1
                
                logger.debug(f"Inserted batch {start_idx//batch_size + 1}: {len(batch)} rows")
            except Exception as e:
                logger.error(f"Failed to insert batch starting at {start_idx}: {e}")
                failed += len(batch)
        logger.info(f"Insertion complete: {success} inserted, {failed} failed")
        return success, failed
    def db_statistics(self, db: DatabaseConnection):
        logger.info("Database Statistics...")
        result = db.execute_query("SELECT COUNT(*) AS count FROM flights")
        count = result[0]['count'] if result else 0
        print(f"Total Flights {count}")
        return count
    
    def run(self):
        print("\n" +  "=" * 60)
        try:
            print("\n Step 1: Loading CSV...")
            self.load_csv()
            print("\n Step 2: Cleaning Data...")
            self.clean_data()

            with DatabaseConnection() as db:
                success, failed = self.insert_data(db)
                total = self.db_statistics(db=db)
                print("=" * 60)
                print(f"  CSV rows: {len(self.df)}")
                print(f"  Inserted: {success}")
                print(f"  Failed: {failed}")
                print(f"  Total in DB: {total}")
                if failed > 0:
                    print(f"\n {failed} rows failed to insert. Check logs for details.")
            
        except Exception as e:
            logger.error(f"Load failed: {e}")
            print(f"\n Error: {e}")
            sys.exit(1)
def main():
    parser = argparse.ArgumentParser(description="Load flight data from CSV to PostgreSQL")
    parser.add_argument('csv_file', help='Path to CSV file containing flight data')
    parser.add_argument('--batch-size', type=int, default=10, help='Batch size for inserts')
    args = parser.parse_args()
    loader = FlightDataLoader(args.csv_file)
    loader.run()

if __name__ == '__main__':
    main()
