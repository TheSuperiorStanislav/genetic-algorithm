import random
import sys


class Individual:
    def __init__(self, value, mutate_chance=0.90):
        self.mutate_chance = mutate_chance
        str_value = str(float(value)).split('.')
        self.int_part = int(str_value[0])
        try:
            self.float_part = int(str_value[-1])
        except ValueError:
            self.int_part = 0
            self.float_part = 0

    def __repr__(self):
        return str(self.value)

    @property
    def int_chromosome(self):
        return format(self.int_part, 'b')

    @property
    def float_chromosome(self):
        return format(self.float_part, 'b')

    @property
    def value(self):
        return float(f'{self.int_part}.{self.float_part}')

    def mutate(self):
        is_to_mutate = random.random() < self.mutate_chance
        if not is_to_mutate:
            return
        self.mutate_int_part()
        self.mutate_float_part()

    def mutate_int_part(self):
        self.int_part = self.mutate_part(self.int_chromosome)

    def mutate_float_part(self):
        self.float_part = self.mutate_part(self.float_chromosome)

    @staticmethod
    def mutate_part(value):
        index_to_mutate = random.randint(0, len(value) - 1)
        mutate_value = list(value)
        if mutate_value[index_to_mutate] == '1':
            mutate_value[index_to_mutate] = '0'
        else:
            mutate_value[index_to_mutate] = '1'
        return int(''.join(mutate_value), 2)


class IndividualGroup:
    def __init__(self, individuals, func):
        self.individuals = list(individuals)
        self.func = func

    def __repr__(self):
        return f'Value {self.value} Group: {self.individuals}'

    def __getitem__(self, item):
        return self.individuals[item]

    def __eq__(self, other):
        return self.fitness == other.fitness

    def __lt__(self, other):
        return self.fitness < other.fitness

    def __le__(self, other):
        return self.fitness <= other.fitness

    @property
    def value(self):
        return self.func(
            *(individual.value for individual in self.individuals)
        )

    @property
    def fitness(self):
        return self.value


class Population:
    def __init__(
        self,
        individual_groups,
        func,
        lower_border,
        upper_border,
        mutate_chance=0.90,
    ):
        self.func = func
        self.individual_groups = [
            individual_group for individual_group in individual_groups
        ]
        self.lower_border = lower_border
        self.upper_border = upper_border
        self.mutate_chance = mutate_chance

    def __getitem__(self, item):
        return self.individual_groups[item]

    @property
    def best(self) -> IndividualGroup:
        return sorted(self)[0]

    @property
    def worst(self) -> IndividualGroup:
        return sorted(self)[-1]

    @property
    def selection(self):
        ranked = sorted(self, reverse=True)
        selected = [
            group
            for index, group in enumerate(ranked, start=1)
            if index / len(ranked) >= random.random()
        ]
        return selected

    def mate(
        self, group1: IndividualGroup, group2: IndividualGroup
    ) -> IndividualGroup:
        individuals = []
        for values in zip(group1, group2):
            individuals.append(self.mate_individual(*values))
        return IndividualGroup(individuals=individuals, func=self.func)

    def mate_individual(
        self, value1: Individual, value2: Individual
    ) -> Individual:
        int_value = []
        for nums in self.zip_chromosome(
            value1.int_chromosome, value2.int_chromosome
        ):
            int_value.append(random.choice(nums))
        int_value = int(''.join(int_value), 2)

        float_value = []
        for nums in self.zip_chromosome(
            value1.float_chromosome, value2.float_chromosome
        ):
            float_value.append(random.choice(nums))
        float_value = int(''.join(float_value), 2)

        individual = Individual(value=float(f'{int_value}.{float_value}'))
        individual.mutate()

        if individual.value > self.upper_border:
            individual = Individual(value=self.upper_border)
        elif individual.value < self.lower_border:
            individual = Individual(value=self.lower_border)

        return individual

    @staticmethod
    def zip_chromosome(chromosome1, chromosome2):
        minus1 = '-' in chromosome1
        minus2 = '-' in chromosome2

        len1 = len(chromosome1)
        len2 = len(chromosome2)

        chromosome1 = chromosome1.replace('-', '')
        chromosome2 = chromosome2.replace('-', '')

        if len1 > len2:
            chromosome2 = '0' * (len1 - len2) + chromosome2
        elif len1 < len2:
            chromosome1 = '0' * (len2 - len1) + chromosome1

        if minus1:
            chromosome1 = '-' + chromosome1
        if minus2:
            chromosome2 = '-' + chromosome2
        return zip(chromosome1, chromosome2)

    def crossover(self):
        selected = self.selection
        new_generation = []
        for _ in range(len(self.individual_groups)):
            new_generation.append(self.mate(*random.choices(selected, k=2)))
        return Population(
            individual_groups=new_generation,
            func=self.func,
            lower_border=self.lower_border,
            upper_border=self.upper_border,
            mutate_chance=self.mutate_chance,
        )
