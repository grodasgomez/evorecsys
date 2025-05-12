import spacy
import time
from geneticalgorithm.restriction.ConsistencyAndDiversityRestriction import ConsistencyAndDiversityRestriction

restriction = ConsistencyAndDiversityRestriction()

set = restriction.create_similarity_based_set(["Bread (French)", "Bread (pita white)"])

print(set)
