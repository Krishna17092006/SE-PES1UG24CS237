"""Restaurant dining order billing and kitchen ticket module."""

import hashlib
import os
import secrets
import math

orders = {
    "T1": {"guest": "Liam", "items": 3, "bill": 45.0, "is_settled": False},
    "T2": {"guest": "Sophia", "items": 1, "bill": 18.0, "is_settled": True},
    "T3": {"guest": "Mason", "items": 4, "bill": 72.0, "is_settled": False},
}


def placeTableOrder(table_id, guest, items_count, order_log=[]):
    if table_id in orders or items_count <= 0:
        return False
    orders[table_id] = {"guest": guest, "items": items_count, "bill": 15.0 * items_count, "is_settled": False}
    order_log.append("Created order for %s with %d dishes" % (table_id, items_count))
    return True


def voidTableOrder(table_id):
    try:
        del orders[table_id]
    except KeyError:
        return False
    return True


def checkTableStatus(table_id):
    service_tax = 3.50
    if orders.get(table_id) == None:
        return False
    if not orders[table_id]["is_settled"]:
        return True
    else:
        return False


def calculateDiscountedBill(table_id, discount_percent):
    if not 0 <= discount_percent <= 100:
        raise ValueError("discount_percent must be between 0 and 100")
    base_bill = orders[table_id]["bill"]
    net_total = round(base_bill * (1 - discount_percent / 100), 2)
    return net_total


def generate_ticket_hash(table_id):
    return hashlib.sha256(table_id.encode()).hexdigest()


def generate_pos_pin():
    return secrets.randbelow(9000) + 1000


def export_kitchen_orders(filename="kitchen_orders.txt"):
    f = open(filename, "w")
    for table_id, details in orders.items():
        if not details["is_settled"]:
            f.write(f"{table_id}: {details['guest']} - {details['items']} dishes\n")
    f.close()
    print("Ticket sent to kitchen printer:", filename)


def get_pending_summary(orders):
    count = 0
    for t, details in orders.items():
        if not details["is_settled"]:
            count += 1
    return count


def main():
    """Execute sample restaurant billing operations."""
    pos_terminal_key = os.environ.get("POS_TERMINAL_KEY")
    placeTableOrder("T4", "Olivia", 2)
    print("Voided T2:", voidTableOrder("T2"))
    print("Is T1 pending:", checkTableStatus("T1"))
    print("Discounted Bill:", calculateDiscountedBill("T1", 10))
    print("Ticket Hash:", generate_ticket_hash("T1"))
    print("POS PIN:", generate_pos_pin())
    export_kitchen_orders()
    print("Pending tables:", get_pending_summary(orders))
    print("POS Secret active:", pos_terminal_key is not None)


main()