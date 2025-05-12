import numpy as np
from src.geneticalgorithm.Population import Population
from src.geneticalgorithm.Individual import Individual

class MOEAD:
    def __init__(self, population_size, number_of_objectives, neighborhood_size=20):
        self.population_size = population_size
        self.number_of_objectives = number_of_objectives
        self.neighborhood_size = neighborhood_size
        self.weight_vectors = []
        self.neighborhoods = []
        self.reference_point = None
        self.population = None
        
    def initialize_weight_vectors(self):
        # Generate weight vectors using simplex lattice design
        H = self.population_size - 1
        for i in range(self.population_size):
            w = np.zeros(self.number_of_objectives)
            w[0] = i / H
            w[1] = (H - i) / H
            self.weight_vectors.append(w)
            
    def initialize_neighborhoods(self):
        # Calculate Euclidean distances between weight vectors
        distances = np.zeros((self.population_size, self.population_size))
        for i in range(self.population_size):
            for j in range(self.population_size):
                distances[i][j] = np.linalg.norm(self.weight_vectors[i] - self.weight_vectors[j])
                
        # Sort distances and get neighborhoods
        for i in range(self.population_size):
            sorted_indices = np.argsort(distances[i])
            # Convert numpy array to list and store neighborhood indices
            self.neighborhoods.append(sorted_indices[1:self.neighborhood_size + 1].tolist())
            
    def update_reference_point(self, population):
        # Update reference point based on current population
        if self.reference_point is None:
            self.reference_point = np.zeros(self.number_of_objectives)
            for i in range(self.number_of_objectives):
                self.reference_point[i] = min(ind.aptitudes[i] for ind in population.initial_population)
        else:
            for i in range(self.number_of_objectives):
                self.reference_point[i] = min(self.reference_point[i], 
                                           min(ind.aptitudes[i] for ind in population.initial_population))
                
    def tchebycheff_scalarization(self, individual, weight_vector):
        # Calculate Tchebycheff scalarization
        max_value = -np.inf
        for i in range(self.number_of_objectives):
            value = weight_vector[i] * abs(individual.aptitudes[i] - self.reference_point[i])
            if value > max_value:
                max_value = value
        return max_value