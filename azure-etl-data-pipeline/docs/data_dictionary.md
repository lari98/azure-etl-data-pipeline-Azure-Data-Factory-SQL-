# Data Dictionary

## Source Tables (data/raw/)

### transactions.csv
| Column | Type | Description |
|--------|------|-------------|
| transaction_id | STRING | Unique transaction identifier (T0000001) |
| order_date | DATETIME | Order timestamp (YYYY-MM-DD HH:MM:SS) |
| customer_id | STRING | Foreign key to customers (C00001) |
| product_id | STRING | Foreign key to products (P00001) |
| channel_id | STRING | Foreign key to channels (CH01-CH05) |
| quantity | INT | Units purchased |
| unit_price_eur | FLOAT | Price per unit in EUR |
| discount_pct | INT | Discount percentage (0-25) |
| total_amount_eur | FLOAT | Line total after discount |
| payment_method | STRING | Payment type (credit_card, paypal, bank_transfer, klarna, apple_pay) |
| status | STRING | Order status (completed, returned, cancelled) |
| shipping_cost_eur | FLOAT | Shipping cost in EUR |

### customers.csv
| Column | Type | Description |
|--------|------|-------------|
| customer_id | STRING | Primary key (C00001) |
| first_name | STRING | Customer first name |
| last_name | STRING | Customer last name |
| email | STRING | Contact email |
| city | STRING | City (DACH region) |
| country | STRING | Country code (DE/AT/CH) |
| segment | STRING | Customer segment (Premium/Standard/Budget) |
| registration_date | DATE | Account creation date |
| is_active | BOOL | Active account flag |

### products.json
| Column | Type | Description |
|--------|------|-------------|
| product_id | STRING | Primary key (P00001) |
| product_name | STRING | Product name with brand |
| category | STRING | Product category (Elektronik, Haushalt, Sport, Buero, Mode) |
| brand | STRING | Brand name |
| price_eur | FLOAT | List price in EUR |
| cost_eur | FLOAT | Unit cost in EUR |
| weight_kg | FLOAT | Product weight |
| is_available | BOOL | In stock flag |
| created_date | DATE | Product listing date |

## Warehouse Tables (data/warehouse/)

### fact_sales
Star schema fact table with surrogate keys linking to all dimensions.

### dim_date
Complete date dimension with fiscal calendar support.

### dim_customer
Customer dimension with SCD Type 2 preparation fields (effective_from, effective_to, is_current).

### dim_product
Product dimension enriched with margin calculations and price tier classification.

### dim_channel
Sales channel dimension (Online/Offline classification).
