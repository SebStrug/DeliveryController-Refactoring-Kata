import datetime
from dataclasses import dataclass
from typing import Optional, Type

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


class DeliveryNode:
    def __init__(self, data: Delivery):
        # Define a doubly linked list
        self.data = data
        self.next: Optional["DeliveryNode"] = None
        self.prev: Optional["DeliveryNode"] = None

    def __repr__(self) -> str:
        return str(self.data) + f", next: {self.next}"


class DeliveryController:
    def __init__(
        self, delivery_schedule: list[Delivery], gateway: Type[Gateway]
    ) -> None:
        self.delivery_schedule = delivery_schedule
        self.email_gateway = gateway()
        self.map_service = MapService()
        self.head: Optional[DeliveryNode] = None
        self.create_delivery_list(self.delivery_schedule)

    def create_delivery_list(self, deliveries: list[Delivery]) -> None:
        """Create a doubly linked list of deliveries

        Args:
            deliveries: List of deliveries as Delivery objects

        Returns:
            Doubly linked list of deliveries
        """
        if not deliveries:
            return

        self.head = DeliveryNode(deliveries[0])
        current_node = self.head
        for delivery in deliveries[1:]:
            new_node = DeliveryNode(delivery)
            current_node.next = new_node
            new_node.prev = current_node
            current_node = new_node
        return

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
        if not self.head:
            return

        node = self.head
        while node:
            if node.data.id != delivery_event.id:
                node = node.next
                continue

            node.data.arrived = True
            time_diff = delivery_event.time_of_delivery - node.data.time_of_delivery
            if time_diff < datetime.timedelta(minutes=10):
                node.data.on_time = True

            self.send_delivery_feedback_email(
                delivery_event.time_of_delivery, node.data.contact_email
            )

            if node.next:
                self.send_next_delivery_email(delivery_event.location, node.next.data)

            if not node.data.on_time and node.prev:
                elapsed_time = (
                    node.data.time_of_delivery - node.prev.data.time_of_delivery
                )
                self.map_service.update_average_speed(
                    node.prev.data.location, node.data.location, elapsed_time
                )
            node = node.next

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
