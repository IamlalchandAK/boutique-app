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
background-color:#fffdf5;
}

.stButton>button {
background-color:#f4b400;
color:black;
border-radius:8px;
font-weight:bold;
height:60px;
}

.stButton>button:hover {
background-color:#e09e00;
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

col1,col2=st.columns([1,5])

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

# ---------------- MEASUREMENT ----------------

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

def field(label,old,key):
    return st.text_input(label,value=old.get(label,""),key=key)

def measurement_form(dress,customer_id):

    old=get_old_measurement(customer_id,dress)

    data={}

    if dress=="Blouse":

        data["Bust"]=field("Bust",old,"b1")
        data["Waist"]=field("Waist",old,"b2")
        data["Shoulder"]=field("Shoulder",old,"b3")
        data["Sleeve"]=field("Sleeve",old,"b4")
        data["Length"]=field("Length",old,"b5")

    elif dress=="Chudi":

        data["Bust"]=field("Bust",old,"c1")
        data["Waist"]=field("Waist",old,"c2")
        data["Hip"]=field("Hip",old,"c3")
        data["Top Length"]=field("Top Length",old,"c4")

    elif dress=="Lehenga":

        data["Waist"]=field("Waist",old,"l1")
        data["Hip"]=field("Hip",old,"l2")
        data["Length"]=field("Length",old,"l3")

    elif dress=="Frock":

        data["Bust"]=field("Bust",old,"f1")
        data["Waist"]=field("Waist",old,"f2")
        data["Length"]=field("Length",old,"f3")

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

    ready=cursor.execute(
    "SELECT COUNT(*) FROM orders WHERE status='Ready'").fetchone()[0]

    stitching=cursor.execute(
    "SELECT COUNT(*) FROM orders WHERE status='Stitching'").fetchone()[0]

    revenue=cursor.execute(
    "SELECT SUM(amount) FROM orders").fetchone()[0]

    if revenue is None:
        revenue=0

    # METRICS
    c1,c2,c3,c4,c5=st.columns(5)

    if c1.button(f"Customers\n{total_customers}"):
        st.session_state.view="customers"

    if c2.button(f"Orders\n{total_orders}"):
        st.session_state.view="orders"

    if c3.button(f"Pending\n{pending}"):
        st.session_state.view="pending"

    if c4.button(f"Stitching\n{stitching}"):
        st.session_state.view="stitching"

    if c5.button(f"Ready\n{ready}"):
        st.session_state.view="ready"

    view=st.session_state.get("view")

    if view=="customers":

        df=pd.read_sql("SELECT * FROM customers",conn)
        st.dataframe(df,use_container_width=True)

    elif view=="orders":

        df=pd.read_sql("""
        SELECT customers.name,customers.phone,
        orders.dress_type,orders.status,
        orders.delivery_date,orders.amount
        FROM orders
        JOIN customers ON customers.id=orders.customer_id
        """,conn)

        st.dataframe(df,use_container_width=True)

    elif view=="pending":

        df=pd.read_sql("""
        SELECT * FROM orders WHERE status='Pending'
        """,conn)

        st.dataframe(df)

    elif view=="stitching":

        df=pd.read_sql("""
        SELECT * FROM orders WHERE status='Stitching'
        """,conn)

        st.dataframe(df)

    elif view=="ready":

        df=pd.read_sql("""
        SELECT * FROM orders WHERE status='Ready'
        """,conn)

        st.dataframe(df)

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
                (customer_id,dress,measurement,
                notes,status,delivery,amount))

                conn.commit()

                st.success("Order Added")

# ---------------- TODAY DELIVERY ----------------

elif page=="Today Deliveries":

    st.title("Today's Deliveries")

    df=pd.read_sql("""
    SELECT customers.name,customers.phone,
    orders.dress_type,orders.status,
    orders.delivery_date,orders.amount
    FROM orders
    JOIN customers ON customers.id=orders.customer_id
    WHERE delivery_date=date('now')
    """,conn)

    st.dataframe(df,use_container_width=True)

# ---------------- PENDING ----------------

elif page=="Pending Orders":

    st.title("Pending Orders")

    df=pd.read_sql("""
    SELECT customers.name,customers.phone,
    orders.dress_type,orders.status,
    orders.delivery_date,orders.amount
    FROM orders
    JOIN customers ON customers.id=orders.customer_id
    WHERE status!='Delivered'
    """,conn)

    st.dataframe(df,use_container_width=True)

# ---------------- VIEW CUSTOMERS ----------------

elif page=="View Customers":

    st.title("Customers")

    customers=pd.read_sql("SELECT * FROM customers",conn)

    for i,customer in customers.iterrows():

        st.subheader(customer["name"])
        st.write(customer["phone"])

        orders=pd.read_sql(
        f"SELECT * FROM orders WHERE customer_id={customer['id']}",
        conn)

        for j,order in orders.iterrows():

            st.write(order["dress_type"],
            order["status"],
            order["delivery_date"],
            order["amount"])

            new_status=st.selectbox(
            "Update Status",
            ["Pending","Stitching","Ready","Delivered"],
            key="s"+str(order["id"]))

            if st.button("Update",key="u"+str(order["id"])):

                cursor.execute(
                "UPDATE orders SET status=? WHERE id=?",
                (new_status,order["id"]))

                conn.commit()
                st.rerun()

            msg=f"Your {order['dress_type']} is Ready"

            sms=f"sms:{customer['phone']}?body={urllib.parse.quote(msg)}"

            st.link_button("Send SMS",sms)

            st.divider()
