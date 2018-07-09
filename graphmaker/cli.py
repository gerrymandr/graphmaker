import click
from graphmaker.constants import state_abbrevation_to_fips
from graphmaker.match import match as _match


@click.group()
def cli():
    pass


def resolve_fips(state):
    if state in state_abbrevation_to_fips:
        return state_abbrevation_to_fips[state]
    elif state.upper() in state_abbrevation_to_fips:
        return state_abbrevation_to_fips[state.uppder()]
    return state


@click.option('--part', default='CD')
@click.option('--unit', default='VTD')
@click.argument('state')
@click.command()
def match(state, unit, part):
    fips = resolve_fips(state)

    _match(fips, unit, part)


cli.add_command(match)
