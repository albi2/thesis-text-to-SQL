-- Add comments to account table columns
COMMENT ON COLUMN account.account_id IS 'unique identifier for the account';
COMMENT ON COLUMN account.district_id IS 'location of branch where account is held';
COMMENT ON COLUMN account.frequency IS 'frequency of account statement issuance - monthly (POPLATEK MESICNE), weekly (POPLATEK TYDNE), or after transaction (POPLATEK PO OBRATU)';
COMMENT ON COLUMN account.date IS 'creation date of the account in YYMMDD format';

-- Add comments to card table columns
COMMENT ON COLUMN card.card_id IS 'unique identifier for the credit card';
COMMENT ON COLUMN card.disp_id IS 'disposition identifier linking to account access rights';
COMMENT ON COLUMN card.type IS 'credit card class level - junior for basic cards, classic for standard cards, gold for premium cards';
COMMENT ON COLUMN card.issued IS 'date when the credit card was issued in YYMMDD format';

-- Add comments to client table columns
COMMENT ON COLUMN client.client_id IS 'unique identifier for the client';
COMMENT ON COLUMN client.gender IS 'client gender - F for female, M for male';
COMMENT ON COLUMN client.birth_date IS 'client birth date';
COMMENT ON COLUMN client.district_id IS 'location of branch where client is registered';

-- Add comments to disp table columns
COMMENT ON COLUMN disp.disp_id IS 'unique identifier for this disposition record';
COMMENT ON COLUMN disp.client_id IS 'identifier of the client who has disposition rights';
COMMENT ON COLUMN disp.account_id IS 'identifier of the account for which disposition is granted';
COMMENT ON COLUMN disp.type IS 'type of account access rights - OWNER has full rights including permanent orders and loan applications, USER and DISPONENT have limited access';

-- Add comments to district table columns
COMMENT ON COLUMN district.district_id IS 'unique identifier for the district';
COMMENT ON COLUMN district.a2 IS 'name of the district';
COMMENT ON COLUMN district.a3 IS 'region where the district is located';
COMMENT ON COLUMN district.a4 IS 'total number of inhabitants in the district';
COMMENT ON COLUMN district.a5 IS 'number of municipalities with less than 499 inhabitants';
COMMENT ON COLUMN district.a6 IS 'number of municipalities with 500-1999 inhabitants';
COMMENT ON COLUMN district.a7 IS 'number of municipalities with 2000-9999 inhabitants';
COMMENT ON COLUMN district.a8 IS 'number of municipalities with more than 10000 inhabitants';
COMMENT ON COLUMN district.a10 IS 'ratio of urban inhabitants in the district';
COMMENT ON COLUMN district.a11 IS 'average salary in the district';
COMMENT ON COLUMN district.a12 IS 'unemployment rate in the district for 1995';
COMMENT ON COLUMN district.a13 IS 'unemployment rate in the district for 1996';
COMMENT ON COLUMN district.a14 IS 'number of entrepreneurs per 1000 inhabitants';
COMMENT ON COLUMN district.a15 IS 'number of committed crimes in the district during 1995';
COMMENT ON COLUMN district.a16 IS 'number of committed crimes in the district during 1996';

-- Add comments to loan table columns
COMMENT ON COLUMN loan.loan_id IS 'unique identifier for the loan';
COMMENT ON COLUMN loan.account_id IS 'identifier of the account associated with the loan';
COMMENT ON COLUMN loan.date IS 'date when the loan was approved';
COMMENT ON COLUMN loan.amount IS 'approved loan amount in US dollars';
COMMENT ON COLUMN loan.duration IS 'loan duration in months';
COMMENT ON COLUMN loan.payments IS 'monthly payment amount';
COMMENT ON COLUMN loan.status IS 'loan repayment status - A: contract finished successfully, B: contract finished with unpaid loan, C: running contract in good standing, D: running contract with client in debt';

-- Add comments to order table columns
COMMENT ON COLUMN "order".order_id IS 'unique identifier for the payment order';
COMMENT ON COLUMN "order".account_id IS 'identifier of the account initiating the payment order';
COMMENT ON COLUMN "order".bank_to IS 'bank code of the payment recipient';
COMMENT ON COLUMN "order".account_to IS 'account number of the payment recipient';
COMMENT ON COLUMN "order".amount IS 'amount debited for the payment order';
COMMENT ON COLUMN "order".k_symbol IS 'purpose of the payment - POJISTNE for insurance, SIPO for household payments, LEASING for leasing payments, UVER for loan payments';
-- Add comments to trans table columns
COMMENT ON COLUMN trans.trans_id IS 'unique identifier for the transaction';
COMMENT ON COLUMN trans.account_id IS 'identifier of the account involved in the transaction';
COMMENT ON COLUMN trans.date IS 'date when the transaction occurred';
COMMENT ON COLUMN trans.type IS 'transaction direction - PRIJEM for credit/deposit, VYDAJ for withdrawal/debit';
COMMENT ON COLUMN trans.operation IS 'method of transaction - VYBER KARTOU for credit card withdrawal, VKLAD for cash deposit, PREVOD Z UCTU for collection from another bank, VYBER for cash withdrawal, PREVOD NA UCET for remittance to another bank';
COMMENT ON COLUMN trans.amount IS 'transaction amount in USD';
COMMENT ON COLUMN trans.balance IS 'account balance after the transaction in USD';
COMMENT ON COLUMN trans.k_symbol IS 'transaction purpose - POJISTNE for insurance payment, SLUZBY for statement fee, UROK for interest credited, SANKC. UROK for sanction interest on negative balance, SIPO for household payments, DUCHOD for pension payments, UVER for loan payments';
COMMENT ON COLUMN trans.bank IS 'bank code of the transaction partner';
COMMENT ON COLUMN trans.account IS 'account number of the transaction partner';