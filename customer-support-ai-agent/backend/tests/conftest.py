"""Shared pytest fixtures: an isolated in-memory SQLite DB per test."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.connection import Base
from app.models.order import Order


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)
    session = TestingSession()

    # seed a couple of orders used across tests
    session.add_all([
        Order(order_number="ORD-1001", customer_id="CUST-001", status="processing",
              total_amount=49.99, is_cancellable=True, is_refundable=True),
        Order(order_number="ORD-1002", customer_id="CUST-002", status="shipped",
              total_amount=120.00, is_cancellable=False, is_refundable=True),
    ])
    session.commit()

    yield session
    session.close()
