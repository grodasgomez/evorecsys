from src.geneticalgorithm.Individual import Individual
import numpy as np



class NDNode:
    """
    This class represents a node in the ND-Tree.
    It has the following attributes:
    - solutions: list of solutions in the node
    - children: list of children nodes
    - parent: parent node
    - ideal_point: ideal point of the node. It is the point with the best values for each objective.
    - nadir_point: nadir point of the node. It is the point with the worst values for each objective.
    """

    def __init__(self, maximum_size: int, minimum_children_size: int):
        self.solutions: list[Individual] = []
        self.children: list[NDNode] = []
        self.parent: NDNode | None = None
        self.ideal_point: list[float] = []
        self.nadir_point: list[float] = []
        self.maximum_size = maximum_size
        self.minimum_children_size = minimum_children_size

    def _is_leaf(self):
        return len(self.children) == 0
    
    def update(self, new_solution: Individual):
        new_point = new_solution.aptitudes

        # if self._is_leaf() and self.solutions == []:
        #     return True

        # If the new solution is dominated by the nadir point, so it is dominated
        # by all solutions in the node. Therefore it is descarted.
        if self._dominates(self.nadir_point, new_point):
            return False
        
        # If the new solution dominates the ideal point, so it dominates all
        # solutions in the node. Therefore the node must be removed.
        elif self._dominates(new_point, self.ideal_point):
            self.remove_self()
        
        elif self._dominates(self.ideal_point, new_point) or self._dominates(new_point, self.nadir_point):
            if self._is_leaf():
                for solution in self.solutions:
                    if solution.dominates(new_solution):
                        return False
                    elif new_solution.dominates(solution):
                        self.solutions.remove(solution)
            else:
                for child in self.children:
                    if not child.update(new_solution):
                        return False
                    else:
                        if child.solutions == [] and child.children == []:
                            child.remove_self()

        return True
        

    def insert(self, new_solution: Individual):
        """
        Insert the new solution to the closest leaf.
        To find a proper leaf we start from the root and always select a child with closest distance to y.
        As a distance measure we use the Euclidean distance to the middle point, i.e. a point lying in the middle of line segment connecting approximate ideal and approximate nadir points.
        """
        if self._is_leaf():
            self.solutions.append(new_solution)
            self.update_ideal_nadir_points(new_solution.aptitudes)
            if len(self.solutions) > self.maximum_size:
                self.split()
        else:
            closest_child = None
            closest_distance = float('inf')
            new_point = new_solution.aptitudes
            for child in self.children:
                child_middle = [(child.ideal_point[i] + child.nadir_point[i]) / 2 for i in range(len(child.ideal_point))]
                distance = np.linalg.norm(np.array(new_point) - np.array(child_middle))
                if distance < closest_distance:
                    closest_distance = distance
                    closest_child = child
            closest_child.insert(new_solution)
    
    def update_ideal_nadir_points(self, new_point: list[float]):
        """
        When a new solution is inserted in the node, the ideal and nadir points
        of the node must be updated.
        If the ideal point or the nadir point of the node is updated, the ideal and nadir points of the parent
        must be updated too.
        """
        has_changed = False
        if(len(self.solutions) == 1):
            self.ideal_point = new_point
            self.nadir_point = new_point
            has_changed = True
        else:
            for i in range(len(new_point)):
                if new_point[i] < self.ideal_point[i]:
                    self.ideal_point[i] = new_point[i]
                    has_changed = True
                if new_point[i] > self.nadir_point[i]:
                    self.nadir_point[i] = new_point[i]
                    has_changed = True
        if has_changed and self.parent is not None:
            self.parent.update_ideal_nadir_points(new_point)
            
    def get_solutions(self):
        if self._is_leaf():
            return self.solutions
        else:
            solutions = []
            for child in self.children:
                solutions.extend(child.get_solutions())
            return solutions
    

    def remove_self(self):
        if self.parent is not None:
            self.parent.children.remove(self)
        else:
            self.solutions = []
            self.children = []
            self.ideal_point = []
            self.nadir_point = []


    def split(self):

        # Step 1: Find the point with the highest average Euclidean distance to all others
        def avg_euclidean_dist(point, others):
            if not others:
                return 0
            return np.mean([np.linalg.norm(np.array(point) - np.array(other.aptitudes)) for other in others])

        # Step 2: Create the first child with the most isolated solution
        z = max(self.solutions, key=lambda s: avg_euclidean_dist(s.aptitudes, [x for x in self.solutions if x != s]))
        children = []
        child = NDNode(self.maximum_size, self.minimum_children_size)
        child.solutions = [z]
        child.parent = self
        child.update_ideal_nadir_points(z.aptitudes)
        children.append(child)
        remaining = [s for s in self.solutions if s != z]

        # Step 3: Create the rest of the children
        while len(children) < self.minimum_children_size:
            # For each remaining solution, compute its average distance to all points in all children
            def avg_dist_to_children(sol):
                all_child_points = [indiv for c in children for indiv in c.solutions]
                return avg_euclidean_dist(sol.aptitudes, all_child_points)
            z = max(remaining, key=avg_dist_to_children)
            
            child = NDNode(self.maximum_size, self.minimum_children_size)
            child.solutions = [z]
            child.parent = self
            child.update_ideal_nadir_points(z.aptitudes)
            
            children.append(child)
            remaining.remove(z)

        # Step 4: Distribute the rest of the solutions
        while len(remaining) > 0:
            z = remaining[0]
            # Find the child whose solution is closest to z
            def get_distance_to_child(child):
                return avg_euclidean_dist(z.aptitudes, child.solutions)
            closest_child = min(children, key=get_distance_to_child)
            closest_child.solutions.append(z)
            closest_child.update_ideal_nadir_points(z.aptitudes)
            remaining.remove(z)

        # Step 5: Update children and clear this node's solutions
        self.children = children
        self.solutions = []

    
    def _dominates(self, point1: list[float], point2: list[float]):
        """Check if point1 dominates point2"""

        # Check if point1 is better or equal in every objective
        for i in range(len(point1)):
            isBetterOrEqual = point1[i] <= point2[i]
            if not isBetterOrEqual:
                return False

        #Check if point1 is better at least in one objective
        for i in range(len(point1)):
            isBetter = point1[i] < point2[i]
            if isBetter:
                return True
        return False



class NDTree:
    def __init__(self, maximum_size: int, minimum_children_size: int):
        self.root: NDNode | None = None
        self.maximum_size = maximum_size
        self.minimum_children_size = minimum_children_size
        
    def update(self, new_solution: Individual):

        root = self.root
        # If node is empty, insert here
        if root is None:
            self.root = NDNode(self.maximum_size, self.minimum_children_size)
            self.root.insert(new_solution)
            return True
        else:
            if root.update(new_solution):
                root.insert(new_solution)

    def get_solutions(self):
        return self.root.get_solutions()
    
    def check_if_all_solutions_are_non_dominated(self):
        solutions = self.get_solutions()
        has_dominated_solution = False
        for solution in solutions:
            for other_solution in solutions:
                if solution.dominates(other_solution) and solution != other_solution:
                    has_dominated_solution = True
        return not has_dominated_solution