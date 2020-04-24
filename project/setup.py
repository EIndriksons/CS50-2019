import sqlite3

conn = sqlite3.connect("project.db")
cur = conn.cursor()


""" TABLES """
# Create Eventlog table
cur.executescript("""
CREATE TABLE 'Eventlog' (
'id' integer PRIMARY KEY AUTOINCREMENT NOT NULL,
'createdate' timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
'action' text NOT NULL,
'table' text NOT NULL,
'variable' text NOT NULL,
'event_id' integer NOT NULL,
'data_from' text,
'data_to' text
)
""")

# Create Users table
cur.executescript("""
CREATE TABLE 'Users' (
'id' integer PRIMARY KEY AUTOINCREMENT NOT NULL,
'createdate' timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
'email' text NOT NULL UNIQUE,
'name' text NOT NULL,
'surname' text NOT NULL,
'personal_code' char(11),
'hash' text NOT NULL,
'role' char(5) NOT NULL DEFAULT 'User',
'status' char(16) NOT NULL DEFAULT 'New',
'status_changed' date,
'status_changed_by' integer
)
""")

# Create Bank Accounts table
cur.executescript("""
CREATE TABLE 'Bank' (
'id' integer PRIMARY KEY AUTOINCREMENT NOT NULL,
'createdate' timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
'user_id' integer NOT NULL,
'bank_name' text NOT NULL,
'bank_code' text NOT NULL,
'bank_iban' text NOT NULL UNIQUE,
'active' boolean
)
""")

# Create Finance table
cur.executescript("""
CREATE TABLE 'Finance' (
'id' integer PRIMARY KEY AUTOINCREMENT NOT NULL,
'createdate' timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
'user_id' integer NOT NULL,
'status' char(16) NOT NULL,
'number' text,
'date' date,
'text' text,
'name_director' text,
'name_accountant' text,
'paid_bank_name' text,
'paid_bank_code' text,
'paid_bank_iban' text,
'review_id' integer
)
""")

# Create Transactions table
cur.executescript("""
CREATE TABLE 'Transactions' (
'id' integer PRIMARY KEY AUTOINCREMENT NOT NULL,
'createdate' timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
'finance_id' integer NOT NULL,
'status' char(32) NOT NULL,
'date' date,
'partner' text,
'expense' text,
'document_type' text,
'document_no' text,
'amount' real DEFAULT 0,
'paid_amount' real DEFAULT 0,
'review_id' integer
)
""")

# Create Settings table
cur.executescript("""
CREATE TABLE 'Settings' (
'id' integer PRIMARY KEY AUTOINCREMENT NOT NULL,
'createdate' timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
'name_director' text NOT NULL,
'name_accountant' text NOT NULL,
'document_types' text
)
""")

cur.executescript("""
INSERT INTO "Settings" ("name_director","name_accountant","document_types") VALUES ('test','test','test')
""")


""" EVENTLOG """
""" update """
# Create an UPDATE trigger on Users table for the Eventlog
cur.executescript("""
CREATE TRIGGER 'Eventlog_UPDATE_Users' AFTER UPDATE ON "Users"
BEGIN
    INSERT INTO "Eventlog" ("action","table","variable","event_id","data_from","data_to")
    SELECT 'UPDATE' "action", 'Users' "table", "variable", "event_id", "data_from", "data_to"
    FROM
    (
        SELECT '' "variable", 0 "event_id", '' "data_from", '' "data_to", 0 "keep"
        UNION ALL
        SELECT sub.*
        FROM
        (
            VALUES
            ('email', OLD.id, OLD.email, NEW.email, NEW.email!=OLD.email),
            ('name', OLD.id, OLD.name, NEW.name, NEW.name!=OLD.name),
            ('surname', OLD.id, OLD.surname, NEW.surname, NEW.surname!=OLD.surname),
            ('personal_code', OLD.id, OLD.personal_code, NEW.personal_code, NEW.personal_code!=OLD.personal_code),
            ('hash', OLD.id, OLD.hash, NEW.hash, NEW.hash!=OLD.hash),
            ('role', OLD.id, OLD.role, NEW.role, NEW.role!=OLD.role),
            ('status', OLD.id, OLD.status, NEW.status, NEW.status!=OLD.status),
            ('status_changed', OLD.id, OLD.status_changed, NEW.status_changed, NEW.status_changed!=OLD.status_changed),
            ('status_changed_by', OLD.id, OLD.status_changed_by, NEW.status_changed_by, NEW.status_changed_by!=OLD.status_changed_by)
        ) AS sub
    ) WHERE keep=1;
END;
""")

# Create an UPDATE trigger on Bank table for the Eventlog
cur.executescript("""
CREATE TRIGGER 'Eventlog_UPDATE_Bank' AFTER UPDATE ON "Bank"
BEGIN
    INSERT INTO "Eventlog" ("action","table","variable","event_id","data_from","data_to")
    SELECT 'UPDATE' "action", 'Bank' "table", "variable", "event_id", "data_from", "data_to"
    FROM
    (
        SELECT '' "variable", 0 "event_id", '' "data_from", '' "data_to", 0 "keep"
        UNION ALL
        SELECT sub.*
        FROM
        (
            VALUES
            ('user_id', OLD.id, OLD.user_id, NEW.user_id, NEW.user_id!=OLD.user_id),
            ('bank_name', OLD.id, OLD.bank_name, NEW.bank_name, NEW.bank_name!=OLD.bank_name),
            ('bank_code', OLD.id, OLD.bank_code, NEW.bank_code, NEW.bank_code!=OLD.bank_code),
            ('bank_iban', OLD.id, OLD.bank_iban, NEW.bank_iban, NEW.bank_iban!=OLD.bank_iban),
            ('active', OLD.id, OLD.active, NEW.active, NEW.active!=OLD.active)
        ) AS sub
    ) WHERE keep=1;
END;
""")

# Create an UPDATE trigger on Finance table for the Eventlog
cur.executescript("""
CREATE TRIGGER 'Eventlog_UPDATE_Finance' AFTER UPDATE ON "Finance"
BEGIN
    INSERT INTO "Eventlog" ("action","table","variable","event_id","data_from","data_to")
    SELECT 'UPDATE' "action", 'Finance' "table", "variable", "event_id", "data_from", "data_to"
    FROM
    (
        SELECT '' "variable", 0 "event_id", '' "data_from", '' "data_to", 0 "keep"
        UNION ALL
        SELECT sub.*
        FROM
        (
            VALUES
            ('user_id', OLD.id, OLD.user_id, NEW.user_id, NEW.user_id!=OLD.user_id),
            ('status', OLD.id, OLD.status, NEW.status, NEW.status!=OLD.status),
            ('number', OLD.id, OLD.number, NEW.number, NEW.number!=OLD.number),
            ('date', OLD.id, OLD.date, NEW.date, NEW.date!=OLD.date),
            ('text', OLD.id, OLD.text, NEW.text, NEW.text!=OLD.text),
            ('name_director', OLD.id, OLD.name_director, NEW.name_director, NEW.name_director!=OLD.name_director),
            ('name_accountant', OLD.id, OLD.name_accountant, NEW.name_accountant, NEW.name_accountant!=OLD.name_accountant),
            ('paid_bank_name', OLD.id, OLD.paid_bank_name, NEW.paid_bank_name, NEW.paid_bank_name!=OLD.paid_bank_name),
            ('paid_bank_code', OLD.id, OLD.paid_bank_code, NEW.paid_bank_code, NEW.paid_bank_code!=OLD.paid_bank_code),
            ('paid_bank_iban', OLD.id, OLD.paid_bank_iban, NEW.paid_bank_iban, NEW.paid_bank_iban!=OLD.paid_bank_iban),
            ('review_id', OLD.id, OLD.review_id, NEW.review_id, NEW.review_id!=OLD.review_id)
        ) AS sub
    ) WHERE keep=1;
END;
""")

# Create an UPDATE trigger on Transactions table for the Eventlog
cur.executescript("""
CREATE TRIGGER 'Eventlog_UPDATE_Transactions' AFTER UPDATE ON "Transactions"
BEGIN
    INSERT INTO "Eventlog" ("action","table","variable","event_id","data_from","data_to")
    SELECT 'UPDATE' "action", 'Transactions' "table", "variable", "event_id", "data_from", "data_to"
    FROM
    (
        SELECT '' "variable", 0 "event_id", '' "data_from", '' "data_to", 0 "keep"
        UNION ALL
        SELECT sub.*
        FROM
        (
            VALUES
            ('finance_id', OLD.id, OLD.finance_id, NEW.finance_id, NEW.finance_id!=OLD.finance_id),
            ('status', OLD.id, OLD.status, NEW.status, NEW.status!=OLD.status),
            ('date', OLD.id, OLD.date, NEW.date, NEW.date!=OLD.date),
            ('partner', OLD.id, OLD.partner, NEW.partner, NEW.partner!=OLD.partner),
            ('expense', OLD.id, OLD.expense, NEW.expense, NEW.expense!=OLD.expense),
            ('document_type', OLD.id, OLD.document_type, NEW.document_type, NEW.document_type!=OLD.document_type),
            ('document_no', OLD.id, OLD.document_no, NEW.document_no, NEW.document_no!=OLD.document_no),
            ('amount', OLD.id, OLD.amount, NEW.amount, NEW.amount!=OLD.amount),
            ('paid_amount', OLD.id, OLD.paid_amount, NEW.paid_amount, NEW.paid_amount!=OLD.paid_amount),
            ('review_id', OLD.id, OLD.review_id, NEW.review_id, NEW.review_id!=OLD.review_id)
        ) AS sub
    ) WHERE keep=1;
END;
""")


""" delete """
# Create an DELETE trigger on Users table for the Eventlog
cur.executescript("""
CREATE TRIGGER 'Eventlog_DELETE_Users' AFTER DELETE ON "Users"
BEGIN
    INSERT INTO "Eventlog" ("action","table","variable","event_id","data_from","data_to")
    SELECT 'DELETE' "action", 'Users' "table", "variable", "event_id", "data_from", "data_to"
    FROM
    (
        SELECT '' "variable", 0 "event_id", '' "data_from", '' "data_to", 0 "keep"
        UNION ALL
        SELECT sub.*
        FROM
        (
            VALUES
            ('createdate', OLD.id, OLD.createdate, '', 1),
            ('email', OLD.id, OLD.email, '', 1),
            ('name', OLD.id, OLD.name, '', 1),
            ('surname', OLD.id, OLD.surname, '', 1),
            ('personal_code', OLD.id, OLD.personal_code, '', 1),
            ('hash', OLD.id, OLD.hash, '', 1),
            ('role', OLD.id, OLD.role, '', 1),
            ('status', OLD.id, OLD.status, '', 1),
            ('status_changed', OLD.id, OLD.status_changed, '', 1),
            ('status_changed_by', OLD.id, OLD.status_changed_by, '', 1)
        ) AS sub
    ) WHERE keep=1;
END;
""")

# Create an DELETE trigger on Bank table for the Eventlog
cur.executescript("""
CREATE TRIGGER 'Eventlog_DELETE_Bank' AFTER DELETE ON "Bank"
BEGIN
    INSERT INTO "Eventlog" ("action","table","variable","event_id","data_from","data_to")
    SELECT 'DELETE' "action", 'Bank' "table", "variable", "event_id", "data_from", "data_to"
    FROM
    (
        SELECT '' "variable", 0 "event_id", '' "data_from", '' "data_to", 0 "keep"
        UNION ALL
        SELECT sub.*
        FROM
        (
            VALUES
            ('createdate', OLD.id, OLD.createdate, '', 1),
            ('user_id', OLD.id, OLD.user_id, '', 1),
            ('bank_name', OLD.id, OLD.bank_name, '', 1),
            ('bank_code', OLD.id, OLD.bank_code, '', 1),
            ('bank_iban', OLD.id, OLD.bank_iban, '', 1),
            ('active', OLD.id, OLD.active, '', 1)
        ) AS sub
    ) WHERE keep=1;
END;
""")

# Create an DELETE trigger on Finance table for the Eventlog
cur.executescript("""
CREATE TRIGGER 'Eventlog_DELETE_Finance' AFTER DELETE ON "Finance"
BEGIN
    INSERT INTO "Eventlog" ("action","table","variable","event_id","data_from","data_to")
    SELECT 'DELETE' "action", 'Finance' "table", "variable", "event_id", "data_from", "data_to"
    FROM
    (
        SELECT '' "variable", 0 "event_id", '' "data_from", '' "data_to", 0 "keep"
        UNION ALL
        SELECT sub.*
        FROM
        (
            VALUES
            ('createdate', OLD.id, OLD.createdate, '', 1),
            ('user_id', OLD.id, OLD.user_id, '', 1),
            ('status', OLD.id, OLD.status, '', 1),
            ('number', OLD.id, OLD.number, '', 1),
            ('date', OLD.id, OLD.date, '', 1),
            ('text', OLD.id, OLD.text, '', 1),
            ('name_director', OLD.id, OLD.name_director, '', 1),
            ('name_accountant', OLD.id, OLD.name_accountant, '', 1),
            ('paid_bank_name', OLD.id, OLD.paid_bank_name, '', 1),
            ('paid_bank_code', OLD.id, OLD.paid_bank_code, '', 1),
            ('paid_bank_iban', OLD.id, OLD.paid_bank_iban, '', 1),
            ('review_id', OLD.id, OLD.review_id, '', 1)
        ) AS sub
    ) WHERE keep=1;
END;
""")

# Create an DELETE trigger on Transactions table for the Eventlog
cur.executescript("""
CREATE TRIGGER 'Eventlog_DELETE_Transactions' AFTER DELETE ON "Transactions"
BEGIN
    INSERT INTO "Eventlog" ("action","table","variable","event_id","data_from","data_to")
    SELECT 'DELETE' "action", 'Transactions' "table", "variable", "event_id", "data_from", "data_to"
    FROM
    (
        SELECT '' "variable", 0 "event_id", '' "data_from", '' "data_to", 0 "keep"
        UNION ALL
        SELECT sub.*
        FROM
        (
            VALUES
            ('createdate', OLD.id, OLD.createdate, '', 1),
            ('finance_id', OLD.id, OLD.finance_id, '', 1),
            ('status', OLD.id, OLD.status, '', 1),
            ('date', OLD.id, OLD.date, '', 1),
            ('partner', OLD.id, OLD.partner, '', 1),
            ('expense', OLD.id, OLD.expense, '', 1),
            ('document_type', OLD.id, OLD.document_type, '', 1),
            ('document_no', OLD.id, OLD.document_no, '', 1),
            ('amount', OLD.id, OLD.amount, '', 1),
            ('paid_amount', OLD.id, OLD.paid_amount, '', 1),
            ('review_id', OLD.id, OLD.review_id, '', 1)
        ) AS sub
    ) WHERE keep=1;
END;
""")