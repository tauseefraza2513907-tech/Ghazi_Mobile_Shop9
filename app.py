import sqlite3, urllib.parse, datetime
import pandas as pd
import streamlit as st

# ---------- SHOP SETTINGS (edit everything here) ----------
SHOP = {
    "name": "Ghazi Mobile Shop",
    "tagline": "New Mobiles | Accessories | Trusted Repairs",
    "whatsapp": "923099683921",  # with country code, no +
    "phone": "+92 309 9683921",
    "address": "Main Bazaar khaki lakhi , shorkot , jhang , Punjab",
    "hours": "Open daily 9 AM - 8 PM",
    "currency": "Rs.",
}
DB = "shop.db"

st.set_page_config(page_title=SHOP["name"], layout="wide")

# ---------- DESIGN (premium dark + gold) ----------
st.markdown("""
<style>
.stApp{background:#0b0d12;color:#e8e6e1}
[data-testid=stSidebar]{background:#11141b}
h1,h2,h3{color:#f2d27a!important;letter-spacing:.3px}
.hero{padding:56px 36px;border-radius:24px;margin-bottom:24px;
 background:linear-gradient(135deg,#1a1f2b 0%,#0b0d12 60%),radial-gradient(circle at 80% 20%,#c9a24b55,transparent 50%);
 border:1px solid #2a2f3d}
.hero h1{font-size:3rem;margin:0}
.hero p{color:#b9b6ad;font-size:1.15rem}
.card{background:#141822;border:1px solid #262b39;border-radius:18px;padding:16px;height:100%}
.card:hover{border-color:#c9a24b}
.pimg{height:150px;border-radius:12px;background:#1d2230;display:flex;align-items:center;
 justify-content:center;font-size:28px;font-weight:700;color:#f2d27a;overflow:hidden;margin-bottom:10px}
.pimg img{max-height:150px;max-width:100%}
.price{color:#f2d27a;font-size:1.3rem;font-weight:700}
.tag{font-size:.75rem;color:#9aa;border:1px solid #333;border-radius:20px;padding:2px 10px}
.stButton>button,.stFormSubmitButton>button{background:#c9a24b;color:#111;border:0;border-radius:10px;font-weight:700}
.stButton>button:hover{background:#f2d27a;color:#000}
</style>""", unsafe_allow_html=True)

# ---------- DATABASE ----------
def db():
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row; return c

def init_db():
    with db() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,brand TEXT,
            category TEXT,price INTEGER,stock INTEGER,descr TEXT,image TEXT);
        CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY AUTOINCREMENT,created TEXT,name TEXT,
            phone TEXT,address TEXT,items TEXT,total INTEGER,status TEXT DEFAULT 'New');
        CREATE TABLE IF NOT EXISTS repairs(id INTEGER PRIMARY KEY AUTOINCREMENT,created TEXT,name TEXT,
            phone TEXT,device TEXT,issue TEXT,status TEXT DEFAULT 'New');""")
        if c.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
            c.executemany("INSERT INTO products(name,brand,category,price,stock,descr,image) VALUES(?,?,?,?,?,?,?)", [
                ("Samsung Galaxy A55", "Samsung", "Mobile", 89999, 8, "8GB/256GB, AMOLED 120Hz, 5000mAh", ""),
                ("iPhone 13 (128GB)", "Apple", "Mobile", 169999, 3, "A15 Bionic, dual camera", ""),
                ("Redmi Note 13", "Xiaomi", "Mobile", 52999, 12, "6GB/128GB, 108MP camera", ""),
                ("Infinix Hot 40", "Infinix", "Mobile", 34999, 10, "8GB/256GB, 5000mAh", ""),
                ("20W Fast Charger", "Generic", "Accessories", 1499, 40, "Type-C, original quality", ""),
                ("Wireless Earbuds", "Generic", "Accessories", 2999, 25, "Bluetooth 5.3, 30-hour battery", ""),
                ("Tempered Glass", "Generic", "Accessories", 499, 100, "9H hardness, all models", ""),
                ("20000mAh Power Bank", "Generic", "Accessories", 4499, 15, "22.5W fast charging", ""),
            ])

def q(sql, args=()):
    with db() as c: return [dict(r) for r in c.execute(sql, args).fetchall()]

def run(sql, args=()):
    with db() as c: c.execute(sql, args)

def money(n): return f"{SHOP['currency']} {int(n):,}"
def now(): return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
def wa_link(text): return f"https://wa.me/{SHOP['whatsapp']}?text=" + urllib.parse.quote(text)
def admin_pw():
    try: return st.secrets["ADMIN_PASSWORD"]
    except Exception: return "admin123"  # change in secrets before deploying!

init_db()
st.session_state.setdefault("cart", {})
ICON = {"Mobile": "Mobile", "Accessories": "Accessory"}

# ---------- SIDEBAR ----------
st.sidebar.markdown(f"## {SHOP['name']}")
page = st.sidebar.radio("Menu", ["Home", "Shop", f"Cart ({sum(st.session_state.cart.values())})",
                                 "Repair Booking", "Contact", "Admin"], label_visibility="collapsed")
st.sidebar.caption(f"{SHOP['hours']}")

# ---------- HOME ----------
if page == "Home":
    st.markdown(f"""<div class="hero"><h1>{SHOP['name']}</h1><p>{SHOP['tagline']}</p></div>""", unsafe_allow_html=True)
    a, b, c = st.columns(3)
    a.markdown("### 100% Original\nWarranty on all phones")
    b.markdown("### Fast Repairs\nScreen, battery, software")
    c.markdown("### WhatsApp Orders\nTalk to the shop directly")
    st.subheader("New Arrivals")
    items = q("SELECT * FROM products WHERE stock>0 ORDER BY id DESC LIMIT 4")
    for col, p in zip(st.columns(4), items):
        col.markdown(f"""<div class="card"><div class="pimg">{ICON.get(p['category'], 'Item')}</div>
        <b>{p['name']}</b><br><span class="price">{money(p['price'])}</span></div>""", unsafe_allow_html=True)

# ---------- SHOP ----------
elif page == "Shop":
    st.title("Shop")
    c1, c2, c3 = st.columns([2, 1, 1])
    search = c1.text_input("Search", placeholder="mobile, charger...")
    cats = ["All"] + [r["category"] for r in q("SELECT DISTINCT category FROM products")]
    cat = c2.selectbox("Category", cats)
    sort = c3.selectbox("Sort by", ["Newest first", "Price: low to high", "Price: high to low"])
    rows = q("SELECT * FROM products")
    if cat != "All": rows = [r for r in rows if r["category"] == cat]
    if search: rows = [r for r in rows if search.lower() in (r["name"] + r["brand"]).lower()]
    if sort == "Price: low to high": rows.sort(key=lambda r: r["price"])
    elif sort == "Price: high to low": rows.sort(key=lambda r: -r["price"])
    else: rows.sort(key=lambda r: -r["id"])
    if not rows: st.info("No products found.")
    for i in range(0, len(rows), 3):
        for col, p in zip(st.columns(3), rows[i:i + 3]):
            with col:
                img = f"<img src='{p['image']}'>" if p["image"] else ICON.get(p["category"], "Item")
                st.markdown(f"""<div class="card"><div class="pimg">{img}</div>
                <span class="tag">{p['brand']}</span><br><b>{p['name']}</b><br>
                <small style="color:#9aa">{p['descr']}</small><br>
                <span class="price">{money(p['price'])}</span></div>""", unsafe_allow_html=True)
                if p["stock"] > 0:
                    if st.button("Add to cart", key=f"add{p['id']}"):
                        cart = st.session_state.cart
                        cart[p["id"]] = min(cart.get(p["id"], 0) + 1, p["stock"])
                        st.toast(f"{p['name']} added ")
                else: st.button("Out of stock", key=f"oos{p['id']}", disabled=True)

# ---------- CART ----------
elif page.startswith("Cart"):
    st.title("Your Cart")
    cart = st.session_state.cart
    if not cart: st.info("Your cart is empty. Pick something from the shop.")
    else:
        total, lines = 0, []
        for pid, qty in list(cart.items()):
            p = q("SELECT * FROM products WHERE id=?", (pid,))[0]
            a, b, c = st.columns([4, 2, 1])
            a.write(f"**{p['name']}**"); b.write(f"{qty} x {money(p['price'])}")
            if c.button("Remove", key=f"rm{pid}"): del cart[pid]; st.rerun()
            total += qty * p["price"]; lines.append(f"{p['name']} x{qty}")
        st.markdown(f"### Total: <span class='price'>{money(total)}</span>", unsafe_allow_html=True)
        with st.form("checkout"):
            name = st.text_input("Name"); phone = st.text_input("Phone number")
            addr = st.text_area("Address (or write 'Pickup from shop')")
            if st.form_submit_button("Place order"):
                if not (name and phone): st.error("Name and phone are required.")
                else:
                    run("INSERT INTO orders(created,name,phone,address,items,total) VALUES(?,?,?,?,?,?)",
                        (now(), name, phone, addr, "; ".join(lines), total))
                    for pid, qty in cart.items(): run("UPDATE products SET stock=stock-? WHERE id=?", (qty, pid))
                    msg = f"New order\nName: {name}\nPhone: {phone}\nItems: {', '.join(lines)}\nTotal: {money(total)}\nAddress: {addr}"
                    st.session_state.cart = {}
                    st.success("Order saved! Send it on WhatsApp to confirm ")
                    st.link_button("Send on WhatsApp", wa_link(msg))

# ---------- REPAIR ----------
elif page == "Repair Booking":
    st.title("Repair Booking")
    with st.form("repair"):
        name = st.text_input("Name"); phone = st.text_input("Phone number")
        device = st.text_input("Phone model (e.g. Redmi Note 10)")
        issue = st.selectbox("Problem", ["Broken screen", "Battery", "Charging port", "Software / hanging",
                                         "Water damage", "Speaker / mic", "Other"])
        note = st.text_area("More details")
        if st.form_submit_button("Book repair"):
            if name and phone and device:
                run("INSERT INTO repairs(created,name,phone,device,issue) VALUES(?,?,?,?,?)",
                    (now(), name, phone, device, f"{issue} - {note}"))
                st.success("Repair request received. We will call you soon.")
                st.link_button("Tell us on WhatsApp", wa_link(f"Repair: {device}, problem: {issue}. Name: {name}"))
            else: st.error("Please fill in name, phone and model.")

# ---------- CONTACT ----------
elif page == "Contact":
    st.title("Contact")
    st.markdown(f"**Address:** {SHOP['address']}  \n**Phone:** {SHOP['phone']}  \n**Hours:** {SHOP['hours']}")
    st.link_button("Chat on WhatsApp", wa_link("Hello, I need some information."))
    st.map(pd.DataFrame({"lat": [30.8333], "lon": [72.1167]}))  # put your shop's exact location here

# ---------- ADMIN ----------
def admin_pw():
    return "Admin123"

    st.title("Admin Panel")

    if not st.session_state.get("admin"):
        pw = st.text_input("Password", type="password")

        if st.button("Login"):
            if pw == admin_pw():
                st.session_state.admin = True
                st.rerun()
            else:
                st.error("Wrong password")
    else:
        t1, t2, t3 = st.tabs(["Orders", "Repairs", "Products"])
        with t1:
            o = pd.DataFrame(q("SELECT * FROM orders ORDER BY id DESC"))
            st.metric("Total sales", money(o["total"].sum() if len(o) else 0))
            st.dataframe(o, use_container_width=True)
            oid = st.number_input("Order ID", 0, step=1, key="oid")
            ost = st.selectbox("Status", ["New", "Confirmed", "Delivered", "Cancelled"], key="ost")
            if st.button("Update order"): run("UPDATE orders SET status=? WHERE id=?", (ost, oid)); st.rerun()
        with t2:
            st.dataframe(pd.DataFrame(q("SELECT * FROM repairs ORDER BY id DESC")), use_container_width=True)
            rid = st.number_input("Repair ID", 0, step=1, key="rid")
            rst = st.selectbox("Status", ["New", "In Progress", "Ready", "Delivered"], key="rst")
            if st.button("Update repair"): run("UPDATE repairs SET status=? WHERE id=?", (rst, rid)); st.rerun()
        with t3:
            with st.form("addp"):
                n = st.text_input("Name"); br = st.text_input("Brand")
                ct = st.selectbox("Category", ["Mobile", "Accessories", "Other"])
                pr = st.number_input("Price", 0, step=100); stk = st.number_input("Stock", 0, step=1)
                ds = st.text_input("Description"); im = st.text_input("Image URL (optional)")
                if st.form_submit_button("Add product") and n:
                    run("INSERT INTO products(name,brand,category,price,stock,descr,image) VALUES(?,?,?,?,?,?,?)",
                        (n, br, ct, pr, stk, ds, im)); st.rerun()
            edited = st.data_editor(pd.DataFrame(q("SELECT * FROM products")), num_rows="dynamic",
                                    use_container_width=True, key="pe")
            if st.button("Save changes"):
                with db() as c:
                    c.execute("DELETE FROM products")
                    for _, r in edited.dropna(subset=["name"]).iterrows():
                        c.execute("INSERT INTO products(name,brand,category,price,stock,descr,image) VALUES(?,?,?,?,?,?,?)",
                                  (r["name"], r["brand"], r["category"], int(r["price"] or 0), int(r["stock"] or 0),
                                   r["descr"] or "", r["image"] or ""))
                st.success("Saved"); st.rerun()
        if st.button("Logout"): st.session_state.admin = False; st.rerun()
