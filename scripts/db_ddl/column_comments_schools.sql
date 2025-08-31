-- PostgreSQL script to add column comments based on CSV metadata
-- Generated from frpm.csv, satscores.csv, and schools.csv metadata
-- Business-focused descriptions only

-- Comments for frpm table
COMMENT ON COLUMN frpm.CDSCode IS 'California Department of Schools unique identifier code';

COMMENT ON COLUMN frpm."Academic Year" IS 'Academic year for the reported data';

COMMENT ON COLUMN frpm."County Code" IS 'Numeric code identifying the county';

COMMENT ON COLUMN frpm."District Code" IS 'Numeric code identifying the school district';

COMMENT ON COLUMN frpm."School Code" IS 'Numeric code identifying the individual school';

COMMENT ON COLUMN frpm."County Name" IS 'Name of the county where the school is located';

COMMENT ON COLUMN frpm."District Name" IS 'Name of the school district';

COMMENT ON COLUMN frpm."School Name" IS 'Name of the individual school';

COMMENT ON COLUMN frpm."District Type" IS 'Classification type of the school district';

COMMENT ON COLUMN frpm."School Type" IS 'Classification type of the school';

COMMENT ON COLUMN frpm."Educational Option Type" IS 'Type of educational program or option offered';

COMMENT ON COLUMN frpm."NSLP Provision Status" IS 'National School Lunch Program provision status';

COMMENT ON COLUMN frpm."Charter School (Y/N)" IS 'Indicates whether the school is a charter school (0: No, 1: Yes)';

COMMENT ON COLUMN frpm."Charter School Number" IS 'Unique identifier number assigned to charter schools';

COMMENT ON COLUMN frpm."Charter Funding Type" IS 'Type of funding model used for the charter school';

COMMENT ON COLUMN frpm.IRC IS 'Internal reference code (not useful for analysis)';

COMMENT ON COLUMN frpm."Low Grade" IS 'Lowest grade level offered by the school';

COMMENT ON COLUMN frpm."High Grade" IS 'Highest grade level offered by the school';

COMMENT ON COLUMN frpm."Enrollment (K-12)" IS 'Total student enrollment for kindergarten through 12th grade';

COMMENT ON COLUMN frpm."Free Meal Count (K-12)" IS 'Number of K-12 students eligible for free meals. Used to calculate eligible free rate = Free Meal Count / Enrollment';

COMMENT ON COLUMN frpm."Percent (%) Eligible Free (K-12)" IS 'Percentage of K-12 students eligible for free meals';

COMMENT ON COLUMN frpm."FRPM Count (K-12)" IS 'Number of K-12 students eligible for free or reduced price meals. Used to calculate eligible FRPM rate = FRPM / Enrollment';

COMMENT ON COLUMN frpm."Percent (%) Eligible FRPM (K-12)" IS 'Percentage of K-12 students eligible for free or reduced price meals';

COMMENT ON COLUMN frpm."Enrollment (Ages 5-17)" IS 'Total student enrollment for ages 5-17';

COMMENT ON COLUMN frpm."Free Meal Count (Ages 5-17)" IS 'Number of students ages 5-17 eligible for free meals. Used to calculate eligible free rate = Free Meal Count / Enrollment';

COMMENT ON COLUMN frpm."Percent (%) Eligible Free (Ages 5-17)" IS 'Percentage of students ages 5-17 eligible for free meals';

COMMENT ON COLUMN frpm."FRPM Count (Ages 5-17)" IS 'Number of students ages 5-17 eligible for free or reduced price meals';

COMMENT ON COLUMN frpm."Percent (%) Eligible FRPM (Ages 5-17)" IS 'Percentage of students ages 5-17 eligible for free or reduced price meals';

COMMENT ON COLUMN frpm."2013-14 CALPADS Fall 1 Certification Status" IS 'Certification status in the California Longitudinal Pupil Achievement Data System for Fall 2013-14';


-- Comments for satscores table
COMMENT ON COLUMN satscores.cds IS 'California Department of Schools unique identifier';

COMMENT ON COLUMN satscores.rtype IS 'Record type identifier (not useful for analysis)';

COMMENT ON COLUMN satscores.sname IS 'Name of the school';

COMMENT ON COLUMN satscores.dname IS 'Name of the school district';

COMMENT ON COLUMN satscores.cname IS 'Name of the county';

COMMENT ON COLUMN satscores.enroll12 IS 'Total student enrollment for grades 1-12';

COMMENT ON COLUMN satscores.NumTstTakr IS 'Number of students who took the SAT test at this school';

COMMENT ON COLUMN satscores.AvgScrRead IS 'Average SAT Reading score for students at this school';

COMMENT ON COLUMN satscores.AvgScrMath IS 'Average SAT Math score for students at this school';

COMMENT ON COLUMN satscores.AvgScrWrite IS 'Average SAT Writing score for students at this school';

COMMENT ON COLUMN satscores.NumGE1500 IS 'Number of students who scored 1500 or higher on total SAT. Used to calculate Excellence Rate = NumGE1500 / NumTstTakr';


-- Comments for schools table
COMMENT ON COLUMN schools.CDSCode IS 'California Department of Schools unique identifier code';

COMMENT ON COLUMN schools.NCESDist IS '7-digit National Center for Educational Statistics school district ID. First 2 digits identify the state, last 5 digits identify the district';

COMMENT ON COLUMN schools.NCESSchool IS '5-digit National Center for Educational Statistics school ID. Combined with NCESDist forms unique 12-digit school identifier';

COMMENT ON COLUMN schools.StatusType IS 'Current operational status: Active (operating), Closed (not operating), Merged (combined with other districts), or Pending (not yet open)';

COMMENT ON COLUMN schools.County IS 'County where the school is located';

COMMENT ON COLUMN schools.District IS 'School district name';

COMMENT ON COLUMN schools.School IS 'Individual school name';

COMMENT ON COLUMN schools.Street IS 'Physical street address of the school';

COMMENT ON COLUMN schools.StreetAbr IS 'Abbreviated physical street address of the school';

COMMENT ON COLUMN schools.City IS 'City where the school is located';

COMMENT ON COLUMN schools.Zip IS 'ZIP code of the school location';

COMMENT ON COLUMN schools.State IS 'State where the school is located';

COMMENT ON COLUMN schools.MailStreet IS 'Mailing street address (may differ from physical address)';

COMMENT ON COLUMN schools.MailStrAbr IS 'Abbreviated mailing street address';

COMMENT ON COLUMN schools.MailCity IS 'City for mailing address';

COMMENT ON COLUMN schools.MailZip IS 'ZIP code for mailing address';

COMMENT ON COLUMN schools.MailState IS 'State for mailing address';

COMMENT ON COLUMN schools.Phone IS 'Primary phone number for the school';

COMMENT ON COLUMN schools.Ext IS 'Phone extension for the school';

COMMENT ON COLUMN schools.Website IS 'School or district website address';

COMMENT ON COLUMN schools.OpenDate IS 'Date when the school first opened';

COMMENT ON COLUMN schools.ClosedDate IS 'Date when the school closed (if applicable)';

COMMENT ON COLUMN schools.Charter IS 'Indicates if school is a charter school (1: Yes, 0: No)';

COMMENT ON COLUMN schools.CharterNum IS '4-digit number assigned to charter schools';

COMMENT ON COLUMN schools.FundingType IS 'Charter school funding model: Not in CS funding model, Locally funded, or Directly funded';

COMMENT ON COLUMN schools.DOC IS 'District ownership category: County Office (00), State Board (02), Statewide Charter (03), State Special (31), Non-school Location (34), Elementary District (52), Unified District (54), High School District (56), ROC/P (98)';

COMMENT ON COLUMN schools.DOCType IS 'Description of the district ownership category';

COMMENT ON COLUMN schools.SOC IS 'School type classification: Preschool (08), Special Ed (09), Youth Authority (11), Opportunity (13), Juvenile Court (14), Other Programs (15), State Special (31), Elementary (60-61), Middle/Jr High (62,64), Alternative Choice (63), K-12 (65), High School (66-67), Continuation (68), Community Day (69), Adult Ed (70), ROC/P (98)';

COMMENT ON COLUMN schools.SOCType IS 'Description of the school type classification';

COMMENT ON COLUMN schools.EdOpsCode IS 'Educational program type: ALTSOC (Alternative), COMM (County Community), COMMDAY (Community Day), CON (Continuation), JUV (Juvenile Court), OPP (Opportunity), YTH (Youth Authority), SSS (State Special), SPEC (Special Education), TRAD (Traditional), ROP (Regional Occupational), HOMHOS (Home/Hospital), SPECON (Special Ed Consortia)';

COMMENT ON COLUMN schools.EdOpsName IS 'Full description of the educational program type offered';

COMMENT ON COLUMN schools.EILCode IS 'Grade level focus: A (Adult), ELEM (Elementary), ELEMHIGH (Elementary-High Combo), HS (High School), INTMIDJR (Intermediate/Middle/Junior High), PS (Preschool), UG (Ungraded)';

COMMENT ON COLUMN schools.EILName IS 'Full description of the grade level focus served by the institution';

COMMENT ON COLUMN schools.GSoffered IS 'Grade span officially offered by the school (may differ from actual enrollment)';

COMMENT ON COLUMN schools.GSserved IS 'Grade span of actual student enrollment as reported in CALPADS (K-12 only)';

COMMENT ON COLUMN schools.Virtual IS 'Virtual instruction model: F (Exclusively Virtual), V (Primarily Virtual), C (Primarily Classroom), N (Not Virtual), P (Partial Virtual - retired after 2016-17)';

COMMENT ON COLUMN schools.Magnet IS 'Indicates if school offers magnet programs (1: Yes, 0: No)';

COMMENT ON COLUMN schools.Latitude IS 'Geographic latitude coordinate of the school location';

COMMENT ON COLUMN schools.Longitude IS 'Geographic longitude coordinate of the school location';

COMMENT ON COLUMN schools.AdmFName1 IS 'First name of the primary administrator (superintendent or principal)';

COMMENT ON COLUMN schools.AdmLName1 IS 'Last name of the primary administrator (superintendent or principal)';

COMMENT ON COLUMN schools.AdmEmail1 IS 'Email address of the primary administrator';

COMMENT ON COLUMN schools.AdmFName2 IS 'First name of the secondary administrator';

COMMENT ON COLUMN schools.AdmLName2 IS 'Last name of the secondary administrator';

COMMENT ON COLUMN schools.AdmEmail2 IS 'Email address of the secondary administrator';

COMMENT ON COLUMN schools.AdmFName3 IS 'First name of the tertiary administrator';

COMMENT ON COLUMN schools.AdmLName3 IS 'Last name of the tertiary administrator';

COMMENT ON COLUMN schools.AdmEmail3 IS 'Email address of the tertiary administrator';

COMMENT ON COLUMN schools.LastUpdate IS 'Date when this school record was last updated in the system';

-- End of script