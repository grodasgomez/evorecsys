# All necessary libraries and imports from other files.
from src.geneticalgorithm.Individual import Individual
from src.geneticalgorithm.restriction.ConsistencyAndDiversityRestriction import ConsistencyAndDiversityRestriction
from src.geneticalgorithm.restriction.UserPreferencesRestriction import UserPreferencesRestriction
from src.geneticalgorithm.restriction.HealthyFoodRestriction import HealthyFoodRestriction
from src.geneticalgorithm.restriction.PARestriction import PARestriction
from src.ontology.user.PAPreferenceData import PAPreferenceData
from src.ontology.user.FoodPreferenceData import FoodPreferenceData
from src.ontology.user.PhysicalData import PhysicalData
from src.geneticalgorithm.Population import Population
from src.geneticalgorithm.MOEAD import MOEAD
from src.database.ItemsConnection import ItemsConnection
import random
import copy
import time
# from src.visualization.plot_4d_population import plot_4d_population, plot_4d_population_interactive


# This class represents a Genetic Algorithm. It uses the information of the current user and the most similar user data
# obtained by the nearest-neighbour collaborative filtering step.
class GeneticAlgorithmMOEAD:

    NUMBER_OF_MEALS_PER_DAY = 3

    #Constructor
    def __init__(self, user_data, most_similar_user_data):

        self.number_of_individuals = 455
        self.number_of_generations = 50
        self.neighborhood_size = 20
        self.physical_data: PhysicalData
        self.food_preferences: FoodPreferenceData
        self.pa_preferences: PAPreferenceData
        self.food_items = {}
        self.pa_items = []
        self.restrictions = []
        self.mutation_dictionary = {}
        self.moead = None

        self.__configure_data(user_data, most_similar_user_data)

    # This method executes the main steps of the Genetic Algorithm.
    def execute_genetic_algorithm(self):

        print('I have started the evolutionary process...')
        start_time = time.time()
        
        # Initialize MOEA/D
        self.moead = MOEAD(self.number_of_individuals, len(self.restrictions), self.neighborhood_size)
        self.moead.initialize_weight_vectors()
        self.moead.initialize_neighborhoods()
        
        # Create initial population
        population = Population(self.physical_data, self.food_preferences, self.pa_preferences, self.food_items,
                                self.pa_items, self.number_of_individuals, self.restrictions,
                                self.mutation_dictionary)
        population.create_population()
        population.evaluate_population()
        self.moead.initialize_reference_point(population)
        
        offspring_times = []
        evaluation_times = []
        update_reference_point_times = []
        update_neighborhood_times = []
        update_external_population_times = []
        
        generation_index = 0
        algorithm_start_time = time.time()
        while generation_index <= self.number_of_generations:
            # For each subproblem
            for i in range(self.number_of_individuals):
                # Select parents from neighborhood
                neighborhood = self.moead.neighborhoods[i]
                parents = random.sample(neighborhood, 2)
                parent1 = population.initial_population[parents[0]]
                parent2 = population.initial_population[parents[1]]
                
                # Create offspring
                offsprint_start_time = time.time()
                offspring = self.__create_offspring(parent1, parent2, population)
                offsprint_end_time = time.time()
                offspring_times.append(offsprint_end_time - offsprint_start_time)
                # Evaluate offspring
                evaluation_start_time = time.time()
                offspring.evaluate_phenotype(self.restrictions)
                evaluation_end_time = time.time()
                evaluation_times.append(evaluation_end_time - evaluation_start_time)
                # Update reference point
                update_reference_point_start_time = time.time()
                self.moead.update_reference_point(offspring) 
                update_reference_point_end_time = time.time()
                update_reference_point_times.append(update_reference_point_end_time - update_reference_point_start_time)
                
                # Update solutions in neighborhood
                for j in neighborhood:
                    update_neighborhood_start_time = time.time()
                    current_solution = population.initial_population[j]
                    current_scalar = self.moead.tchebycheff_scalarization(current_solution, self.moead.weight_vectors[j])
                    offspring_scalar = self.moead.tchebycheff_scalarization(offspring, self.moead.weight_vectors[j])
                    
                    if offspring_scalar < current_scalar:
                        # Replace solution and update objective values (FV^j = F(y'))
                        population.initial_population[j] = copy.deepcopy(offspring)
                    update_neighborhood_end_time = time.time()
                    update_neighborhood_times.append(update_neighborhood_end_time - update_neighborhood_start_time)
                
                # Update external population (Step 2.5)
                update_external_population_start_time = time.time()
                self.moead.update_external_population(offspring)
                update_external_population_end_time = time.time()
                update_external_population_times.append(update_external_population_end_time - update_external_population_start_time)
            
            generation_index += 1

        algorithm_end_time = time.time()
        algorithm_execution_time = algorithm_end_time - algorithm_start_time
        external_population = self.moead.external_population

        
        print(f'Algorithm execution time: {algorithm_execution_time:.2f} seconds')

        end_time = time.time()
        execution_time = end_time - start_time
        print(f'Total execution time: {execution_time:.2f} seconds')
        
        print(f'Offspring avg creation time: {sum(offspring_times) / len(offspring_times) * 1000:.3f} milliseconds')
        print(f'Offspring total creation time: {sum(offspring_times):.2f} seconds')

        print(f'Evaluation avg time: {sum(evaluation_times) / len(evaluation_times) * 1000:.3f} milliseconds')
        print(f'Evaluation total time: {sum(evaluation_times):.2f} seconds')

        print(f'Update reference point avg time: {sum(update_reference_point_times) / len(update_reference_point_times) * 1000:.3f} milliseconds')
        print(f'Update reference point total time: {sum(update_reference_point_times):.2f} seconds')

        print(f'Update neighborhood avg time: {sum(update_neighborhood_times) / len(update_neighborhood_times) * 1000:.3f} milliseconds')
        print(f'Update neighborhood total time: {sum(update_neighborhood_times):.2f} seconds')

        print(f'Update external population avg time: {sum(update_external_population_times) / len(update_external_population_times) * 1000:.3f} milliseconds')
        print(f'Update external population total time: {sum(update_external_population_times):.2f} seconds')

        print(f'External population size: {len(external_population)}')

        individual_with_lower_user_preferences_aptitude = min(external_population, key=lambda x: x.user_preferences_aptitude())
        print(f'Individual with the lower aptitude in the User Preferences Restriction')
        print(f'Aptitude: {individual_with_lower_user_preferences_aptitude.aptitude}')
        print(f'Aptitudes: {individual_with_lower_user_preferences_aptitude.aptitudes}')
        print('I have finished; the recommendations are:')
                
    
        # Getting best individual for each aptitude
        best_individual_average = min(
            external_population,
            key=lambda x: x.aptitude
        )
        best_individual_healthier = min(
            external_population,
            key=lambda x: x.aptitudes[Individual.FOOD_RESTRICTION_INDEX]
        )
        best_individual_preference = min(
            external_population,
            key=lambda x: x.aptitudes[Individual.USER_PREFERENCES_RESTRICTION_INDEX]
        )
        best_individual_diverse = min(
            external_population,
            key=lambda x: x.aptitudes[Individual.SEMANTIC_RESTRICTION_INDEX]
        )
        
            
        print("Best individual aptitudes:")
        best_individual_average.print_aptitude()
        print("Best individual aptitude: ", best_individual_average.aptitude)
        # self.__print_phenotype(best_individual.phenotype)

        # Create the visualizations
        # plot_4d_population(external_population, title="External Population Visualization")
        # plot_4d_population_interactive(external_population, title="External Population Interactive Visualization")

        return [best_individual_average, best_individual_healthier, best_individual_preference, best_individual_diverse]

    def __create_offspring(self, parent1, parent2, population):
        # Create a new individual
        offspring = Individual()
        
        # Perform crossover
        if random.random() < Population.CROSSOVER_PROBABILITY:
            # Create new phenotype by combining parents
            new_phenotype = []
            for i in range(len(parent1.phenotype)):
                if random.random() < 0.5:
                    new_phenotype.append(copy.deepcopy(parent1.phenotype[i]))
                else:
                    new_phenotype.append(copy.deepcopy(parent2.phenotype[i]))
            offspring.set_phenotype(new_phenotype)
        else:
            offspring.set_phenotype(copy.deepcopy(parent1.phenotype))
            
        # Perform mutation
        if random.random() < Population.MUTATION_PROBABILITY:
            population.execute_random_swap_of_items(offspring.phenotype)
        
        return offspring

    # This method utilises the information given to configure all the elements needed during the evolutionary execution.
    def __configure_data(self, user_data, most_similar_user_data):

        self.physical_data = PhysicalData(user_data[0], user_data[1], user_data[2], user_data[3], user_data[4],
                                          user_data[29])
        self.food_preferences = FoodPreferenceData(user_data[5], user_data[6], user_data[7], user_data[8], user_data[9],
                                                   user_data[10], user_data[11], user_data[12], user_data[13],
                                                   user_data[14], user_data[15], user_data[16], user_data[17],
                                                   user_data[18])
        high_evaluated_food_types = self.food_preferences.get_higher_evaluated_types()
        self.pa_preferences = PAPreferenceData(user_data[19], user_data[20], user_data[21], user_data[22],
                                               user_data[23], user_data[24],user_data[25], user_data[26],
                                               user_data[27], user_data[28])
        high_evaluated_activities = self.pa_preferences.get_higher_evaluated_activities()

        has_diabetes = user_data[30]
        self.__get_items()
        self.__initialise_restrictions(high_evaluated_food_types, high_evaluated_activities, has_diabetes)
        self.__get_high_evaluated_preferences_of_similar_user(most_similar_user_data)

    # This method retrieves both food and physical activity data according to the preferences of the current user.
    def __get_items(self):

        connection = ItemsConnection()
        self.food_items = connection.retrieve_food_items(self.food_preferences)

        if self.physical_data.goal == 3:

            self.pa_items = connection.retrieve_pa_items(self.pa_preferences, True)

        else:

            self.pa_items = connection.retrieve_pa_items(self.pa_preferences)

        random.shuffle(self.food_items.get("main"))
        random.shuffle(self.food_items.get("side"))
        random.shuffle(self.pa_items)

    # This method initalises the list of restrictions to evaluate individuals.
    def __initialise_restrictions(self, high_evaluated_food_types, high_evaluated_activity_types, has_diabetes):

        self.__build_healthy_food_restriction(has_diabetes)
        self.__build_diversity_and_consistency_restriction()
        self.__build_pa_restriction(self.pa_preferences.minutes)
        self.__build_user_preferences_restriction(high_evaluated_food_types, high_evaluated_activity_types)

    def __build_healthy_food_restriction(self, has_diabetes: int):

        if has_diabetes == 1:
            print("The user has diabetes. The load glycemic restriction will be applied to the healthy food objective")

        conn = ItemsConnection()
        restrictions = conn.retrieve_healthy_food_restrictions(self.physical_data.is_female, self.physical_data.age)
        protein_size_per_meal = round((restrictions[0] / self.NUMBER_OF_MEALS_PER_DAY), 2)
        carbohydrate_size_per_meal = round((restrictions[1] / self.NUMBER_OF_MEALS_PER_DAY), 2)
        sugar_size_per_meal = round((restrictions[2] / self.NUMBER_OF_MEALS_PER_DAY), 2)
        fibre_size_per_meal = round((restrictions[3] / self.NUMBER_OF_MEALS_PER_DAY), 2)
        fat_size_per_meal = round((restrictions[4] / self.NUMBER_OF_MEALS_PER_DAY), 2)
        saturated_fat_size_per_meal = round((restrictions[5] / self.NUMBER_OF_MEALS_PER_DAY), 2)
        sodium_size_per_meal = round((restrictions[6] / self.NUMBER_OF_MEALS_PER_DAY), 2)

        if self.physical_data.goal == 3:

            if self.physical_data.is_female == 0:

                muscle_gain_protein = protein_size_per_meal * 0.15
                healthy_restriction = HealthyFoodRestriction(muscle_gain_protein, carbohydrate_size_per_meal,
                                                             sugar_size_per_meal, fibre_size_per_meal,
                                                             fat_size_per_meal, saturated_fat_size_per_meal,
                                                             sodium_size_per_meal, has_diabetes)
                self.restrictions.append(healthy_restriction)
            else:

                muscle_gain_protein = protein_size_per_meal * 0.20
                healthy_restriction = HealthyFoodRestriction(muscle_gain_protein, carbohydrate_size_per_meal,
                                                             sugar_size_per_meal, fibre_size_per_meal,
                                                             fat_size_per_meal, saturated_fat_size_per_meal,
                                                             sodium_size_per_meal, has_diabetes)
                self.restrictions.append(healthy_restriction)

        else:

            healthy_restriction = HealthyFoodRestriction(protein_size_per_meal, carbohydrate_size_per_meal,
                                                         sugar_size_per_meal, fibre_size_per_meal, fat_size_per_meal,
                                                         saturated_fat_size_per_meal, sodium_size_per_meal, has_diabetes)
            self.restrictions.append(healthy_restriction)

    def __build_pa_restriction(self, spent_minutes):

        pa_restriction = PARestriction(spent_minutes)
        self.restrictions.append(pa_restriction)

    def __build_diversity_and_consistency_restriction(self):

        diversity_and_consistency_restriction = ConsistencyAndDiversityRestriction()
        self.restrictions.append(diversity_and_consistency_restriction)

    def __build_user_preferences_restriction(self, high_evaluated_food_types, high_evaluated_activity_types):

        if self.physical_data.goal == 3:

            user_preferences_restriction = UserPreferencesRestriction(high_evaluated_food_types,
                                                                      high_evaluated_activity_types, True)
            self.restrictions.append(user_preferences_restriction)

        else:

            user_preferences_restriction = UserPreferencesRestriction(high_evaluated_food_types,
                                                                      high_evaluated_activity_types)
            self.restrictions.append(user_preferences_restriction)

    def __get_high_evaluated_preferences_of_similar_user(self, similar_user_data):

        similar_food_preferences = FoodPreferenceData(similar_user_data[5], similar_user_data[6], similar_user_data[7],
                                                      similar_user_data[8], similar_user_data[9],
                                                      similar_user_data[10], similar_user_data[11],
                                                      similar_user_data[12], similar_user_data[13],
                                                      similar_user_data[14], similar_user_data[15],
                                                      similar_user_data[16], similar_user_data[17],
                                                      similar_user_data[18])
        similar_high_evaluated_food_types = similar_food_preferences.get_higher_evaluated_types()
        similar_pa_preferences = PAPreferenceData(similar_user_data[19], similar_user_data[20],similar_user_data[21],
                                                  similar_user_data[22], similar_user_data[23], similar_user_data[24],
                                                  similar_user_data[25], similar_user_data[26], similar_user_data[27],
                                                  similar_user_data[28])
        similar_high_evaluated_pas = similar_pa_preferences.get_higher_evaluated_activities()
        similar_food = similar_high_evaluated_food_types["first"]
        self.__get_food_indexes(similar_food, "main")
        self.__get_food_indexes(similar_food, "side")
        similar_pas = similar_high_evaluated_pas["first"]
        self.__get_pas_indexes(similar_pas)

    def __get_food_indexes(self, similar_food_types, main_side):

        for similar in similar_food_types:

            location_list = []
            index = 0

            for main_item in self.food_items.get(main_side):

                if main_item.category == similar:
                    location = (main_side, index)
                    location_list.append(location)

                index += 1

            if len(location_list) != 0:

                self.mutation_dictionary[similar] = location_list

    def __get_pas_indexes(self, similar_pas):

        for similar in similar_pas:

            location_list = []
            index = 0

            for pa in self.pa_items:

                if pa.category == similar:
                    location_list.append(index)

                index += 1

            if len(location_list) != 0:
                self.mutation_dictionary[similar] = location_list

    # This method prints on console the recommendations built by the Genetic Algorithms.
    def __print_phenotype(self, phenotype):

        print('  Meal 1, total (grams): %s --- Meal 2, total (grams): %s --- Meal 3, total (grams): %s' % (
            phenotype[0].meal.serving_size, phenotype[1].meal.serving_size, phenotype[2].meal.serving_size))
        print('  Meal 1, calories: %s --- Meal 2, calories: %s --- Meal 3, calories: %s' % (
            phenotype[0].meal.number_of_calories, phenotype[1].meal.number_of_calories,
            phenotype[2].meal.number_of_calories))
        print('  Meal 1, protein: %s --- Meal 2, protein: %s --- Meal 3, protein: %s' % (
            phenotype[0].meal.proteins, phenotype[1].meal.proteins, phenotype[2].meal.proteins))
        print('  Meal 1, carbohydrates: %s --- Meal 2, carbohydrates: %s --- Meal 3, carbohydrates: %s' % (
            phenotype[0].meal.carbohydrates, phenotype[1].meal.carbohydrates, phenotype[2].meal.carbohydrates))
        print('  Meal 1, sugar: %s --- Meal 2, sugar: %s --- Meal 3, sugar: %s' % (
            phenotype[0].meal.sugars, phenotype[1].meal.sugars, phenotype[2].meal.sugars))
        print('  Meal 1, fiber: %s ---  Meal 2, fiber: %s ---  Meal 3, fiber: %s' % (
            phenotype[0].meal.fiber, phenotype[1].meal.fiber, phenotype[2].meal.fiber))
        print('  Meal 1, fat: %s --- Meal 2, fat: %s --- Meal 3, fat: %s' % (
            phenotype[0].meal.fats, phenotype[1].meal.fats, phenotype[2].meal.fats))
        print('  Meal 1, sat fat: %s --- Meal 2, sat fat: %s --- Meal 3, sat fat: %s' % (
            phenotype[0].meal.saturated_fats, phenotype[1].meal.saturated_fats, phenotype[2].meal.saturated_fats))
        print('  Meal 1, sodium: %s --- Meal 2, sodium: %s, --- Meal 3, sodium: %s' % (
            phenotype[0].meal.sodium, phenotype[1].meal.sodium, phenotype[2].meal.sodium))
        print(' ---***---***--- ')
        main0 = phenotype[0].meal.main_food_item
        main1 = phenotype[1].meal.main_food_item
        main2 = phenotype[2].meal.main_food_item
        print('  Meal 1, main: %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s' %
              (main0.name, main0.category, main0.serving_size, main0.number_of_calories, main0.protein, main0.carbohydrate,
               main0.sugar, main0.fiber, main0.fat, main0.saturated_fat, main0.sodium))
        print('  Meal 2, main: %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s' %
              (main1.name, main1.category, main1.serving_size, main1.number_of_calories, main1.protein, main1.carbohydrate,
               main1.sugar, main1.fiber, main1.fat, main1.saturated_fat, main1.sodium))
        print('  Meal 3, main: %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s' %
              (main2.name, main2.category, main2.serving_size, main2.number_of_calories, main2.protein, main2.carbohydrate,
               main2.sugar, main2.fiber, main2.fat, main2.saturated_fat, main2.sodium))
        print(' ////////////// ')
        sides0 = phenotype[0].meal.side_food_items_list
        sides1 = phenotype[1].meal.side_food_items_list
        sides2 = phenotype[2].meal.side_food_items_list
        print('  Meal 1, side 1: %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s' %
              (sides0[0].name, sides0[0].category, sides0[0].serving_size, sides0[0].number_of_calories, sides0[0].protein,
               sides0[0].carbohydrate, sides0[0].sugar, sides0[0].fiber, sides0[0].fat, sides0[0].saturated_fat,
               sides0[0].sodium))
        print('  Meal 2, side 1: %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s' %
              (sides1[0].name, sides1[0].category, sides1[0].serving_size, sides1[0].number_of_calories, sides1[0].protein,
               sides1[0].carbohydrate, sides1[0].sugar, sides1[0].fiber, sides1[0].fat, sides1[0].saturated_fat,
               sides1[0].sodium))
        print('  Meal 3, side 1: %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s' %
              (sides2[0].name, sides2[0].category, sides2[0].serving_size, sides2[0].number_of_calories, sides2[0].protein,
               sides2[0].carbohydrate, sides2[0].sugar, sides2[0].fiber, sides2[0].fat, sides2[0].saturated_fat,
               sides2[0].sodium))
        print(' *---* ')
        print('  Meal 1, side 2: %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s' %
              (sides0[1].name, sides0[1].category, sides0[1].serving_size, sides0[1].number_of_calories, sides0[1].protein,
               sides0[1].carbohydrate, sides0[1].sugar, sides0[1].fiber, sides0[1].fat, sides0[1].saturated_fat,
               sides0[1].sodium))
        print('  Meal 2, side 2: %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s' %
              (sides1[1].name, sides1[1].category, sides1[1].serving_size, sides1[1].number_of_calories, sides1[1].protein,
               sides1[1].carbohydrate, sides1[1].sugar, sides1[1].fiber, sides1[1].fat, sides1[1].saturated_fat,
               sides1[1].sodium))
        print('  Meal 3, side 2: %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s' %
              (sides2[1].name, sides2[1].category, sides2[1].serving_size, sides2[1].number_of_calories, sides2[1].protein,
               sides2[1].carbohydrate, sides2[1].sugar, sides2[1].fiber, sides2[1].fat, sides2[1].saturated_fat,
               sides2[1].sodium))
        print(' *---* ')
        print('  Meal 1, side 3: %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s' %
              (sides0[2].name, sides0[2].category, sides0[2].serving_size, sides0[2].number_of_calories, sides0[2].protein,
               sides0[2].carbohydrate, sides0[2].sugar, sides0[2].fiber, sides0[2].fat, sides0[2].saturated_fat,
               sides0[2].sodium))
        print('  Meal 2, side 3: %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s' %
              (sides1[2].name, sides1[2].category, sides1[2].serving_size, sides1[2].number_of_calories, sides1[2].protein,
               sides1[2].carbohydrate, sides1[2].sugar, sides1[2].fiber, sides1[2].fat, sides1[2].saturated_fat,
               sides1[2].sodium))
        print('  Meal 3, side 3: %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s' %
              (sides2[2].name, sides2[2].category, sides2[2].serving_size, sides2[2].number_of_calories, sides2[2].protein,
               sides2[2].carbohydrate, sides2[2].sugar, sides2[2].fiber, sides2[2].fat, sides2[2].saturated_fat,
               sides2[2].sodium))
        print(' ---***---***--- ')
        ex0 = phenotype[0].pa
        ex1 = phenotype[1].pa
        ex2 = phenotype[2].pa
        print('PA 1: %s, %s, %s, %s, %s, %s, %s' % (
            ex0.name, ex0.category, ex0.indoors, ex0.outdoors, ex0.intensity, ex0.met, ex0.duration))
        print('PA 2: %s, %s, %s, %s, %s, %s, %s' % (
            ex1.name, ex1.category, ex1.indoors, ex1.outdoors, ex1.intensity, ex1.met, ex1.duration))
        print('PA 3: %s, %s, %s, %s, %s, %s, %s' % (
            ex2.name, ex2.category, ex2.indoors, ex2.outdoors, ex2.intensity, ex2.met, ex2.duration))
        
        print("Meal 1:")
        phenotype[0].meal.print_meal()
        print("Meal 2:")
        phenotype[1].meal.print_meal()
        print("Meal 3:")
        phenotype[2].meal.print_meal()

