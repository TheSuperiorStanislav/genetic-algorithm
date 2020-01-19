import random

from cached_property import cached_property


class Individual:
    length = 32

    def __init__(self, value, mutate_chance=0.05):
        self.mutate_chance = mutate_chance
        str_value = str(float(value)).split('.')

        self.int_part = int(str_value[0])
        self.sign = False
        if self.int_part < 0:
            self.sign = True
            self.int_part *= -1

        try:
            self.float_part = int(str_value[-1])
        except ValueError:
            self.int_part = 0
            self.float_part = 0

    def __repr__(self):
        return str(self.value)

    @cached_property
    def int_chromosome(self):
        return self.to_chromosome(self.int_part)

    @cached_property
    def float_chromosome(self):
        return self.to_chromosome(self.float_part)

    def to_chromosome(self, num: int):
        """Convert part to chromosome."""
        chromosome = format(num, 'b')
        chromosome = '0' * (self.length - len(chromosome)) + chromosome
        return chromosome

    @cached_property
    def value(self):
        """Get value of individual."""
        value = float(f'{self.int_part}.{self.float_part}')
        if self.sign:
            value *= -1
        return value

    def mutate(self):
        """Perform mutation."""
        is_to_mutate = random.random() < self.mutate_chance
        if not is_to_mutate:
            return
        self.mutate_int_part()
        self.mutate_float_part()

    def mutate_int_part(self):
        """Mutate int part."""
        self.int_part = self.mutate_part(self.int_chromosome)

    def mutate_float_part(self):
        """Mutate float part."""
        self.float_part = self.mutate_part(self.float_chromosome)

    @staticmethod
    def mutate_part(value):
        """Mutate chromosome part."""
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

    @cached_property
    def value(self):
        """Get value of function with group values."""
        return self.func(
            *(individual.value for individual in self.individuals)
        )

    @cached_property
    def fitness(self):
        """Calculate fitness."""
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
        self.individual_groups = list(individual_groups)
        self.lower_border = lower_border
        self.upper_border = upper_border
        self.mutate_chance = mutate_chance

    def __getitem__(self, item):
        return self.individual_groups[item]

    @cached_property
    def sorted_by_fitness(self):
        """Sort by fitness function from worst ot best."""
        return sorted(self, reverse=True)

    @cached_property
    def best(self) -> IndividualGroup:
        """Get best group in population."""
        return self.sorted_by_fitness[-1]

    @cached_property
    def worst(self) -> IndividualGroup:
        """Get worst group in population."""
        return self.sorted_by_fitness[0]

    @property
    def selection(self):
        ranked = self.sorted_by_fitness
        selected = [
            group
            for index, group in enumerate(ranked, start=1)
            if index / len(ranked) >= random.random()
        ]
        return selected

    def mate(self, *groups) -> IndividualGroup:
        """Mate individual groups"""
        individuals = (
            self.mate_individual(*values)
            for values in zip(*groups)
        )
        return IndividualGroup(individuals=individuals, func=self.func)

    def mate_individual(self, *individuals) -> Individual:
        """Mate individuals."""
        int_value = self.mate_chromosomes('int_chromosome', *individuals)
        float_value = self.mate_chromosomes('float_chromosome', *individuals)

        value = float(f'{int_value}.{float_value}')
        sign = random.choice([
            individual.sign
            for individual in individuals
        ])
        if sign:
            value *= -1

        individual = Individual(value=value)
        individual.mutate()

        if individual.value > self.upper_border:
            individual = Individual(value=self.upper_border)
        elif individual.value < self.lower_border:
            individual = Individual(value=self.lower_border)

        return individual

    @staticmethod
    def mate_chromosomes(part_name: str, *individuals):
        """Mate chromosomes of individuals."""
        chromosomes = (
            getattr(individual, part_name)
            for individual in individuals
        )
        chromosome = (
            random.choice(nums)
            for nums in zip(*chromosomes)
        )
        return int(''.join(chromosome), 2)

    def crossover(self):
        """Perform crossover."""
        selected = self.selection
        new_generation = (
            self.mate(*random.choices(selected, k=2))
            for _ in range(len(self.individual_groups))
        )

        return Population(
            individual_groups=new_generation,
            func=self.func,
            lower_border=self.lower_border,
            upper_border=self.upper_border,
            mutate_chance=self.mutate_chance,
        )
