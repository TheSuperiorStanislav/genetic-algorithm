import random

import models
import test_funcs


def generate_init_population(
    func, size, group_size, lower_border, upper_border, mutate_chance
) -> models.Population:
    """Generate first population."""
    return models.Population(
        individual_groups=(
            generate_group(
                group_size=group_size,
                lower_border=lower_border,
                upper_border=upper_border,
                func=func,
            )
            for _ in range(size)
        ),
        func=func,
        lower_border=lower_border,
        upper_border=upper_border,
        mutate_chance=mutate_chance,
    )


def generate_group(
    group_size, lower_border, upper_border, func,
) -> models.IndividualGroup:
    """Generate group of individuals."""
    return models.IndividualGroup(
        individuals=(
            generate_individual(
                lower_border=lower_border, upper_border=upper_border
            )
            for _ in range(group_size)
        ),
        func=func,
    )


def generate_individual(lower_border, upper_border) -> models.Individual:
    """Generate individual."""
    return models.Individual(
        value=random.uniform(a=lower_border, b=upper_border)
    )


def do_the_thing(
    step_limit,
    duplicate_limit,
    size,
    group_size,
    lower_border,
    upper_border,
    func,
    mutate_chance,
):
    population = generate_init_population(
        size=size,
        group_size=group_size,
        lower_border=lower_border,
        upper_border=upper_border,
        func=func,
        mutate_chance=mutate_chance,
    )
    best = list()
    for population_num in range(step_limit):
        print(
            f'Population {population_num}\n'
            f'Best {population.best}\n'
            f'Worst {population.worst}'
        )
        best_in_population = population.best
        best.append(best_in_population)
        if best.count(best_in_population) >= duplicate_limit:
            print('Reached duplication limit')
            break
        population = population.crossover()

    print(f'Results: \n' f'Best {sorted(best)[0]}')


if __name__ == '__main__':
    do_the_thing(
        step_limit=100,
        duplicate_limit=10,
        size=1000,
        group_size=2,
        lower_border=-500,
        upper_border=500,
        func=test_funcs.test_func_6,
        mutate_chance=0.50,
    )
