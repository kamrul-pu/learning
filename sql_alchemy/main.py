from typing import List, Optional
from sqlalchemy import create_engine
from sqlalchemy import ForeignKey, String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session


# Base class for all SQLAlchemy ORM models
class Base(DeclarativeBase):
    pass


# Define the 'User' model which represents a user account
class User(Base):
    __tablename__ = "user_account"  # The name of the table in the database

    # Define the columns for the user_account table
    id: Mapped[int] = mapped_column(primary_key=True)  # Primary key, integer ID
    name: Mapped[str] = mapped_column(
        String(30)
    )  # User's name, a string (max length 30)
    full_name: Mapped[Optional[str]]  # Optional full name, can be None
    addresses: Mapped[List["Address"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )  # One-to-many relationship with Address, user can have many addresses

    def __repr__(self) -> str:
        # Define the string representation of the User object
        return f"User(id={self.id!r}, name={self.name!r}, full_name={self.full_name!r})"


# Define the 'Address' model representing the user's email address
class Address(Base):
    __tablename__ = "address"  # The name of the table in the database

    # Define the columns for the address table
    id: Mapped[int] = mapped_column(primary_key=True)  # Primary key, integer ID
    email_address: Mapped[str]  # Email address as a string
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user_account.id")
    )  # Foreign key to the User table
    user: Mapped["User"] = relationship(
        back_populates="addresses"
    )  # Many-to-one relationship with User

    def __repr__(self) -> str:
        # Define the string representation of the Address object
        return f"Address(id={self.id!r}, email_address={self.email_address!r}"


# Set up the SQLite in-memory database and enable SQL logging for debugging
engine = create_engine("sqlite://", echo=True)

# Create all tables based on the defined models
Base.metadata.create_all(engine)

# Start a session to interact with the database
with Session(engine) as session:
    # Create new User objects and their associated Address objects
    spongebob = User(
        name="spongebob",
        full_name="Spongebob Squarepants",
        addresses=[
            Address(email_address="spongebob@sqlalchemy.org")
        ],  # One address for Spongebob
    )
    sandy = User(
        name="sandy",
        full_name="Sandy Cheeks",
        addresses=[
            Address(email_address="sandy@sqlalchemy.org"),
            Address(email_address="sandy@squirrelpower.org"),
        ],  # Two addresses for Sandy
    )
    patrick = User(
        name="patrick", full_name="Patrick Star"
    )  # Patrick doesn't have an address yet

    # Add all the new users to the session
    session.add_all([spongebob, sandy, patrick])

    # Commit the transaction to persist the data to the database
    session.commit()

# Start a new session to perform queries
session = Session(engine)

# Create a query to select users whose names are 'spongebob' or 'sandy'
stmt = select(User).where(User.name.in_(["spongebob", "sandy"]))

# Execute the query and print the selected users
for user in session.scalars(stmt):
    print(f"user id={user.id}, name={user.name}, full_name={user.full_name}")

# Create a query to select an Address for Sandy with a specific email address
stmt = (
    select(Address)
    .join(Address.user)  # Join with the User table to access user-related data
    .where(User.name == "sandy")  # Filter for Sandy
    .where(
        Address.email_address == "sandy@sqlalchemy.org"
    )  # Specific email address filter
)

# Execute the query and fetch the result (Sandy's email address)
sandy_address = session.scalars(stmt).one()
print(sandy_address)

# Now, we want to modify Patrick's data
stmt = select(User).where(User.name == "patrick")
patrick = session.scalars(stmt).one()

# Add a new address for Patrick
patrick.addresses.append(Address(email_address="patrickstar@sqlalchemy.org"))

# Modify the email address for Sandy's address
sandy_address.email_address = "sandy_cheeks@sqlalchemy.org"

# Commit the changes to the database
session.commit()


# Fetch the 'sandy' user again from the database using the primary key (id=2)
sandy = session.get(User, 2)

# Remove Sandy's specific address (the one we just updated)
sandy.addresses.remove(sandy_address)

# Use flush to ensure changes are persisted in memory but not yet committed
session.flush()

# Delete Patrick from the database
session.delete(patrick)

# Commit all changes to the database (Patrick is now deleted, and Sandy's address is updated)
session.commit()
