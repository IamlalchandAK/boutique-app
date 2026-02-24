import streamlit as st
import sqlite3
import pandas as pd
import urllib.parse

# CONFIG
st.set_page_config(page_title="Jeyasri Mustard Yellow", layout="wide")

# DATABASE
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

# HEADER
col1,col2=st.columns([1,4])
with col1:
    try: st.image("logo.png",width=120)
    except: pass
with col2:
    try: st.image("banner.png",use_container_width=True)
    except: pass

# SIDEBAR
st.sidebar.title("Menu")
page=st.sidebar.radio("Navigation",
["Dashboard","Add Customer / Order","View Customers"])


# MEASUREMENT FORM (EXTENDED ONLY)
def measurement_form(dress):

    data={}

    if dress=="Blouse":
        data["Bust"]=st.text_input("Bust")
        data["Waist"]=st.text_input("Waist")
        data["Shoulder"]=st.text_input("Shoulder")
        data["Sleeve Length"]=st.text_input("Sleeve Length")
        data["Blouse Length"]=st.text_input("Blouse Length")
        data["Front Neck"]=st.text_input("Front Neck Depth")
        data["Back Neck"]=st.text_input("Back Neck Depth")

    elif dress=="Chudi":
        data["Bust"]=st.text_input("Bust")
        data["Waist"]=st.text_input("Waist")
        data["Hip"]=st.text_input("Hip")
        data["Shoulder"]=st.text_input("Shoulder")
        data["Sleeve Length"]=st.text_input("Sleeve Length")
        data["Top Length"]=st.text_input("Top Length")
        data["Bottom Length"]=st.text_input("Bottom Length")

    elif dress=="Saree Blouse":
        data["Bust"]=st.text_input("Bust")
        data["Waist"]=st.text_input("Waist")
        data["Shoulder"]=st.text_input("Shoulder")
        data["Sleeve Length"]=st.text_input("Sleeve Length")
        data["Length"]=st.text_input("Length")
        data["Front Neck"]=st.text_input("Front Neck")
        data["Back Neck"]=st.text_input("Back Neck")

    elif dress=="Princess Cut Blouse":
        data["Bust"]=st.text_input("Bust")
        data["Waist"]=st.text_input("Waist")
        data["Shoulder"]=st.text_input("Shoulder")
        data["Length"]=st.text_input("Length")
        data["Cup Size"]=st.text_input("Cup Size")

    elif dress=="Lehenga":
        data["Waist"]=st.text_input("Waist")
        data["Hip"]=st.text_input("Hip")
        data["Length"]=st.text_input("Lehenga Length")
        data["Flare"]=st.text_input("Flare")

    elif dress=="Frock":
        data["Bust"]=st.text_input("Bust")
        data["Waist"]=st.text_input("Waist")
        data["Hip"]=st.text_input("Hip")
        data["Shoulder"]=st.text_input("Shoulder")
        data["Length"]=st.text_input("Frock Length")

    elif dress=="Nighty":
        data["Bust"]=st.text_input("Bust")
        data["Hip"]=st.text_input("Hip")
        data["Shoulder"]=st.text_input("Shoulder")
        data["Length"]=st.text_input("Nighty Length")

    elif dress=="Skirt":
        data["Waist"]=st.text_input("Waist")
        data["Hip"]=st.text_input("Hip")
        data["Length"]=st.text_input("Skirt Length")

    elif dress=="Pant":
        data["Waist"]=st.text_input("Waist")
        data["Hip"]=st.text_input("Hip")
        data["Thigh"]=st.text_input("Thigh")
        data["Knee"]=st.text_input("Knee")
        data["Length"]=st.text_input("Pant Length")

    elif dress=="Sharara":
        data["Waist"]=st.text_input("Waist")
        data["Hip"]=st.text_input("Hip")
        data["Length"]=st.text_input("Sharara Length")

    elif dress=="Palazzo":
        data["Waist"]=st.text_input("Waist")
        data["Hip"]=st.text_input("Hip")
        data["Length"]=st.text_input("Palazzo Length")

    return str(data)



# DASHBOARD
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
        st.subheader("Customers Table")
        search=st.text_input("Search Customer")
        query="SELECT * FROM customers"
        if search:
            query+=f" WHERE name LIKE '%{search}%' OR phone LIKE '%{search}%'"
        df=pd.read_sql(query,conn)
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



# ADD CUSTOMER / ORDER
elif page=="Add Customer / Order":

    st.title("Add Customer / Order")

    phone=st.text_input("Phone Number")

    if phone and len(phone)==10 and phone.isdigit():

        customer=cursor.execute(
        "SELECT * FROM customers WHERE phone=?",(phone,)
        ).fetchone()

        if customer:
            st.success(f"Existing Customer: {customer[1]}")
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
            [
            "Blouse",
            "Chudi",
            "Saree Blouse",
            "Princess Cut Blouse",
            "Lehenga",
            "Frock",
            "Nighty",
            "Skirt",
            "Pant",
            "Sharara",
            "Palazzo"
            ])

            measurement=measurement_form(dress)

            notes=st.text_area("Notes")

            status=st.selectbox(
            "Status",["Pending","Stitching","Ready","Delivered"])

            delivery=st.date_input("Delivery Date")

            amount=st.number_input("Amount")

            if st.button("Add Dress"):

                duplicate=cursor.execute("""
                SELECT * FROM orders
                WHERE customer_id=? AND dress_type=? AND delivery_date=?""",
                (customer_id,dress,str(delivery))).fetchone()

                if duplicate:
                    st.warning("Duplicate prevented")

                else:
                    cursor.execute("""
                    INSERT INTO orders
                    (customer_id,dress_type,measurement,notes,status,delivery_date,amount)
                    VALUES(?,?,?,?,?,?,?)""",
                    (customer_id,dress,measurement,notes,status,delivery,amount))

                    conn.commit()
                    st.success("Dress Added")



# VIEW CUSTOMERS (UNCHANGED)
elif page=="View Customers":

    st.title("Customers")

    search=st.text_input("Search Customer")

    query="SELECT * FROM customers"
    if search:
        query+=f" WHERE name LIKE '%{search}%' OR phone LIKE '%{search}%'"

    customers=pd.read_sql(query,conn)

    for i,customer in customers.iterrows():

        st.subheader(customer["name"])
        st.write(customer["phone"])

        if st.button("Delete Customer",key=f"dc{customer['id']}"):

            cursor.execute(
            "DELETE FROM orders WHERE customer_id=?",
            (customer["id"],))

            cursor.execute(
            "DELETE FROM customers WHERE id=?",
            (customer["id"],))

            conn.commit()
            st.rerun()

        orders=pd.read_sql(
        f"SELECT * FROM orders WHERE customer_id={customer['id']}",
        conn)

        for j,order in orders.iterrows():

            st.markdown(f"""
            **Dress:** {order['dress_type']}  
            **Measurement:** {order['measurement']}  
            **Notes:** {order['notes']}  
            **Status:** {order['status']}  
            **Delivery:** {order['delivery_date']}  
            **Amount:** ₹{order['amount']}
            """)

            col1,col2,col3=st.columns(3)

            with col1:

                new_status=st.selectbox(
                "Update Status",
                ["Pending","Stitching","Ready","Delivered"],
                key=f"status{order['id']}")

                if st.button("Update",key=f"update{order['id']}"):

                    cursor.execute(
                    "UPDATE orders SET status=? WHERE id=?",
                    (new_status,order["id"]))

                    conn.commit()
                    st.success("Updated")

            with col2:

                if st.button("Delete Order",
                key=f"delete{order['id']}"):

                    cursor.execute(
                    "DELETE FROM orders WHERE id=?",
                    (order["id"],))

                    conn.commit()
                    st.rerun()

            with col3:

                msg=f"""
Dear {customer['name']},

Your {order['dress_type']} is Ready.
Collect between 10AM - 6PM

Jeyasri Mustard Yellow
"""

                sms=f"sms:{customer['phone']}?body={urllib.parse.quote(msg)}"

                st.link_button("Send SMS",sms)

        st.divider()
