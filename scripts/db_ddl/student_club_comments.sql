-- PostgreSQL script to add column comments to database tables

-- Attendance table comments
COMMENT ON COLUMN attendance.link_to_event IS 'The unique identifier of the event which was attended. References the Event table';
COMMENT ON COLUMN attendance.link_to_member IS 'The unique identifier of the member who attended the event. References the Member table';

-- Budget table comments
COMMENT ON COLUMN budget.budget_id IS 'A unique identifier for the budget entry';
COMMENT ON COLUMN budget.category IS 'The area for which the amount is budgeted, such as advertisement, food, parking';
COMMENT ON COLUMN budget.spent IS 'The total amount spent in the budgeted category for an event (in dollars). This is summarized from the Expense table';
COMMENT ON COLUMN budget.remaining IS 'A value calculated as the amount budgeted minus the amount spent (in dollars). If the remaining < 0, it means that the cost has exceeded the budget';
COMMENT ON COLUMN budget.amount IS 'The amount budgeted for the specified category and event (in dollars). Can be calculated as amount = spent + remaining';
COMMENT ON COLUMN budget.event_status IS 'The status of the event. Closed: event is closed, spent and remaining won''t change. Open: event is already opened, spent and remaining will change with new expenses. Planning: event is not started yet but is planning, spent and remaining won''t change at this stage';
COMMENT ON COLUMN budget.link_to_event IS 'The unique identifier of the event to which the budget line applies. References the Event table';

-- Event table comments
COMMENT ON COLUMN event.event_id IS 'A unique identifier for the event';
COMMENT ON COLUMN event.event_name IS 'Event name';
COMMENT ON COLUMN event.event_date IS 'The date the event took place or is scheduled to take place (e.g. 2020-03-10T12:00:00)';
COMMENT ON COLUMN event.type IS 'The kind of event, such as game, social, election';
COMMENT ON COLUMN event.notes IS 'A free text field for any notes about the event';
COMMENT ON COLUMN event.location IS 'Address where the event was held or is to be held or the name of such a location';
COMMENT ON COLUMN event.status IS 'One of three values indicating if the event is in planning, is opened, or is closed (Open/Closed/Planning)';

-- Expense table comments
COMMENT ON COLUMN expense.expense_id IS 'Unique id of expense';
COMMENT ON COLUMN expense.expense_description IS 'A textual description of what the money was spent for';
COMMENT ON COLUMN expense.expense_date IS 'The date the expense was incurred (YYYY-MM-DD format)';
COMMENT ON COLUMN expense.cost IS 'The dollar amount of the expense';
COMMENT ON COLUMN expense.approved IS 'A true or false value indicating if the expense was approved';
COMMENT ON COLUMN expense.link_to_member IS 'The member who incurred the expense';
COMMENT ON COLUMN expense.link_to_budget IS 'The unique identifier of the record in the Budget table that indicates the expected total expenditure for a given category and event. References the Budget table';

-- Income table comments
COMMENT ON COLUMN income.income_id IS 'A unique identifier for each record of income';
COMMENT ON COLUMN income.date_received IS 'The date that the fund was received';
COMMENT ON COLUMN income.amount IS 'Amount of funds (in dollars)';
COMMENT ON COLUMN income.source IS 'A value indicating where the funds come from such as dues, or the annual university allocation';
COMMENT ON COLUMN income.notes IS 'A free-text value giving any needed details about the receipt of funds';
COMMENT ON COLUMN income.link_to_member IS 'Link to member';

-- Major table comments
COMMENT ON COLUMN major.major_id IS 'A unique identifier for each major';
COMMENT ON COLUMN major.major_name IS 'Major name';
COMMENT ON COLUMN major.department IS 'The name of the department that offers the major';
COMMENT ON COLUMN major.college IS 'The name of college that houses the department that offers the major';

-- Member table comments
COMMENT ON COLUMN member.member_id IS 'Unique id of member';
COMMENT ON COLUMN member.first_name IS 'Member''s first name';
COMMENT ON COLUMN member.last_name IS 'Member''s last name. Full name is first_name + last_name. e.g. A member''s first name is Angela and last name is Sanders. Thus, his/her full name is Angela Sanders';
COMMENT ON COLUMN member.email IS 'Member''s email';
COMMENT ON COLUMN member.position IS 'The position the member holds in the club';
COMMENT ON COLUMN member.t_shirt_size IS 'The size of tee shirt that member wants when shirts are ordered. Usually the student who ordered t-shirt with larger size has bigger body shape';
COMMENT ON COLUMN member.phone IS 'The best telephone at which to contact the member';
COMMENT ON COLUMN member.zip IS 'The zip code of the member''s hometown';
COMMENT ON COLUMN member.link_to_major IS 'The unique identifier of the major of the member. References the Major table';

-- Zip Code table comments
COMMENT ON COLUMN zip_code.zip_code IS 'The ZIP code itself. A five-digit number identifying a US post office';
COMMENT ON COLUMN zip_code.type IS 'The kind of ZIP code. Standard: the normal codes with which most people are familiar. PO Box: zip codes have post office boxes. Unique: zip codes that are assigned to individual organizations';
COMMENT ON COLUMN zip_code.city IS 'The city to which the ZIP pertains';
COMMENT ON COLUMN zip_code.county IS 'The county to which the ZIP pertains';
COMMENT ON COLUMN zip_code.state IS 'The name of the state to which the ZIP pertains';
COMMENT ON COLUMN zip_code.short_state IS 'The abbreviation of the state to which the ZIP pertains';