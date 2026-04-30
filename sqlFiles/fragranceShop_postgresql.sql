-- Table 1: CUSTOMER
CREATE TABLE IF NOT EXISTS CUSTOMER (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    middle_name VARCHAR(50),
    last_name VARCHAR(50) NOT NULL,
    DOB DATE NOT NULL,
    gender VARCHAR(10) NOT NULL CHECK (gender IN ('Male', 'Female')),
    email_address VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- Table 2: PHONE_NUMBERS
CREATE TABLE IF NOT EXISTS PHONE_NUMBERS (
    customer_id INT NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    PRIMARY KEY(phone_number),
    FOREIGN KEY(customer_id) REFERENCES CUSTOMER(customer_id) ON DELETE CASCADE
);

-- Table 3: ADDRESSES
CREATE TABLE IF NOT EXISTS ADDRESSES (
    address_id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    house VARCHAR(100) NOT NULL,
    street_name VARCHAR(100) NOT NULL,
    town_city VARCHAR(50) NOT NULL,
    county VARCHAR(50) NOT NULL,
    postcode VARCHAR(20) NOT NULL,
    country VARCHAR(50) NOT NULL CHECK (country IN ('England', 'Scotland', 'Wales', 'Northern Ireland')),
    FOREIGN KEY(customer_id) REFERENCES CUSTOMER(customer_id) ON DELETE CASCADE
);

-- Table 4: DISCOUNT_RATE
CREATE TABLE IF NOT EXISTS DISCOUNT_RATE (
    member_type VARCHAR(50) PRIMARY KEY,
    discount_rate REAL NOT NULL CHECK (member_type IN ('Standard', 'Premium', 'Student'))
);

-- Table 5: MEMBERSHIP
CREATE TABLE IF NOT EXISTS MEMBERSHIP (
    member_id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    member_type VARCHAR(50) NOT NULL,
    end_ren_date DATE,
    FOREIGN KEY(customer_id) REFERENCES CUSTOMER(customer_id) ON DELETE CASCADE,
    FOREIGN KEY(member_type) REFERENCES DISCOUNT_RATE(member_type)
);

-- Table 6: GIFT_CARDS
CREATE TABLE IF NOT EXISTS GIFT_CARDS (
    gift_card_num SERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    amount REAL NOT NULL,
    issue_date DATE NOT NULL,
    exp_date DATE NOT NULL,
    redeemed_status BOOLEAN NOT NULL,
    FOREIGN KEY(customer_id) REFERENCES CUSTOMER(customer_id) ON DELETE CASCADE
);

-- Table 7: PRODUCTS
CREATE TABLE IF NOT EXISTS PRODUCTS (
    product_id SERIAL PRIMARY KEY,
    brand VARCHAR(50) NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    price REAL NOT NULL,
    gift BOOLEAN NOT NULL
);

-- Table 8: PERSONAL_FRAGRANCES
CREATE TABLE IF NOT EXISTS PERSONAL_FRAGRANCES (
    product_id INT NOT NULL,
    size VARCHAR(20) NOT NULL,
    fragrance_family VARCHAR(50) NOT NULL CHECK (fragrance_family IN ('Floral', 'Oriental', 'Woody', 'Fresh', 'Citrus', 'Chypre')),
    gender VARCHAR(10) NOT NULL,
    strength VARCHAR(20) NOT NULL CHECK (strength IN ('Eau de Parfum', 'Eau de Toilette', 'Parfum')),
    engraving VARCHAR(100),
    PRIMARY KEY(product_id, size),
    FOREIGN KEY(product_id) REFERENCES PRODUCTS(product_id) ON DELETE CASCADE
);

-- Table 9: HOME_FRAGRANCES
CREATE TABLE IF NOT EXISTS HOME_FRAGRANCES (
    product_id INT PRIMARY KEY,
    product_type VARCHAR(50) NOT NULL CHECK (product_type IN ('Scent Diffuser', 'Air Freshener', 'Scented Candles', 'Room Sprays', 'Reed Diffusers')),
    bundle BOOLEAN NOT NULL,
    FOREIGN KEY(product_id) REFERENCES PRODUCTS(product_id) ON DELETE CASCADE
);

-- Table 10: BASKET
CREATE TABLE IF NOT EXISTS BASKET (
    customer_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    PRIMARY KEY(customer_id, product_id),
    FOREIGN KEY(customer_id) REFERENCES CUSTOMER(customer_id) ON DELETE CASCADE,
    FOREIGN KEY(product_id) REFERENCES PRODUCTS(product_id) ON DELETE CASCADE
);

-- Table 11: FAVOURITE
CREATE TABLE IF NOT EXISTS FAVOURITE (
    customer_id INT NOT NULL,
    product_id INT NOT NULL,
    PRIMARY KEY(customer_id, product_id),
    FOREIGN KEY(customer_id) REFERENCES CUSTOMER(customer_id) ON DELETE CASCADE,
    FOREIGN KEY(product_id) REFERENCES PRODUCTS(product_id) ON DELETE CASCADE
);

-- Table 12: STORE
CREATE TABLE IF NOT EXISTS STORE (
    store_id SERIAL PRIMARY KEY,
    branch_number VARCHAR(20),
    address VARCHAR(255)
);

-- Table 13: INVENTORY
CREATE TABLE IF NOT EXISTS INVENTORY (
    inventory_id SERIAL PRIMARY KEY,
    store_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    restocking_threshold INT NOT NULL DEFAULT 10,
    last_restocking_date DATE,
    FOREIGN KEY(store_id) REFERENCES STORE(store_id) ON DELETE CASCADE,
    FOREIGN KEY(product_id) REFERENCES PRODUCTS(product_id) ON DELETE CASCADE
);

-- Table 14: ORDERS
CREATE TABLE IF NOT EXISTS ORDERS (
    order_id SERIAL PRIMARY KEY,
    gift_card_num INT,
    order_date TIMESTAMP NOT NULL,
    order_status VARCHAR(50) NOT NULL,
    order_type VARCHAR(50) NOT NULL CHECK (order_type IN ('Delivery', 'Pickup')),
    payment_method VARCHAR(50) NOT NULL CHECK (payment_method IN ('Card', 'Paypal')),
    installment BOOLEAN NOT NULL,
    total_payment REAL NOT NULL,
    FOREIGN KEY(gift_card_num) REFERENCES GIFT_CARDS(gift_card_num) ON DELETE SET NULL
);

-- Table 15: ORDER_ITEMS
CREATE TABLE IF NOT EXISTS ORDER_ITEMS (
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    price DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES ORDERS(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES PRODUCTS(product_id) ON DELETE CASCADE
);

-- Table 16: INSTALMENTS
CREATE TABLE IF NOT EXISTS INSTALMENTS (
    order_id INT NOT NULL,
    instalment_number INT NOT NULL,
    instalment_amount DECIMAL(10,2) NOT NULL,
    pay_due DATE,
    payment_status VARCHAR(50) NOT NULL DEFAULT 'Pending' CHECK (payment_status IN ('Pending', 'Paid', 'Late')),
    PRIMARY KEY (order_id, instalment_number),
    FOREIGN KEY (order_id) REFERENCES ORDERS(order_id) ON DELETE CASCADE
);

-- Table 17: ORDER_REF
CREATE TABLE IF NOT EXISTS ORDER_REF (
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (product_id) REFERENCES PRODUCTS(product_id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES ORDER_ITEMS(order_id) ON DELETE CASCADE
);

-- Table 18: PLACES
CREATE TABLE IF NOT EXISTS PLACES (
    customer_id INT NOT NULL,
    product_id INT NOT NULL,
    order_id INT NOT NULL,
    PRIMARY KEY (customer_id, product_id, order_id),
    FOREIGN KEY (customer_id) REFERENCES CUSTOMER(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES PRODUCTS(product_id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES ORDERS(order_id) ON DELETE CASCADE
);

-- Table 19: PRODUCT_INVENTORY
CREATE TABLE IF NOT EXISTS PRODUCT_INVENTORY (
    inventory_id INT NOT NULL,
    product_id INT NOT NULL,
    PRIMARY KEY (inventory_id, product_id),
    FOREIGN KEY (inventory_id) REFERENCES INVENTORY(inventory_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES PRODUCTS(product_id) ON DELETE CASCADE
);

-- Table 20: PRODUCT_IMAGES
CREATE TABLE IF NOT EXISTS PRODUCT_IMAGES (
    image_id SERIAL PRIMARY KEY,
    product_id INT NOT NULL,
    image BYTEA NOT NULL,
    FOREIGN KEY (product_id) REFERENCES PRODUCTS(product_id) ON DELETE CASCADE
);
