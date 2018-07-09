import click
from graphmaker.constants import state_abbrevation_to_fips
from graphmaker.match import match as _match


@click.group()
def cli():
    pass


@click.option('--part', default='CD')
@click.option('--unit', default='VTD')
@click.argument('state')
@click.command()
def match(state, unit, part):
    if state in state_abbrevation_to_fips:
        fips = state_abbrevation_to_fips[state]
    else:
        fips = state

    _match(fips, unit, part)
