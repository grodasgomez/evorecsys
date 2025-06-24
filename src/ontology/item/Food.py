# All necessary imports from other files.
from src.ontology.item.Item import Item


# This class instant represents a food item. It contains nutritional data, serving size, if it is vegan/vegetarian,
# if it is main or side, etc. It extends from the Item class.
class Food(Item):

    # Constructor
    def __init__(self, name, category, main, breakfast, lunch, dinner, vegetarian, vegan, size, cal, prot, carbo, sug,
                 fib, fat, sat_fat, sod, glycemic_index):

        super().__init__(name, category)

        self.is_main = main
        self.is_breakfast = breakfast
        self.is_lunch = lunch
        self.is_dinner = dinner
        self.is_vegetarian = vegetarian
        self.is_vegan = vegan
        self.serving_size = size
        self.number_of_calories = cal
        self.protein = prot
        self.carbohydrate = carbo
        self.sugar = sug
        self.fiber = fib
        self.fat = fat
        self.saturated_fat = sat_fat
        self.sodium = sod
        self.glycemic_index = glycemic_index

    def print_food(self):
        print(f"Name: {self.name}")
        print(f"Category: {self.category}")
        print(f"Is main: {self.is_main}")
        print(f"Is breakfast: {self.is_breakfast}")
        print(f"Is lunch: {self.is_lunch}")
        print(f"Is dinner: {self.is_dinner}")
        print(f"Is vegetarian: {self.is_vegetarian}")
        print(f"Is vegan: {self.is_vegan}")
        print(f"Serving size: {self.serving_size}")
        print(f"Number of calories: {self.number_of_calories}")
        print(f"Protein: {self.protein}")
        print(f"Carbohydrate: {self.carbohydrate}")
        print(f"Sugar: {self.sugar}")
        print(f"Fiber: {self.fiber}")
        print(f"Fat: {self.fat}")
        print(f"Saturated fat: {self.saturated_fat}")
        print(f"Sodium: {self.sodium}")

    def get_glycemic_load(self):
        return self.glycemic_index * self.carbohydrate / 100
