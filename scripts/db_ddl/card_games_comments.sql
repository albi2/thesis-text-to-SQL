-- Comments for cards table
COMMENT ON COLUMN cards.id IS 'Unique identifier for each card';
COMMENT ON COLUMN cards.artist IS 'The name of the artist that illustrated the card art';
COMMENT ON COLUMN cards.asciiName IS 'Card name formatted with no special unicode characters';
COMMENT ON COLUMN cards.availability IS 'Available printing types: arena, dreamcast, mtgo, paper, shandalar';
COMMENT ON COLUMN cards.borderColor IS 'Color of the card border: black, borderless, gold, silver, white';
COMMENT ON COLUMN cards.cardKingdomFoilId IS 'Card Kingdom Foil identifier - when paired with cardKingdomId provides powerful functionality';
COMMENT ON COLUMN cards.cardKingdomId IS 'Card Kingdom identifier';
COMMENT ON COLUMN cards.colorIdentity IS 'All colors found in mana cost, color indicator, and text';
COMMENT ON COLUMN cards.colorIndicator IS 'Colors in the color indicator (symbol prefixed to card types)';
COMMENT ON COLUMN cards.colors IS 'All colors in mana cost and color indicator. Some cards may not have values, such as cards with "Devoid" in text';
COMMENT ON COLUMN cards.convertedManaCost IS 'The converted mana cost of the card - higher values mean more expensive mana cost';
COMMENT ON COLUMN cards.duelDeck IS 'Indicator for which duel deck the card belongs to';
COMMENT ON COLUMN cards.edhrecRank IS 'Card rank on EDHRec';
COMMENT ON COLUMN cards.faceConvertedManaCost IS 'Converted mana cost for the face of split or double-faced cards - higher values mean more expensive mana cost for that face';
COMMENT ON COLUMN cards.faceName IS 'Name on the face of the card';
COMMENT ON COLUMN cards.flavorName IS 'Promotional card name printed above the true card name on special cards with no game function';
COMMENT ON COLUMN cards.flavorText IS 'Italicized text below the rules text that has no game function';
COMMENT ON COLUMN cards.frameEffects IS 'Visual frame effects: colorshifted, companion, compasslanddfc, devoid, draft, etched, extendedart, fullart, inverted, legendary, lesson, miracle, mooneldrazidfc, nyxtouched, originpwdfc, showcase, snow, sunmoondfc, textless, tombstone, waxingandwaningmoondfc';
COMMENT ON COLUMN cards.frameVersion IS 'Version of the card frame style: 1993, 1997, 2003, 2015, future';
COMMENT ON COLUMN cards.hand IS 'Starting maximum hand size total modifier. Positive (+1, +2), negative (-1), or neutral (0)';
COMMENT ON COLUMN cards.hasAlternativeDeckLimit IS 'Whether the card allows other than 4 copies in a deck: 0=disallow, 1=allow';
COMMENT ON COLUMN cards.hasContentWarning IS 'Whether the card is marked by Wizards of the Coast for sensitive content: 0=no, 1=yes. Cards with this property may have missing or degraded properties';
COMMENT ON COLUMN cards.hasFoil IS 'Whether the card can be found in foil: 0=cannot, 1=can';
COMMENT ON COLUMN cards.hasNonFoil IS 'Whether the card can be found in non-foil: 0=cannot, 1=can';
COMMENT ON COLUMN cards.isAlternative IS 'Whether the card is an alternate variation to an original printing: 0=no, 1=yes';
COMMENT ON COLUMN cards.isFullArt IS 'Whether the card has full artwork: 0=no, 1=yes';
COMMENT ON COLUMN cards.isOnlineOnly IS 'Whether the card is only available in online game variations: 0=no, 1=yes';
COMMENT ON COLUMN cards.isOversized IS 'Whether the card is oversized: 0=no, 1=yes';
COMMENT ON COLUMN cards.isPromo IS 'Whether the card is a promotional printing: 0=no, 1=yes';
COMMENT ON COLUMN cards.isReprint IS 'Whether the card has been reprinted: 0=no, 1=yes';
COMMENT ON COLUMN cards.isReserved IS 'Whether the card is on the Magic: The Gathering Reserved List: 0=no, 1=yes';
COMMENT ON COLUMN cards.isStarter IS 'Whether the card is found in a starter deck such as Planeswalker/Brawl decks: 0=no, 1=yes';
COMMENT ON COLUMN cards.isStorySpotlight IS 'Whether the card is a Story Spotlight card: 0=no, 1=yes';
COMMENT ON COLUMN cards.isTextless IS 'Whether the card has a text box: 0=has text box, 1=no text box';
COMMENT ON COLUMN cards.isTimeshifted IS 'Whether the card is time shifted - a feature where cards have different frame versions: 0=no, 1=yes';
COMMENT ON COLUMN cards.keywords IS 'List of keywords found on the card';
COMMENT ON COLUMN cards.layout IS 'Type of card layout. For token cards, this will be "token"';
COMMENT ON COLUMN cards.leadershipSkills IS 'List of formats the card is legal to be a commander in';
COMMENT ON COLUMN cards.life IS 'Starting life total modifier with plus or minus character preceding integer';
COMMENT ON COLUMN cards.loyalty IS 'Starting loyalty value of the card. Used only on Planeswalker cards, empty means unknown';
COMMENT ON COLUMN cards.manaCost IS 'Mana cost of the card wrapped in brackets for each value - this is unconverted mana cost';
COMMENT ON COLUMN cards.name IS 'Name of the card. Cards with multiple faces like Split and Meld cards are given a delimiter';
COMMENT ON COLUMN cards.number IS 'Number of the card';
COMMENT ON COLUMN cards.originalReleaseDate IS 'Original release date for promotional cards printed outside of a cycle window, such as Secret Lair Drop promotions';
COMMENT ON COLUMN cards.originalText IS 'Text on the card as originally printed';
COMMENT ON COLUMN cards.originalType IS 'Type of the card as originally printed, including any supertypes and subtypes';
COMMENT ON COLUMN cards.otherFaceIds IS 'List of card UUIDs to this card''s counterparts, such as transformed or melded faces';
COMMENT ON COLUMN cards.power IS 'Power of the card. ∞ means infinite power, null or * refers to unknown power';
COMMENT ON COLUMN cards.printings IS 'List of set printing codes the card was printed in, formatted in uppercase';
COMMENT ON COLUMN cards.promoTypes IS 'List of promotional types: arenaleague, boosterfun, boxtopper, brawldeck, bundle, buyabox, convention, datestamped, draculaseries, draftweekend, duels, event, fnm, gameday, gateway, giftbox, gilded, godzillaseries, instore, intropack, jpwalker, judgegift, league, mediainsert, neonink, openhouse, planeswalkerstamped, playerrewards, playpromo, premiereshop, prerelease, promopack, release, setpromo, stamped, textured, themepack, thick, tourney, wizardsplaynetwork';
COMMENT ON COLUMN cards.purchaseUrls IS 'Links that navigate to websites where the card can be purchased';
COMMENT ON COLUMN cards.rarity IS 'Card printing rarity';
COMMENT ON COLUMN cards.setCode IS 'Set printing code that the card is from';
COMMENT ON COLUMN cards.side IS 'Identifier of the card side. Used on cards with multiple faces on the same card. Empty means single-faced card';
COMMENT ON COLUMN cards.subtypes IS 'List of card subtypes found after em-dash';
COMMENT ON COLUMN cards.supertypes IS 'List of card supertypes found before em-dash. All types should be the union of subtypes and supertypes';
COMMENT ON COLUMN cards.text IS 'Rules text of the card';
COMMENT ON COLUMN cards.toughness IS 'Toughness of the card';
COMMENT ON COLUMN cards.type IS 'Type of the card as visible, including any supertypes and subtypes: Artifact, Card, Conspiracy, Creature, Dragon, Dungeon, Eaturecray, Elemental, Elite, Emblem, Enchantment, Ever, Goblin, Hero, Instant, Jaguar, Knights, Land, Phenomenon, Plane, Planeswalker, Scariest, Scheme, See, Sorcery, Sticker, Summon, Token, Tribal, Vanguard, Wolf, Youâ€™ll, instant';
COMMENT ON COLUMN cards.types IS 'List of all card types of the card, including Un-sets and gameplay variants';
COMMENT ON COLUMN cards.variations IS 'Card variations';
COMMENT ON COLUMN cards.watermark IS 'Name of the watermark on the card';

-- Comments for foreign_data table
COMMENT ON COLUMN foreign_data.id IS 'Unique identifier for this foreign data entry';
COMMENT ON COLUMN foreign_data.flavorText IS 'Foreign flavor text of the card';
COMMENT ON COLUMN foreign_data.language IS 'Foreign language of the card';
COMMENT ON COLUMN foreign_data.multiverseid IS 'Foreign multiverse identifier of the card';
COMMENT ON COLUMN foreign_data.name IS 'Foreign name of the card';
COMMENT ON COLUMN foreign_data.text IS 'Foreign text ruling of the card';
COMMENT ON COLUMN foreign_data.type IS 'Foreign type of the card, including any supertypes and subtypes';

-- Comments for legalities table
COMMENT ON COLUMN legalities.id IS 'Unique identifier for this legality entry';
COMMENT ON COLUMN legalities.format IS 'Format of play - each value refers to different rules to play';
COMMENT ON COLUMN legalities.status IS 'Legal status: legal, banned, or restricted';

-- Comments for rulings table
COMMENT ON COLUMN rulings.id IS 'Unique identifier for this ruling';
COMMENT ON COLUMN rulings.date IS 'Date of the ruling';
COMMENT ON COLUMN rulings.text IS 'Description of this ruling';

-- Comments for set_translations table
COMMENT ON COLUMN set_translations.id IS 'Unique identifier for this set translation';
COMMENT ON COLUMN set_translations.language IS 'Language of this card set';
COMMENT ON COLUMN set_translations.setCode IS 'Set code for this set';
COMMENT ON COLUMN set_translations.translation IS 'Translation of this card set';

-- Comments for sets table
COMMENT ON COLUMN sets.id IS 'Unique identifier for this set';
COMMENT ON COLUMN sets.baseSetSize IS 'Number of cards in the set';
COMMENT ON COLUMN sets.block IS 'Block name the set was in';
COMMENT ON COLUMN sets.booster IS 'Breakdown of possibilities and weights of cards in a booster pack';
COMMENT ON COLUMN sets.code IS 'Set code for the set';
COMMENT ON COLUMN sets.isFoilOnly IS 'Whether the set is only available in foil: 0=no, 1=yes';
COMMENT ON COLUMN sets.isForeignOnly IS 'Whether the set is available only outside the United States of America: 0=no, 1=yes';
COMMENT ON COLUMN sets.isNonFoilOnly IS 'Whether the set is only available in non-foil: 0=no, 1=yes';
COMMENT ON COLUMN sets.isOnlineOnly IS 'Whether the set is only available in online game variations: 0=no, 1=yes';
COMMENT ON COLUMN sets.isPartialPreview IS 'Whether the set is still in preview (spoiled). Preview sets do not have complete data: 0=no, 1=yes';
COMMENT ON COLUMN sets.keyruneCode IS 'Matching Keyrune code for set image icons';
COMMENT ON COLUMN sets.mcmId IS 'Magic Card Market set identifier';
COMMENT ON COLUMN sets.mcmIdExtras IS 'Split Magic Card Market set identifier if a set is printed in two sets - represents the second set identifier';
COMMENT ON COLUMN sets.mcmName IS 'Magic Card Market name';
COMMENT ON COLUMN sets.mtgoCode IS 'Set code as it appears on Magic: The Gathering Online. If null or empty, then it doesn''t appear on MTGO';
COMMENT ON COLUMN sets.name IS 'Name of the set';
COMMENT ON COLUMN sets.parentCode IS 'Parent set code for set variations like promotions, guild kits, etc.';
COMMENT ON COLUMN sets.releaseDate IS 'Release date of the set';
COMMENT ON COLUMN sets.tcgplayerGroupId IS 'Group identifier of the set on TCGplayer';
COMMENT ON COLUMN sets.totalSetSize IS 'Total number of cards in the set, including promotional and related supplemental products but excluding Alchemy modifications';
COMMENT ON COLUMN sets.type IS 'Expansion type of the set: alchemy, archenemy, arsenal, box, commander, core, draft_innovation, duel_deck, expansion, from_the_vault, funny, masterpiece, masters, memorabilia, planechase, premium_deck, promo, spellbook, starter, token, treasure_chest, vanguard';