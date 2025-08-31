-- SQL script to add column comments to database tables
-- PostgreSQL dialect

-- Comments for customers table
COMMENT ON COLUMN customers.customerid IS 'Identification of the customer';
COMMENT ON COLUMN customers.segment IS 'Client segment classification';
COMMENT ON COLUMN customers.currency IS 'Currency used by the customer';

-- Comments for gasstations table  
COMMENT ON COLUMN gasstations.gasstationid IS 'Gas station identification number';
COMMENT ON COLUMN gasstations.chainid IS 'Chain identification number';
COMMENT ON COLUMN gasstations.country IS 'Country where the gas station is located';
COMMENT ON COLUMN gasstations.segment IS 'Chain segment classification';

-- Comments for products table
COMMENT ON COLUMN products.productid IS 'Product identification number';
COMMENT ON COLUMN products.description IS 'Product description';

-- Comments for transactions_1k table
COMMENT ON COLUMN transactions_1k.transactionid IS 'Transaction identification number';
COMMENT ON COLUMN transactions_1k.date IS 'Date when the transaction occurred';
COMMENT ON COLUMN transactions_1k.time IS 'Time when the transaction occurred';
COMMENT ON COLUMN transactions_1k.customerid IS 'Customer identification number';
COMMENT ON COLUMN transactions_1k.cardid IS 'Card identification number used for the transaction';
COMMENT ON COLUMN transactions_1k.gasstationid IS 'Gas station identification number where transaction took place';
COMMENT ON COLUMN transactions_1k.productid IS 'Product identification number purchased';
COMMENT ON COLUMN transactions_1k.amount IS 'Quantity of product purchased';
COMMENT ON COLUMN transactions_1k.price IS 'Unit price of the product (total price = Amount x Price)';

-- Comments for yearmonth table
COMMENT ON COLUMN yearmonth.customerid IS 'Customer identification number';
COMMENT ON COLUMN yearmonth.date IS 'Date reference for the consumption period';
COMMENT ON COLUMN yearmonth.consumption IS 'Customer consumption amount for the period';