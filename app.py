import streamlit as st
import sqlite3
import pandas as pd
import urllib.parse
from datetime import date

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="Jeyasri Mustard Yellow Boutique",
    layout="wide"
)

# ---------------- CUSTOM COLORS ----------------

st.markdown("""
<style>

.main {
    background-color: #fffdf5;
}

.stButton>button {
    background-color: #f4b400;
    color: black;
    border-radius: 8px;
    font-weight: bold;
}

.stButton>button:hover {
    background-color: #e09e00;
}

</style>
""", unsafe_allow_html=True)

# ---------------- DATABASE ----------------

conn = sqlite3.connect("boutique.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS customers(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
phone TEXT UNIQUE)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders(
id INTEGER PRIMARY KEY AUTOINCREMENT,
customer_id INTEGER,
dress_type TEXT,
measurement TEXT,
notes TEXT,
status TEXT,
delivery_date TEXT,
amount REAL)
""")

conn.commit()

# ---------------- HEADER ----------------

col1,col2=st.columns([1,4])

with col1:
    try:
        st.image("logo.png",width=120)
    except:
        pass

with col2:
    try:
        st.image("banner.png",use_container_width=True)
    except:
        st.title("Jeyasri Mustard Yellow Boutique")

# ---------------- SIDEBAR ----------------

st.sidebar.title("Menu")

page=st.sidebar.radio("Navigation",[
"Dashboard",
"Add Customer / Order",
"Today Deliveries",
"Pending Orders",
"View Customers"
])

# ---------------- MEASUREMENT AUTO FILL ----------------

def get_old_measurement(customer_id,dress):

    old=cursor.execute("""
    SELECT measurement FROM orders
    WHERE customer_id=? AND dress_type=?
    ORDER BY id DESC LIMIT 1
    """,(customer_id,dress)).fetchone()

    if old:
        try:
            return eval(old[0])
        except:
            return {}
    return {}

def field(label,old,key_prefix=""):

    return st.text_input(
        label,
        value=old.get(label,""),
        key=key_prefix+label
    )

# ---------------- NEW ORDER MEASUREMENT ----------------

def measurement_form(dress,customer_id):

    old=get_old_measurement(customer_id,dress)

    data={}

    if dress=="Blouse":

        data["Bust"]=field("Bust",old,"new_")
        data["Waist"]=field("Waist",old,"new_")
        data["Shoulder"]=field("Shoulder",old,"new_")
        data["Sleeve"]=field("Sleeve",old,"new_")
        data["Length"]=field("Length",old,"new_")
        data["Front Neck"]=field("Front Neck",old,"new_")
        data["Back Neck"]=field("Back Neck",old,"new_")

    elif dress=="Chudi":

        data["Bust"]=field("Bust",old,"new_")
        data["Waist"]=field("Waist",old,"new_")
        data["Hip"]=field("Hip",old,"new_")
        data["Shoulder"]=field("Shoulder",old,"new_")
        data["Sleeve"]=field("Sleeve",old,"new_")
        data["Top Length"]=field("Top Length",old,"new_")
        data["Bottom Length"]=field("Bottom Length",old,"new_")

    elif dress=="Lehenga":

        data["Waist"]=field("Waist",old,"new_")
        data["Hip"]=field("Hip",old,"new_")
        data["Length"]=field("Length",old,"new_")

    elif dress=="Frock":

        data["Bust"]=field("Bust",old,"new_")
        data["Waist"]=field("Waist",old,"new_")
        data["Length"]=field("Length",old,"new_")

    return str(data)

# ---------------- EDIT MEASUREMENT ----------------

def edit_measurement_form(dress,measurement_str):

    try:
        old=eval(measurement_str)
    except:
        old={}

    data={}

    if dress=="Blouse":

        data["Bust"]=field("Bust",old,"edit_")
        data["Waist"]=field("Waist",old,"edit_")
        data["Shoulder"]=field("Shoulder",old,"edit_")
        data["Sleeve"]=field("Sleeve",old,"edit_")
        data["Length"]=field("Length",old,"edit_")
        data["Front Neck"]=field("Front Neck",old,"edit_")
        data["Back Neck"]=field("Back Neck",old,"edit_")

    elif dress=="Chudi":

        data["Bust"]=field("Bust",old,"edit_")
        data["Waist"]=field("Waist",old,"edit_")
        data["Hip"]=field("Hip",old,"edit_")
        data["Top Length"]=field("Top Length",old,"edit_")
        data["Bottom Length"]=field("Bottom Length",old,"edit_")

    elif dress=="Lehenga":

        data["Waist"]=field("Waist",old,"edit_")
        data["Hip"]=field("Hip",old,"edit_")
        data["Length"]=field("Length",old,"edit_")

    elif dress=="Frock":

        data["Bust"]=field("Bust",old,"edit_")
        data["Waist"]=field("Waist",old,"edit_")
        data["Length"]=field("Length",old,"edit_")

    return str(data)

# ---------------- DASHBOARD ----------------

if page=="Dashboard":

    st.title("Dashboard")

    total_customers=cursor.execute(
    "SELECT COUNT(*) FROM customers").fetchone()[0]

    total_orders=cursor.execute(
    "SELECT COUNT(*) FROM orders").fetchone()[0]

    pending=cursor.execute(
    "SELECT COUNT(*) FROM orders WHERE status='Pending'").fetchone()[0]

    today_count=cursor.execute("""
    SELECT COUNT(*) FROM orders WHERE delivery_date=date('now')
    """).fetchone()[0]

    revenue=cursor.execute("""
    SELECT SUM(amount) FROM orders
    """).fetchone()[0]

    if revenue is None:
        revenue=0

    c1,c2,c3,c4=st.columns(4)

    c1.metric("Customers",total_customers)
    c2.metric("Orders",total_orders)
    c3.metric("Pending",pending)
    c4.metric("Revenue ₹",revenue)

# ---------------- ADD ORDER ----------------

elif page=="Add Customer / Order":

    st.title("Add Customer / Order")

    phone=st.text_input("Phone Number")

    if phone and len(phone)==10:

        customer=cursor.execute(
        "SELECT * FROM customers WHERE phone=?",(phone,)
        ).fetchone()

        if customer:

            st.success("Existing Customer: "+customer[1])
            customer_id=customer[0]

        else:

            name=st.text_input("Customer Name")

            if st.button("Create Customer"):

                cursor.execute(
                "INSERT INTO customers(name,phone) VALUES(?,?)",
                (name,phone))

                conn.commit()
                st.rerun()

        if customer:

            dress=st.selectbox(
            "Dress Type",
            ["Blouse","Chudi","Lehenga","Frock"]
            )

            measurement=measurement_form(dress,customer_id)

            notes=st.text_area("Notes")

            status=st.selectbox(
            "Status",
            ["Pending","Stitching","Ready","Delivered"]
            )

            delivery=st.date_input("Delivery Date")

            amount=st.number_input("Amount")

            if st.button("Add Dress"):

                cursor.execute("""
                INSERT INTO orders
                (customer_id,dress_type,measurement,
                notes,status,delivery_date,amount)
                VALUES(?,?,?,?,?,?,?)
                """,
                (
                customer_id,
                dress,
                measurement,
                notes,
                status,
                delivery,
                amount
                ))

                conn.commit()

                st.success("Dress Added")

# ---------------- VIEW CUSTOMERS WITH EDIT ----------------

elif page=="View Customers":

    st.title("Customers")

    customers=pd.read_sql(
    "SELECT * FROM customers",
    conn
    )

    for i,customer in customers.iterrows():

        st.subheader(customer["name"])
        st.write(customer["phone"])

        orders=pd.read_sql(
        f"SELECT * FROM orders WHERE customer_id={customer['id']}",
        conn)

        for j,order in orders.iterrows():

            st.markdown(f"""
Dress: {order['dress_type']}  
Measurement: {order['measurement']}  
Notes: {order['notes']}  
Status: {order['status']}  
Delivery: {order['delivery_date']}  
Amount: ₹{order['amount']}
""")

            msg=f"""
Dear {customer['name']},

Your {order['dress_type']} is Ready.

Jeyasri Mustard Yellow Boutique
"""

            sms=f"sms:{customer['phone']}?body={urllib.parse.quote(msg)}"

            col1,col2=st.columns(2)

            with col1:
                st.link_button("Send SMS",sms)

            with col2:
                if st.button("Edit Order",key="edit"+str(order["id"])):
                    st.session_state.edit_id=order["id"]

            if st.session_state.get("edit_id")==order["id"]:

                st.subheader("Edit Order")

                new_measurement=edit_measurement_form(
                    order["dress_type"],
                    order["measurement"]
                )

                new_notes=st.text_area(
                    "Edit Notes",
                    value=order["notes"]
                )

                new_status=st.selectbox(
                    "Edit Status",
                    ["Pending","Stitching","Ready","Delivered"]
                )

                new_amount=st.number_input(
                    "Edit Amount",
                    value=float(order["amount"])
                )

                new_delivery=st.date_input(
                    "Edit Delivery",
                    value=pd.to_datetime(order["delivery_date"])
                )

                if st.button("Save Changes",key="save"+str(order["id"])):

                    cursor.execute("""
                    UPDATE orders SET
                    measurement=?,
                    notes=?,
                    status=?,
                    amount=?,
                    delivery_date=?
                    WHERE id=?
                    """,
                    (
                    new_measurement,
                    new_notes,
                    new_status,
                    new_amount,
                    new_delivery,
                    order["id"]
                    ))

                    conn.commit()

                    st.success("Updated Successfully")

                    del st.session_state.edit_id

                    st.rerun()

            st.divider()
