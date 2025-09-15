COMMENT ON COLUMN bond.bond_id IS 'unique id representing bonds. TRxxx_A1_A2: TRXXX refers to which molecule A1 and A2 refers to which atom';
COMMENT ON COLUMN bond.molecule_id IS 'identifying the molecule in which the bond appears';
COMMENT ON COLUMN bond.bond_type IS 'type of the bond. "-": single bond "=": double bond "#": triple bond';

COMMENT ON COLUMN connected.atom_id IS 'id of the first atom';
COMMENT ON COLUMN connected.atom_id2 IS 'id of the second atom';
COMMENT ON COLUMN connected.bond_id IS 'bond id representing bond between two atoms';

COMMENT ON COLUMN molecule.molecule_id IS 'unique id of molecule';
COMMENT ON COLUMN molecule.label IS 'whether this molecule is carcinogenic or not. "+": this molecule / compound is carcinogenic "-": this molecule / compound is not carcinogenic';

COMMENT ON COLUMN atom.atom_id IS 'the unique id of atoms';
COMMENT ON COLUMN atom.molecule_id IS 'identifying the molecule to which the atom belongs. TRXXX_i represents ith atom of molecule TRXXX';
COMMENT ON COLUMN atom.element IS 'the element of the toxicology. cl: chlorine c: carbon h: hydrogen o: oxygen s: sulfur n: nitrogen p: phosphorus na: sodium br: bromine f: fluorine i: iodine sn: Tin pb: lead te: tellurium ca: Calcium';

-- Add table comments
COMMENT ON TABLE bond IS 'Defines the type of chemical bonds (single, double, triple) that exist within molecules.';
COMMENT ON TABLE connected IS 'A linking table that explicitly defines which two atoms are joined by a specific bond.';
COMMENT ON TABLE molecule IS 'Stores information for each chemical molecule, including its carcinogenicity classification.';
COMMENT ON TABLE atom IS 'Contains a list of all atoms, specifying their chemical element and the molecule they belong to.';