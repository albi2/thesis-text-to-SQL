-- Country table column comments
COMMENT ON COLUMN country.id IS 'Unique identifier for countries';
COMMENT ON COLUMN country.name IS 'Country name';

-- League table column comments
COMMENT ON COLUMN league.id IS 'Unique identifier for leagues';
COMMENT ON COLUMN league.country_id IS 'Unique identifier for countries - links to country table';
COMMENT ON COLUMN league.name IS 'League name';

-- Match table column comments
COMMENT ON COLUMN match.id IS 'Unique identifier for matches';
COMMENT ON COLUMN match.country_id IS 'Country identifier';
COMMENT ON COLUMN match.league_id IS 'League identifier';
COMMENT ON COLUMN match.season IS 'Season of the match';
COMMENT ON COLUMN match.stage IS 'Stage of the match';
COMMENT ON COLUMN match.date IS 'Date of the match (e.g. 2008-08-17 00:00:00)';
COMMENT ON COLUMN match.match_api_id IS 'Match API identifier';
COMMENT ON COLUMN match.home_team_api_id IS 'Home team API identifier';
COMMENT ON COLUMN match.away_team_api_id IS 'Away team API identifier';
COMMENT ON COLUMN match.home_team_goal IS 'Goals scored by the home team';
COMMENT ON COLUMN match.away_team_goal IS 'Goals scored by the away team';
COMMENT ON COLUMN match.goal IS 'Goal events of the match';
COMMENT ON COLUMN match.shoton IS 'Shot on goal events - shots that enter the goal or would have entered if not blocked by goalkeeper or defensive player';
COMMENT ON COLUMN match.shotoff IS 'Shot off goal events - shots that miss the target, opposite of shot on';
COMMENT ON COLUMN match.foulcommit IS 'Fouls committed during the match';
COMMENT ON COLUMN match.card IS 'Cards (yellow/red) given during the match';
COMMENT ON COLUMN match.cross IS 'Balls sent into the opposition team''s area from a wide position';
COMMENT ON COLUMN match.corner IS 'Corner kick events when ball goes out of play';
COMMENT ON COLUMN match.possession IS 'Ball possession duration from when a player takes over the ball';

-- Player table column comments
COMMENT ON COLUMN player.id IS 'Unique identifier for players';
COMMENT ON COLUMN player.player_api_id IS 'Player API identifier';
COMMENT ON COLUMN player.player_name IS 'Player name';
COMMENT ON COLUMN player.player_fifa_api_id IS 'Player FIFA API identifier';
COMMENT ON COLUMN player.birthday IS 'Player''s birth date (e.g. 1992-02-29 00:00:00) - earlier dates indicate older players';
COMMENT ON COLUMN player.height IS 'Player''s height';
COMMENT ON COLUMN player.weight IS 'Player''s weight';

-- Player_Attributes table column comments
COMMENT ON COLUMN player_attributes.id IS 'Unique identifier for players';
COMMENT ON COLUMN player_attributes.player_fifa_api_id IS 'Player FIFA API identifier';
COMMENT ON COLUMN player_attributes.player_api_id IS 'Player API identifier';
COMMENT ON COLUMN player_attributes.date IS 'Date of attribute assessment (e.g. 2016-02-18 00:00:00)';
COMMENT ON COLUMN player_attributes.overall_rating IS 'Overall player rating (0-100 calculated by FIFA) - higher rating means stronger overall ability';
COMMENT ON COLUMN player_attributes.potential IS 'Player potential score (0-100 calculated by FIFA) - higher score indicates greater future potential';
COMMENT ON COLUMN player_attributes.preferred_foot IS 'Player''s preferred foot when attacking (right/left)';
COMMENT ON COLUMN player_attributes.attacking_work_rate IS 'Player''s attacking work rate - high: joins all attacks, medium: selective participation, low: stays in position';
COMMENT ON COLUMN player_attributes.defensive_work_rate IS 'Player''s defensive work rate - high: stays in position for defense, medium: selective participation, low: focuses on attacking';
COMMENT ON COLUMN player_attributes.crossing IS 'Crossing ability score (0-100) - measures performance in long passes into opponent''s goal area for headers';
COMMENT ON COLUMN player_attributes.finishing IS 'Finishing ability score (0-100 calculated by FIFA)';
COMMENT ON COLUMN player_attributes.heading_accuracy IS 'Heading accuracy score (0-100 calculated by FIFA)';
COMMENT ON COLUMN player_attributes.short_passing IS 'Short passing ability score (0-100 calculated by FIFA)';
COMMENT ON COLUMN player_attributes.volleys IS 'Volley technique score (0-100 calculated by FIFA)';
COMMENT ON COLUMN player_attributes.dribbling IS 'Dribbling ability score (0-100 calculated by FIFA)';
COMMENT ON COLUMN player_attributes.curve IS 'Ball curve technique score (0-100 calculated by FIFA)';
COMMENT ON COLUMN player_attributes.free_kick_accuracy IS 'Free kick accuracy score (0-100 calculated by FIFA)';
COMMENT ON COLUMN player_attributes.long_passing IS 'Long passing ability score (0-100 calculated by FIFA)';
COMMENT ON COLUMN player_attributes.ball_control IS 'Ball control skill score (0-100 calculated by FIFA)';
COMMENT ON COLUMN player_attributes.acceleration IS 'Acceleration speed score (0-100 calculated by FIFA)';
COMMENT ON COLUMN player_attributes.sprint_speed IS 'Sprint speed score (0-100 calculated by FIFA)';
COMMENT ON COLUMN player_attributes.agility IS 'Agility score (0-100 calculated by FIFA)';
COMMENT ON COLUMN player_attributes.reactions IS 'Reaction time score (0-100 calculated by FIFA)';
COMMENT ON COLUMN player_attributes.balance IS 'Balance score (0-100 calculated by FIFA)';
COMMENT ON COLUMN player_attributes.shot_power IS 'Shot power score (0-100 calculated by FIFA)';
COMMENT ON COLUMN player_attributes.jumping IS 'Jumping ability score (0-100 calculated by FIFA)';
COMMENT ON COLUMN player_attributes.stamina IS 'Stamina score (0-100 calculated by FIFA)';
COMMENT ON COLUMN player_attributes.strength IS 'Physical strength score (0-100 calculated by FIFA)';
COMMENT ON COLUMN player_attributes.long_shots IS 'Long range shooting ability score (0-100 calculated by FIFA)';
COMMENT ON COLUMN player_attributes.aggression IS 'Aggression level score (0-100 calculated by FIFA)';
COMMENT ON COLUMN player_attributes.interceptions IS 'Interception ability score (0-100 calculated by FIFA)';
COMMENT ON COLUMN player_attributes.positioning IS 'Positioning awareness score (0-100 calculated by FIFA)';
COMMENT ON COLUMN player_attributes.vision IS 'Vision and awareness score (0-100 calculated by FIFA)';
COMMENT ON COLUMN player_attributes.penalties IS 'Penalty taking ability score (0-100 calculated by FIFA)';
COMMENT ON COLUMN player_attributes.marking IS 'Marking ability score (0-100 calculated by FIFA)';
COMMENT ON COLUMN player_attributes.standing_tackle IS 'Standing tackle technique score (0-100 calculated by FIFA)';
COMMENT ON COLUMN player_attributes.sliding_tackle IS 'Sliding tackle technique score (0-100 calculated by FIFA)';
COMMENT ON COLUMN player_attributes.gk_diving IS 'Goalkeeper diving ability score (0-100 calculated by FIFA)';
COMMENT ON COLUMN player_attributes.gk_handling IS 'Goalkeeper ball handling ability score (0-100 calculated by FIFA)';
COMMENT ON COLUMN player_attributes.gk_kicking IS 'Goalkeeper kicking ability score (0-100 calculated by FIFA)';
COMMENT ON COLUMN player_attributes.gk_positioning IS 'Goalkeeper positioning ability score (0-100 calculated by FIFA)';
COMMENT ON COLUMN player_attributes.gk_reflexes IS 'Goalkeeper reflexes score (0-100 calculated by FIFA)';

-- Team table column comments
COMMENT ON COLUMN team.id IS 'Unique identifier for teams';
COMMENT ON COLUMN team.team_api_id IS 'Team API identifier';
COMMENT ON COLUMN team.team_fifa_api_id IS 'Team FIFA API identifier';
COMMENT ON COLUMN team.team_long_name IS 'Team''s full name';
COMMENT ON COLUMN team.team_short_name IS 'Team''s abbreviated name';

-- Team_Attributes table column comments
COMMENT ON COLUMN team_attributes.id IS 'Unique identifier for teams';
COMMENT ON COLUMN team_attributes.team_fifa_api_id IS 'Team FIFA API identifier';
COMMENT ON COLUMN team_attributes.team_api_id IS 'Team API identifier';
COMMENT ON COLUMN team_attributes.date IS 'Date of attribute assessment (e.g. 2010-02-22 00:00:00)';
COMMENT ON COLUMN team_attributes.buildupplayspeed IS 'Speed of attack formation (1-100) - how quickly attacks are put together';
COMMENT ON COLUMN team_attributes.buildupplayspeedclass IS 'Attack speed classification - Slow: 1-33, Balanced: 34-66, Fast: 66-100';
COMMENT ON COLUMN team_attributes.buildupplaydribbling IS 'Tendency/frequency of dribbling during build-up play';
COMMENT ON COLUMN team_attributes.buildupplaydribblingclass IS 'Dribbling classification - Little: 1-33, Normal: 34-66, Lots: 66-100';
COMMENT ON COLUMN team_attributes.buildupplaypassing IS 'Passing distance preference and teammate support level during build-up';
COMMENT ON COLUMN team_attributes.buildupplaypassingclass IS 'Passing style classification - Short: 1-33, Mixed: 34-66, Long: 66-100';
COMMENT ON COLUMN team_attributes.buildupplaypositioningclass IS 'Team''s freedom of movement in the first two thirds of the pitch (Organised/Free Form)';
COMMENT ON COLUMN team_attributes.chancecreationpassing IS 'Risk level in passing decisions and run support for creating chances';
COMMENT ON COLUMN team_attributes.chancecreationpassingclass IS 'Chance creation passing risk - Safe: 1-33, Normal: 34-66, Risky: 66-100';
COMMENT ON COLUMN team_attributes.chancecreationcrossing IS 'Tendency/frequency of crosses into the penalty box';
COMMENT ON COLUMN team_attributes.chancecreationcrossingclass IS 'Crossing frequency classification - Little: 1-33, Normal: 34-66, Lots: 66-100';
COMMENT ON COLUMN team_attributes.chancecreationshooting IS 'Tendency/frequency of shots taken';
COMMENT ON COLUMN team_attributes.chancecreationshootingclass IS 'Shooting frequency classification - Little: 1-33, Normal: 34-66, Lots: 66-100';
COMMENT ON COLUMN team_attributes.chancecreationpositioningclass IS 'Team''s freedom of movement in the final third of the pitch (Organised/Free Form)';
COMMENT ON COLUMN team_attributes.defencepressure IS 'How high up the pitch the team starts pressuring opponents';
COMMENT ON COLUMN team_attributes.defencepressureclass IS 'Defensive pressure style - Deep: 1-33, Medium: 34-66, High: 66-100';
COMMENT ON COLUMN team_attributes.defenceaggression IS 'Team''s approach to tackling the ball possessor';
COMMENT ON COLUMN team_attributes.defenceaggressionclass IS 'Defensive aggression style - Contain: 1-33, Press: 34-66, Double: 66-100';
COMMENT ON COLUMN team_attributes.defenceteamwidth IS 'How much the team shifts toward the ball side';
COMMENT ON COLUMN team_attributes.defenceteamwidthclass IS 'Defensive width classification - Narrow: 1-33, Normal: 34-66, Wide: 66-100';
COMMENT ON COLUMN team_attributes.defencedefenderlineclass IS 'Defensive shape and strategy (Cover/Offside Trap)';