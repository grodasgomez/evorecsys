from src.ontology.bundle.Bundle import Bundle

# This class represents the restriction related to the healthiness of the food items.
class LoadGlycemicRestriction:

    MAX_LOAD_GLYCEMIC_INDEX_PER_MEAL = 400

    def evaluate(self, phenotype: list[Bundle]):
        load_glycemic_scores = []

        for bundle in phenotype:

            meal = bundle.meal
            assert meal.glycemic_load >= 0, "Glycemic load is not positive"

            load_glycemic_score = meal.glycemic_load / self.MAX_LOAD_GLYCEMIC_INDEX_PER_MEAL
            load_glycemic_scores.append(load_glycemic_score)

        aptitude = sum(load_glycemic_scores) / len(load_glycemic_scores)

        return aptitude
