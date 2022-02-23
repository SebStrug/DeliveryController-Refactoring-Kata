import datetime
from dataclasses import dataclass
from typing import Type

from email_gateway import Gateway
from map_service import MapService, Location


@dataclass
class DeliveryEvent:
    id: str
    time_of_delivery: datetime.datetime
    location: Location


@dataclass
class Delivery:
    id: str
    contact_email: str
    location: Location
    time_of_delivery: datetime.datetime
    arrived: bool
    on_time: bool


class DeliveryController:
    def __init__(
        self, delivery_schedule: list[Delivery], gateway: Type[Gateway]
    ) -> None:
        self.delivery_schedule = delivery_schedule
        self.email_gateway = gateway()
        self.map_service = MapService()

    def update_delivery(self, delivery_event: DeliveryEvent) -> None:
        """Given a delivery event:
        1. Check if the event ID matches one of the deliveries in the
        delivery schedule...
        2. Mark that delivery as arrived
        3. Calculate the time difference between the delivery time and
        delivery event time
        # TODO (SS): Remove this magic number
        4. If it's less than 10 minutes, mark it as on time
        5. Send a feedback email
        6. If there are more deliveries... get the ETA of the next delivery...
        and send an ETA email
        7. If not on time, update the average speed
        """
        for i, delivery in enumerate(self.delivery_schedule):
            if delivery_event.id == delivery.id:
                delivery.arrived = True
                time_difference = (
                    delivery_event.time_of_delivery - delivery.time_of_delivery
                )
                if time_difference < datetime.timedelta(minutes=10):
                    delivery.on_time = True

                self.send_delivery_feedback_email(
                    delivery_event.time_of_delivery, delivery.contact_email
                )
                try:
                    self.send_next_delivery_email(
                        delivery_event.location, self.delivery_schedule[i + 1]
                    )
                except IndexError:
                    # no next delivery, so no next delivery email to send
                    pass

                if not delivery.on_time and len(self.delivery_schedule) > 1 and i > 0:
                    previous_delivery = self.delivery_schedule[i - 1]
                    elapsed_time = (
                        delivery.time_of_delivery - previous_delivery.time_of_delivery
                    )
                    self.map_service.update_average_speed(
                        previous_delivery.location, delivery.location, elapsed_time
                    )

    def send_next_delivery_email(
        self, prev_event_loc: Location, next_delivery: Delivery
    ) -> None:
        """Send an email for the next delivery

        Args:
            prev_event_loc: Previous event location
            next_delivery: Next delivery
        """
        next_eta = self.map_service.calculate_eta(
            prev_event_loc, next_delivery.location
        )
        message = (
            f"Your delivery to {next_delivery.location} is next, "
            f"estimated time of arrival is in {next_eta} minutes. Be ready!"
        )
        self.email_gateway.send(
            next_delivery.contact_email, "Your delivery will arrive soon", message
        )

    def send_delivery_feedback_email(
        self, time_of_delivery: datetime, email: str
    ) -> None:
        """Send email asking for feedback

        Args:
            time_of_delivery: Time of delivery event
            email: Email address to send feedback email to
        """
        message = (
            f"Regarding your delivery today at {time_of_delivery}."
            " How likely would you be to recommend this delivery service to a friend?"
            " Click <a href='url'>here</a>"
        )
        self.email_gateway.send(email, "Your feedback is important to us", message)
