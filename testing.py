import pkg_resources
from symspellpy.symspellpy import SymSpell, Verbosity

# Initialize SysmSpell object

sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
dictionary_path = pkg_resources.resource_filename("symspellpy", "frequency_dictionary_en_82_765.txt")
bigram_path = pkg_resources.resource_filename("symspellpy", "frequency_bigramdictionary_en_243_342.txt")


sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)
sym_spell.load_bigram_dictionary(bigram_path, term_index=0, count_index=2)

inp= "byr"

sugs = sym_spell.lookup(inp, Verbosity.CLOSEST, max_edit_distance=2)

for g in sugs:
    print(g.term)