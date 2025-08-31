-- Add column comments for alignment table
COMMENT ON COLUMN alignment.id IS 'The unique identifier of the alignment';
COMMENT ON COLUMN alignment.alignment IS 'The alignment of the superhero. Alignment refers to a character''s moral and ethical stance and can be used to describe the overall attitude or behavior of a superhero. Good: These superheroes are typically kind, selfless, and dedicated to protecting others and upholding justice (e.g., Superman, Wonder Woman, Spider-Man). Neutral: These superheroes may not always prioritize the greater good, but are not necessarily evil either. They may act in their own self-interest or make decisions based on their own moral code (e.g., Hulk, Deadpool). Bad: These superheroes are typically selfish, manipulative, and willing to harm others in pursuit of their own goals (e.g., Lex Luthor, Joker).';

-- Add column comments for attribute table
COMMENT ON COLUMN attribute.id IS 'The unique identifier of the attribute';
COMMENT ON COLUMN attribute.attribute_name IS 'The attribute name. A superhero''s attribute is a characteristic or quality that defines who they are and what they are capable of. This could be a physical trait, such as superhuman strength or the ability to fly, or a personal trait, such as extraordinary intelligence or exceptional bravery.';

-- Add column comments for colour table
COMMENT ON COLUMN colour.id IS 'The unique identifier of the color';
COMMENT ON COLUMN colour.colour IS 'The color of the superhero''s skin/eye/hair/etc';

-- Add column comments for gender table
COMMENT ON COLUMN gender.id IS 'The unique identifier of the gender';
COMMENT ON COLUMN gender.gender IS 'The gender of the superhero';

-- Add column comments for hero_attribute table
COMMENT ON COLUMN hero_attribute.hero_id IS 'The id of the hero. Maps to superhero(id)';
COMMENT ON COLUMN hero_attribute.attribute_id IS 'The id of the attribute. Maps to attribute(id)';
COMMENT ON COLUMN hero_attribute.attribute_value IS 'The attribute value. If a superhero has a higher attribute value on a particular attribute, it means that they are more skilled or powerful in that area compared to other superheroes. For example, if a superhero has a higher attribute value for strength, they may be able to lift heavier objects or deliver more powerful punches than other superheroes.';

-- Add column comments for hero_power table
COMMENT ON COLUMN hero_power.hero_id IS 'The id of the hero. Maps to superhero(id)';
COMMENT ON COLUMN hero_power.power_id IS 'The id of the power. Maps to superpower(id). In general, a superhero''s attributes provide the foundation for their abilities and help to define who they are, while their powers are the specific abilities that they use to fight crime and protect others.';

-- Add column comments for publisher table
COMMENT ON COLUMN publisher.id IS 'The unique identifier of the publisher';
COMMENT ON COLUMN publisher.publisher_name IS 'The name of the publisher';

-- Add column comments for race table
COMMENT ON COLUMN race.id IS 'The unique identifier of the race';
COMMENT ON COLUMN race.race IS 'The race of the superhero. In the context of superheroes, a superhero''s race would refer to the particular group of people that the superhero belongs to based on physical characteristics.';

-- Add column comments for superhero table
COMMENT ON COLUMN superhero.id IS 'The unique identifier of the superhero';
COMMENT ON COLUMN superhero.superhero_name IS 'The name of the superhero';
COMMENT ON COLUMN superhero.full_name IS 'The full name of the superhero. The full name of a person typically consists of their given name (first name or personal name) and their surname (last name or family name). For example, if someone''s given name is "John" and their surname is "Smith," their full name would be "John Smith."';
COMMENT ON COLUMN superhero.gender_id IS 'The id of the superhero''s gender';
COMMENT ON COLUMN superhero.eye_colour_id IS 'The id of the superhero''s eye color';
COMMENT ON COLUMN superhero.hair_colour_id IS 'The id of the superhero''s hair color';
COMMENT ON COLUMN superhero.skin_colour_id IS 'The id of the superhero''s skin color';
COMMENT ON COLUMN superhero.race_id IS 'The id of the superhero''s race';
COMMENT ON COLUMN superhero.publisher_id IS 'The id of the publisher';
COMMENT ON COLUMN superhero.alignment_id IS 'The id of the superhero''s alignment';
COMMENT ON COLUMN superhero.height_cm IS 'The height of the superhero in centimeters. If the height_cm is NULL or 0, it means the height of the superhero is missing.';
COMMENT ON COLUMN superhero.weight_kg IS 'The weight of the superhero in kilograms. If the weight_kg is NULL or 0, it means the weight of the superhero is missing.';

-- Add column comments for superpower table
COMMENT ON COLUMN superpower.id IS 'The unique identifier of the superpower';
COMMENT ON COLUMN superpower.power_name IS 'The superpower name';