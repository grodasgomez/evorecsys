import time
import csv
import os

from src.geneticalgorithm.GeneticAlgorithmMOEAD import GeneticAlgorithmMOEAD

user_data = [1.0, 25.0, 174.0, 91.4, 0.0, 4.0, 4.0, 4.0, 4.0, 0.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 1.0, 4.0, 5.0, 80.0, 0.0, 0.0, 5.0, 5.0, 4.0, 5.0, 4.0, 0.0, 0.0]

similar_user_data = [1.0, 55.0, 170.0, 100.0, 2.0, 5.0, 3.0, 5.0, 1.0, 0.0, 5.0, 4.0, 5.0, 4.0, 4.0, 3.0, 5.0, 0.0, 5.0, 3.0, 60.0, 2.0, 1.0, 5.0, 4.0, 3.0, 4.0, 5.0, 0.0, 0.0]

ga = GeneticAlgorithmMOEAD(user_data, similar_user_data)
iterations = 10
aptitudes = []
times = []

# Create and write to CSV file in performance_tests directory
csv_path = os.path.join('performance_tests', 'performance_moead.csv')
with open(csv_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Iteration', 'Aptitude', 'Execution Time (seconds)'])
    
    for i in range(iterations):
        start_time = time.time()
        best_individual = ga.execute_genetic_algorithm()
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Time taken: {execution_time} seconds")
        
        aptitudes.append(best_individual.aptitude)
        times.append(execution_time)
        
        # Write each iteration's data to CSV
        writer.writerow([i + 1, best_individual.aptitude, execution_time])

print(f"Average aptitude: {sum(aptitudes) / iterations}")
print(f"Average time taken: {sum(times) / iterations} seconds")


