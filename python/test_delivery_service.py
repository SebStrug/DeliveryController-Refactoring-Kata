import pytest
from datetime import datetime

from delivery_controller import DeliveryController, Delivery, DeliveryEvent
from map_service import MapService, Location

location1 = Location(52.2296756, 21.0122287)
location2 = Location(52.406374, 16.9251681)

class DummyGateway:
    def __init__(self):
        self.sent = 0

    def send(self, address, subject, message):
        self.sent += 1


def test_map_service():
    map_service = MapService()
    assert map_service.calculate_distance(location1, location2) == pytest.approx(
        278.546, rel=1e-2
    )


@pytest.fixture
def globe_loc():
    return Location(latitude=51.4906, longitude=0.3097)


def test_empty_delivery_controller(globe_loc):
    some_time = datetime(2022, 1, 1, 13, 0, 0)
    event = DeliveryEvent(id="foo", time_of_delivery=some_time, location=globe_loc)
    controller = DeliveryController([], DummyGateway)
    controller.update_delivery(event)
    assert controller.email_gateway.sent == 0


def test_delivery_controller(globe_loc):
    some_time = datetime(2022, 1, 1, 13, 0, 0)
    delivery = Delivery(
        id="foo",
        contact_email="seb@gmail.com",
        location=globe_loc,
        time_of_delivery=some_time,
        arrived=False,
        on_time=True,
    )
    controller = DeliveryController([delivery], DummyGateway)

    event = DeliveryEvent(id="foo", time_of_delivery=some_time, location=globe_loc)
    controller.update_delivery(event)
    assert controller.email_gateway.sent == 1


def test_delivery_controller_non_matching_ids(globe_loc):
    some_time = datetime(2022, 1, 1, 13, 0, 0)
    delivery = Delivery(
        id="bar",
        contact_email="seb@gmail.com",
        location=globe_loc,
        time_of_delivery=some_time,
        arrived=False,
        on_time=True,
    )
    controller = DeliveryController([delivery], DummyGateway)

    event = DeliveryEvent(id="foo", time_of_delivery=some_time, location=globe_loc)
    controller.update_delivery(event)
    assert controller.email_gateway.sent == 0
