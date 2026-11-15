import asyncio
import flet as ft
from models import Ride
from storage import CarpoolManager


def main(page: ft.Page):
    page.title = "UniRide — Campus & Commuter Carpool"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.TEAL)
    page.window.width = 460
    page.window.height = 820

    manager = CarpoolManager()
    # Simulated logged-in user (can be switched via top bar)
    state = {"current_user": "Alex V."}

    def notify(message: str, is_error: bool = False):
        page.show_dialog(
            ft.SnackBar(
                content=ft.Text(message, color=ft.Colors.WHITE),
                bgcolor=ft.Colors.RED_700 if is_error else ft.Colors.TEAL_700,
            )
        )

    def go(route: str):
        asyncio.create_task(page.push_route(route))

    # --- Reusable UI Components ---
    def build_ride_card(ride: Ride) -> ft.Card:
        is_booked = state["current_user"] in ride.passengers
        is_driver = state["current_user"] == ride.driver_name

        badge_text = (
            "Your Ride" if is_driver
            else "Booked" if is_booked
            else f"{ride.seats_available} seats left"
        )
        badge_color = (
            ft.Colors.BLUE_100 if is_driver
            else ft.Colors.GREEN_100 if is_booked
            else ft.Colors.TEAL_50 if ride.seats_available > 0
            else ft.Colors.RED_100
        )

        return ft.Card(
            elevation=2,
            content=ft.Container(
                padding=16,
                on_click=lambda _: go(f"/ride/{ride.ride_id}"),
                border_radius=12,
                content=ft.Column(
                    spacing=8,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Row(
                                    spacing=6,
                                    controls=[
                                        ft.Icon(ft.Icons.DIRECTIONS_CAR, color=ft.Colors.TEAL),
                                        ft.Text(ride.driver_name, weight=ft.FontWeight.BOLD, size=15),
                                    ],
                                ),
                                ft.Container(
                                    bgcolor=badge_color,
                                    padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                                    border_radius=20,
                                    content=ft.Text(badge_text, size=12, weight=ft.FontWeight.W_600),
                                ),
                            ],
                        ),
                        ft.Row(
                            spacing=8,
                            controls=[
                                ft.Icon(ft.Icons.TRIP_ORIGIN, size=16, color=ft.Colors.GREEN),
                                ft.Text(ride.origin, size=14, expand=True),
                            ],
                        ),
                        ft.Row(
                            spacing=8,
                            controls=[
                                ft.Icon(ft.Icons.LOCATION_ON, size=16, color=ft.Colors.RED_400),
                                ft.Text(ride.destination, size=14, weight=ft.FontWeight.W_500, expand=True),
                            ],
                        ),
                        ft.Divider(height=1),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(f"Departs: {ride.departure_time}", size=13, color=ft.Colors.GREY_700),
                                ft.Text(
                                    f"R{ride.price_per_seat:.2f} / seat",
                                    size=15,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.TEAL_800,
                                ),
                            ],
                        ),
                    ],
                ),
            ),
        )

    # --- Views ---
    def home_view() -> ft.View:
        origin_input = ft.TextField(
            label="From (Origin)",
            prefix_icon=ft.Icons.MY_LOCATION,
            dense=True,
            expand=True,
        )
        dest_input = ft.TextField(
            label="To (Destination)",
            prefix_icon=ft.Icons.SEARCH,
            dense=True,
            expand=True,
        )
        rides_column = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

        def refresh_list(e=None):
            filtered = manager.search_rides(origin_input.value, dest_input.value)
            rides_column.controls = (
                [build_ride_card(r) for r in filtered]
                if filtered
                else [
                    ft.Container(
                        padding=30,
                        alignment=ft.Alignment.CENTER,
                        content=ft.Text("No matching rides found.", color=ft.Colors.GREY_600),
                    )
                ]
            )
            page.update()

        origin_input.on_change = refresh_list
        dest_input.on_change = refresh_list
        rides_column.controls = [build_ride_card(r) for r in manager.rides]

        def switch_user_dialog(e):
            name_field = ft.TextField(label="Your Display Name", value=state["current_user"])

            def save_user(_):
                if name_field.value.strip():
                    state["current_user"] = name_field.value.strip()
                    page.pop_dialog()
                    route_change()

            page.show_dialog(
                ft.AlertDialog(
                    title=ft.Text("Switch Active User"),
                    content=name_field,
                    actions=[
                        ft.TextButton("Cancel", on_click=lambda _: page.pop_dialog()),
                        ft.FilledButton("Save", on_click=save_user),
                    ],
                )
            )

        return ft.View(
            route="/",
            appbar=ft.AppBar(
                title=ft.Text("UniRide Carpool", weight=ft.FontWeight.BOLD),
                bgcolor=ft.Colors.TEAL,
                color=ft.Colors.WHITE,
                actions=[
                    ft.TextButton(
                        content=ft.Row(
                            spacing=4,
                            controls=[
                                ft.Icon(ft.Icons.PERSON, color=ft.Colors.WHITE, size=18),
                                ft.Text(state["current_user"], color=ft.Colors.WHITE),
                            ],
                        ),
                        on_click=switch_user_dialog,
                    )
                ],
            ),
            floating_action_button=ft.FloatingActionButton(
                icon=ft.Icons.ADD,
                content="Offer Ride",
                on_click=lambda _: go("/offer"),
            ),
            navigation_bar=ft.NavigationBar(
                selected_index=0,
                on_change=lambda e: go("/" if e.control.selected_index == 0 else "/my-trips"),
                destinations=[
                    ft.NavigationBarDestination(icon=ft.Icons.EXPLORE, label="Find Rides"),
                    ft.NavigationBarDestination(icon=ft.Icons.BOOKMARK_ADDED, label="My Trips"),
                ],
            ),
            controls=[
                ft.Container(
                    padding=12,
                    expand=True,
                    content=ft.Column(
                        spacing=12,
                        expand=True,
                        controls=[
                            ft.Row(spacing=8, controls=[origin_input, dest_input]),
                            rides_column,
                        ],
                    ),
                )
            ],
        )

    def offer_ride_view() -> ft.View:
        origin_tf = ft.TextField(label="Pickup Location *", prefix_icon=ft.Icons.TRIP_ORIGIN)
        dest_tf = ft.TextField(label="Destination *", prefix_icon=ft.Icons.LOCATION_ON)
        time_tf = ft.TextField(label="Departure Time (e.g. 08:30 AM) *", prefix_icon=ft.Icons.ACCESS_TIME)
        vehicle_tf = ft.TextField(label="Vehicle Model & Color *", prefix_icon=ft.Icons.DIRECTIONS_CAR)
        price_tf = ft.TextField(
            label="Price per Seat (R) *",
            prefix_icon=ft.Icons.PAYMENTS,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        seats_dropdown = ft.Dropdown(
            label="Available Seats *",
            value="3",
            options=[ft.dropdown.Option(str(i)) for i in range(1, 7)],
        )

        def submit_ride(e):
            if not all([origin_tf.value, dest_tf.value, time_tf.value, vehicle_tf.value, price_tf.value]):
                notify("Please fill in all required fields.", is_error=True)
                return
            try:
                price = float(price_tf.value)
                if price < 0:
                    raise ValueError
            except ValueError:
                notify("Enter a valid numeric price.", is_error=True)
                return

            new_ride = Ride(
                driver_name=state["current_user"],
                origin=origin_tf.value.strip(),
                destination=dest_tf.value.strip(),
                departure_time=time_tf.value.strip(),
                price_per_seat=price,
                total_seats=int(seats_dropdown.value),
                vehicle=vehicle_tf.value.strip(),
            )
            manager.add_ride(new_ride)
            notify("Ride published!")
            go("/")

        return ft.View(
            route="/offer",
            appbar=ft.AppBar(
                title=ft.Text("Offer a Ride"),
                bgcolor=ft.Colors.TEAL,
                color=ft.Colors.WHITE,
            ),
            controls=[
                ft.Container(
                    padding=16,
                    expand=True,
                    content=ft.Column(
                        spacing=14,
                        scroll=ft.ScrollMode.AUTO,
                        controls=[
                            ft.Text(
                                f"Posting as driver: {state['current_user']}",
                                weight=ft.FontWeight.W_600,
                                color=ft.Colors.TEAL_800,
                            ),
                            origin_tf,
                            dest_tf,
                            time_tf,
                            vehicle_tf,
                            ft.Row(spacing=10, controls=[
                                ft.Container(content=price_tf, expand=True),
                                ft.Container(content=seats_dropdown, expand=True),
                            ]),
                            ft.FilledButton(
                                "Publish Ride",
                                icon=ft.Icons.CHECK_CIRCLE,
                                height=48,
                                width=float("inf"),
                                on_click=submit_ride,
                            ),
                        ],
                    ),
                )
            ],
        )

    def ride_detail_view(ride_id: str) -> ft.View:
        ride = manager.get_ride(ride_id)
        if not ride:
            return ft.View(
                route=f"/ride/{ride_id}",
                appbar=ft.AppBar(title=ft.Text("Ride Not Found")),
                controls=[ft.Text("This ride no longer exists.")],
            )

        user = state["current_user"]
        is_booked = user in ride.passengers
        is_driver = user == ride.driver_name

        def handle_book(e):
            success, msg = ride.book_seat(user)
            if success:
                manager.save()
                notify(msg)
                route_change()
            else:
                notify(msg, is_error=True)

        def handle_cancel(e):
            if ride.cancel_booking(user):
                manager.save()
                notify("Booking cancelled.")
                route_change()

        action_button = (
            ft.OutlinedButton("You are the driver of this trip", disabled=True, width=float("inf"))
            if is_driver
            else ft.FilledTonalButton(
                "Cancel My Seat",
                icon=ft.Icons.CANCEL,
                width=float("inf"),
                on_click=handle_cancel,
            )
            if is_booked
            else ft.FilledButton(
                f"Book Seat (R{ride.price_per_seat:.2f})",
                icon=ft.Icons.EVENT_SEAT,
                disabled=ride.seats_available == 0,
                width=float("inf"),
                height=48,
                on_click=handle_book,
            )
        )

        passenger_chips = (
            [ft.Chip(label=ft.Text(p), leading=ft.Icon(ft.Icons.PERSON)) for p in ride.passengers]
            if ride.passengers
            else [ft.Text("No passengers booked yet.", color=ft.Colors.GREY_600)]
        )

        return ft.View(
            route=f"/ride/{ride_id}",
            appbar=ft.AppBar(
                title=ft.Text("Trip Details"),
                bgcolor=ft.Colors.TEAL,
                color=ft.Colors.WHITE,
            ),
            controls=[
                ft.Container(
                    padding=18,
                    expand=True,
                    content=ft.Column(
                        spacing=16,
                        controls=[
                            ft.Card(
                                content=ft.Container(
                                    padding=16,
                                    content=ft.Column(
                                        spacing=10,
                                        controls=[
                                            ft.Text("Route Information", size=18, weight=ft.FontWeight.BOLD),
                                            ft.Text(f"From: {ride.origin}", size=15),
                                            ft.Text(f"To: {ride.destination}", size=15),
                                            ft.Text(f"Departure: {ride.departure_time}", size=15),
                                            ft.Divider(),
                                            ft.Text(f"Driver: {ride.driver_name}", size=15),
                                            ft.Text(f"Vehicle: {ride.vehicle}", size=15),
                                            ft.Text(
                                                f"Seats: {ride.seats_available} of {ride.total_seats} available",
                                                weight=ft.FontWeight.W_600,
                                                color=ft.Colors.TEAL_800,
                                            ),
                                        ],
                                    ),
                                )
                            ),
                            ft.Text("Confirmed Passengers", size=16, weight=ft.FontWeight.BOLD),
                            ft.Row(wrap=True, spacing=8, controls=passenger_chips),
                            ft.Container(expand=True),
                            action_button,
                        ],
                    ),
                )
            ],
        )

    def my_trips_view() -> ft.View:
        user = state["current_user"]
        driving = [r for r in manager.rides if r.driver_name == user]
        booked = [r for r in manager.rides if user in r.passengers]

        return ft.View(
            route="/my-trips",
            appbar=ft.AppBar(
                title=ft.Text("My Trips"),
                bgcolor=ft.Colors.TEAL,
                color=ft.Colors.WHITE,
            ),
            navigation_bar=ft.NavigationBar(
                selected_index=1,
                on_change=lambda e: go("/" if e.control.selected_index == 0 else "/my-trips"),
                destinations=[
                    ft.NavigationBarDestination(icon=ft.Icons.EXPLORE, label="Find Rides"),
                    ft.NavigationBarDestination(icon=ft.Icons.BOOKMARK_ADDED, label="My Trips"),
                ],
            ),
            controls=[
                ft.Container(
                    padding=14,
                    expand=True,
                    content=ft.Column(
                        spacing=12,
                        scroll=ft.ScrollMode.AUTO,
                        controls=[
                            ft.Text("Booked Seats", size=17, weight=ft.FontWeight.BOLD),
                            *(
                                [build_ride_card(r) for r in booked]
                                if booked
                                else [ft.Text("You haven't booked any rides yet.", color=ft.Colors.GREY_600)]
                            ),
                            ft.Divider(),
                            ft.Text("Rides You're Driving", size=17, weight=ft.FontWeight.BOLD),
                            *(
                                [build_ride_card(r) for r in driving]
                                if driving
                                else [ft.Text("You haven't offered any rides yet.", color=ft.Colors.GREY_600)]
                            ),
                        ],
                    ),
                )
            ],
        )

    # --- Flet 1.0 Route & View Stack Management ---
    def route_change(e=None):
        page.views.clear()
        page.views.append(home_view())

        if page.route == "/offer":
            page.views.append(offer_ride_view())
        elif page.route == "/my-trips":
            page.views.append(my_trips_view())
        elif page.route.startswith("/ride/"):
            ride_id = page.route.split("/ride/")[1]
            page.views.append(ride_detail_view(ride_id))

        page.update()

    async def view_pop(e):
        if e.view is not None and len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            await page.push_route(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    route_change()


if __name__ == "__main__":
    ft.run(main)
