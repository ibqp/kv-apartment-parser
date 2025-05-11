import logging
from sqlalchemy.sql import func
from typing import List, Dict, Any
from sqlalchemy.schema import CreateSchema
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP


SCHEMA_NAME = 'kv_apartments'


# Database SQLAlchemy Models (ApartmentDB and ImageDB)
Base = declarative_base()
class ApartmentDB(Base):
    __tablename__ = 'apartments'
    __table_args__ = {'schema': SCHEMA_NAME}

    # Fields
    apartment_id = Column(Integer, primary_key=True)
    apurl = Column(String, unique=True)
    raw_address = Column(String)
    street = Column(String)
    subdistrict = Column(String)
    district = Column(String)
    city = Column(String)
    parish = Column(String)
    price = Column(Integer)
    price_per_m2 = Column(Integer)
    rooms = Column(String)
    bedrooms = Column(String)
    total_area = Column(String)
    floor = Column(String)
    built_year = Column(String)
    cadastre_no = Column(String)
    energy_mark = Column(String)
    utilities_summer = Column(String)
    utilities_winter = Column(String)
    ownership_form = Column(String)
    condition = Column(String)

    # Meta fields
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    images = relationship("ImageDB", back_populates="apartment")
class ImageDB(Base):
    __tablename__ = 'images'
    __table_args__ = {'schema': SCHEMA_NAME}

    # Fields
    id = Column(Integer, primary_key=True)
    apartment_id = Column(Integer, ForeignKey(f'{SCHEMA_NAME}.apartments.apartment_id'))
    image = Column(String)

    # Meta fields
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationship
    apartment = relationship("ApartmentDB", back_populates="images")


# Database Operations Manager
class DatabaseManager:
    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)
        self.Session = sessionmaker(bind=self.engine)
        self._session = None

    @property
    def session(self):
        if self._session is None:
            self._session = self.Session()
        return self._session

    def init_db(self) -> None:
        # Create schema if not exists
        inspector = inspect(self.engine)
        schema_exists = inspector.has_schema(SCHEMA_NAME)
        if not schema_exists:
            self.session.execute(CreateSchema(SCHEMA_NAME))
            self.session.commit()
            logging.info(f"Schema '{SCHEMA_NAME}' initialized.")

        # Create all tables
        Base.metadata.create_all(self.engine)
        logging.debug("Tables created or already exist.")

    def check_apartment_exists(self, url: str) -> bool:
        try:
            exists = self.session.query(ApartmentDB).filter_by(apurl=url).first() is not None
            return exists
        except Exception as e:
            logging.error(f"Error checking if apartment exists: {e}")
            return False

    def save_apartments(self, apartments: List[Dict[str, Any]]) -> None:
        try:
            for apt in apartments:
                # Create new apartment record
                db_apartment = ApartmentDB(
                    apurl=apt.get('apurl')
                    , raw_address = apt.get('raw_address')
                    , street = apt.get('street')
                    , subdistrict = apt.get('subdistrict')
                    , district = apt.get('district')
                    , city = apt.get('city')
                    , parish = apt.get('parish')
                    , price=apt.get('price')
                    , price_per_m2=apt.get('price_per_m2')
                    , rooms=apt.get('rooms')
                    , bedrooms=apt.get('bedrooms')
                    , total_area=apt.get('total_area')
                    , floor=apt.get('floor')
                    , built_year=apt.get('built_year')
                    , cadastre_no=apt.get('cadastre_no')
                    , energy_mark=apt.get('energy_mark')
                    , utilities_summer=apt.get('utilities_summer')
                    , utilities_winter=apt.get('utilities_winter')
                    , ownership_form=apt.get('ownership_form')
                    , condition=apt.get('condition')
                )

                # Create image records
                images = apt.get('images', [])
                if images:
                    for img_url in images:
                        db_image = ImageDB(image=img_url)
                        db_apartment.images.append(db_image) # links image to the apartment

                # Add apartment (and its related iamge objects) to the session
                self.session.add(db_apartment)

            # Save all changes to the database (commit transaction)
            self.session.commit()

            logging.info(f"Successfully saved {len(apartments)} apartments to database.")
        except Exception as e:
            self.session.rollback()
            logging.error(f"Failed to save data to database: {e}")
        finally:
            if self._session:
                self._session.close()
                self._session = None
