-- Add column comments for badges table
COMMENT ON COLUMN badges.id IS 'The badge identifier';
COMMENT ON COLUMN badges.userid IS 'The unique identifier of the user who obtained the badge';
COMMENT ON COLUMN badges.name IS 'The badge name the user obtained';
COMMENT ON COLUMN badges.date IS 'The date that the user obtained the badge';

-- Add column comments for comments table
COMMENT ON COLUMN comments.id IS 'The comment identifier';
COMMENT ON COLUMN comments.postid IS 'The unique identifier of the post being commented on';
COMMENT ON COLUMN comments.score IS 'Rating score. Scores above 60 indicate positive comments, scores below 60 indicate negative comments';
COMMENT ON COLUMN comments.text IS 'The detailed content of the comment';
COMMENT ON COLUMN comments.creationdate IS 'The creation date of the comment';
COMMENT ON COLUMN comments.userid IS 'The identifier of the user who posted the comment';
COMMENT ON COLUMN comments.userdisplayname IS 'User''s display name';

-- Add column comments for posthistory table
COMMENT ON COLUMN posthistory.id IS 'The post history identifier';
COMMENT ON COLUMN posthistory.posthistorytypeid IS 'The identifier of the post history type';
COMMENT ON COLUMN posthistory.postid IS 'The unique identifier of the post';
COMMENT ON COLUMN posthistory.revisionguid IS 'The revision globally unique identifier of the post';
COMMENT ON COLUMN posthistory.creationdate IS 'The creation date of the post';
COMMENT ON COLUMN posthistory.userid IS 'The user who posted the post';
COMMENT ON COLUMN posthistory.text IS 'The detailed content of the post';
COMMENT ON COLUMN posthistory.comment IS 'Comments of the post';
COMMENT ON COLUMN posthistory.userdisplayname IS 'User''s display name';

-- Add column comments for postlinks table
COMMENT ON COLUMN postlinks.id IS 'The post link identifier';
COMMENT ON COLUMN postlinks.creationdate IS 'The creation date of the post link';
COMMENT ON COLUMN postlinks.postid IS 'The post identifier';
COMMENT ON COLUMN postlinks.relatedpostid IS 'The identifier of the related post';
COMMENT ON COLUMN postlinks.linktypeid IS 'The identifier of the link type';

-- Add column comments for posts table
COMMENT ON COLUMN posts.id IS 'The post identifier';
COMMENT ON COLUMN posts.posttypeid IS 'The identifier of the post type';
COMMENT ON COLUMN posts.acceptedanswerid IS 'The accepted answer identifier of the post';
COMMENT ON COLUMN posts.creaiondate IS 'The creation date of the post';
COMMENT ON COLUMN posts.score IS 'The score of the post';
COMMENT ON COLUMN posts.viewcount IS 'The view count of the post. Higher view count indicates higher popularity';
COMMENT ON COLUMN posts.body IS 'The body content of the post';
COMMENT ON COLUMN posts.owneruserid IS 'The identifier of the owner user';
COMMENT ON COLUMN posts.lasactivitydate IS 'The last activity date';
COMMENT ON COLUMN posts.title IS 'The title of the post';
COMMENT ON COLUMN posts.tags IS 'The tags associated with the post';
COMMENT ON COLUMN posts.answercount IS 'The total number of answers to the post';
COMMENT ON COLUMN posts.commentcount IS 'The total number of comments on the post';
COMMENT ON COLUMN posts.favoritecount IS 'The total number of favorites for the post. Higher favorite count indicates more valuable posts';
COMMENT ON COLUMN posts.lasteditoruserid IS 'The identifier of the last editor';
COMMENT ON COLUMN posts.lasteditdate IS 'The last edit date';
COMMENT ON COLUMN posts.communityowneddate IS 'The community owned date';
COMMENT ON COLUMN posts.parentid IS 'The identifier of the parent post. If null, this is a root post; otherwise, it is a child post of another post';
COMMENT ON COLUMN posts.closeddate IS 'The closed date of the post. If null or empty, the post is not well-finished; if not null, the post is well-finished';
COMMENT ON COLUMN posts.ownerdisplayname IS 'The display name of the post owner';
COMMENT ON COLUMN posts.lasteditordisplayname IS 'The display name of the last editor';

-- Add column comments for tags table
COMMENT ON COLUMN tags.id IS 'The tag identifier';
COMMENT ON COLUMN tags.tagname IS 'The name of the tag';
COMMENT ON COLUMN tags.count IS 'The count of posts that contain this tag. Higher counts indicate more popular tags';
COMMENT ON COLUMN tags.excerptpostid IS 'The excerpt post identifier of the tag';
COMMENT ON COLUMN tags.wikipostid IS 'The wiki post identifier of the tag';

-- Add column comments for users table
COMMENT ON COLUMN users.id IS 'The user identifier';
COMMENT ON COLUMN users.reputation IS 'The user''s reputation. Users with higher reputation have more influence';
COMMENT ON COLUMN users.creationdate IS 'The creation date of the user account';
COMMENT ON COLUMN users.displayname IS 'The user''s display name';
COMMENT ON COLUMN users.lastaccessdate IS 'The last access date of the user account';
COMMENT ON COLUMN users.websiteurl IS 'The website URL of the user account';
COMMENT ON COLUMN users.location IS 'User''s location';
COMMENT ON COLUMN users.aboutme IS 'The self introduction of the user';
COMMENT ON COLUMN users.views IS 'The number of profile views';
COMMENT ON COLUMN users.upvotes IS 'The number of upvotes given by the user';
COMMENT ON COLUMN users.downvotes IS 'The number of downvotes given by the user';
COMMENT ON COLUMN users.accountid IS 'The unique identifier of the account';
COMMENT ON COLUMN users.age IS 'User''s age. Teenager: 13-18, Adult: 19-65, Elder: >65';
COMMENT ON COLUMN users.profileimageurl IS 'The profile image URL';

-- Add column comments for votes table
COMMENT ON COLUMN votes.id IS 'The vote identifier';
COMMENT ON COLUMN votes.postid IS 'The identifier of the post that is voted on';
COMMENT ON COLUMN votes.votetypeid IS 'The identifier of the vote type';
COMMENT ON COLUMN votes.creationdate IS 'The creation date of the vote';
COMMENT ON COLUMN votes.userid IS 'The identifier of the voter';
COMMENT ON COLUMN votes.bountyamount IS 'The amount of bounty associated with the vote';