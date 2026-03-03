import psycopg2
import os
from dotenv import load_dotenv
import logging
from psycopg2.extras import RealDictCursor
from datetime import datetime

# Load environment variables
load_dotenv()

logs_dir = 'logs'
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

log_filename = os.path.join(logs_dir, f'airline_db_{datetime.now().strftime("%Y%m%d")}.log')
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=log_filename,
    filemode='a'
)
logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Handle PostgreSQL database connection"""
    def __init__(self) -> None:
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = os.getenv('DB_PORT', '5432')
        self.database = os.getenv('DB_NAME', 'poetry_data')
        self.user = os.getenv('DB_USER', 'postgres')
        self.password = os.getenv('DB_PASSWORD')
        self.connection = None
        self.cursor = None
        logger.info(f"Database Connection Initialized for {self.database}")
    def connect(self):
        """Establish Database Connection"""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self.connection.autocommit = True
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            logger.info(f"Connected to database: {self.database}(autocommit={self.connection.autocommit})")
        except psycopg2.OperationalError as e:
            logger.error(f"Database connection failed - Operational error: {e}")
            raise ConnectionError(f"Failed to connect to database: {e}")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def close(self) -> None:
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
            logger.debug("Cursor closed")

        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def execute_query(self, query: str, params = None, fetch: bool = True):
        """
        Execute a SQL query with parameters.
        
        Args:
            query: SQL query string
            params: Tuple of query parameters
            fetch: Whether to fetch and return results
            
        Returns:
            List of dictionaries if fetch=True, None otherwise
        """
        try:
            if not self.connection:
                self.connect()
            logger.debug(f"Executing query: {query[:10]}...")
            self.cursor.execute(query, params)

            if fetch:
                results = self.cursor.fetchall()
                logger.debug(f"Query returned {len(results)} rows")
                return results
            return None
        except psycopg2.Error as e:
            logger.error(f"Query execution failed: {e}")
            if self.connection and not self.connection.autocommit:
                self.connection.rollback()
            raise
        except Exception as e:
            logger.error(f"Unexpected error during query execution: {e}")
            raise
    
    def get_tables(self):
        """Get list of tables in database"""
        query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """
        return self.execute_query(query) or []
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        if exc_type:
            logger.error(f"Exception in context: {exc_type.__name__}: {exc_val}")

if __name__ == "__main__":
    try:
        with DatabaseConnection() as db:
            tables = db.get_tables()
            print(f"\n Tables in database:")
            for table in tables:
                print(f"  - {table['table_name']}")
    except Exception as e:
        print(f"Error: {e}")
