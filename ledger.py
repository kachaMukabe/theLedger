import click
import os
import datetime
import pandas as pd


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Track your money every month"""
    ctx.obj = Ledger()
    if ctx.invoked_subcommand is None:
        click.echo(ctx.obj.to_string())


@cli.command()
@click.option('-c', '--category', default="Income", help="Category of the income.")
@click.argument('amount', type=click.FLOAT)
@click.pass_context
def deposit(ctx, amount, category):
    """Record income amount."""
    description = click.prompt('Enter description', default="None")
    ctx.obj.deposit(amount, description, category)
    click.echo("Successfully deposited K{} into {}.".format(amount, category))


@cli.command()
@click.option('-c', '--category', default="Expense", help="Category of the expense.")
@click.argument('amount', type=click.FLOAT)
@click.pass_context
def withdraw(ctx, amount, category):
    """Record expense amount"""
    description = click.prompt('Enter description', default="None")
    ctx.obj.withdraw(amount, description, category)
    click.echo("Withdrawn K{} for {}.".format(amount, category))


@cli.command()
@click.argument('ledger_id', type=click.INT)
@click.pass_context
def edit(ctx, ledger_id):
    """Edit an entry using it's ID."""
    entry = ctx.obj.select_entry(ledger_id)
    amount = 0
    click.echo(entry.date)
    if entry.deposit == 0:
        amount = click.prompt('Withdrawal', default=entry.withdrawal, type=float)
    elif entry.withdrawal == 0:
        amount = click.prompt('Deposit', default=entry.deposit, type=float)
    description = click.prompt('Description', default=entry.description)
    category = click.prompt('Category', default=entry["category"])
    ctx.obj.edit_entry(ledger_id, amount, description, category)
    click.echo("\nSuccessfully edited")
    click.echo(ctx.obj.select_entry(ledger_id))


@cli.command()
@click.argument('ledger_id', type=click.INT)
@click.confirmation_option(prompt='Are you sure you want to delete this entry')
@click.pass_context
def delete(ctx, ledger_id):
    """Delete an entry using it's ID"""
    ctx.obj.delete_entry(ledger_id)
    click.echo("Deleted entry {}".format(ledger_id))


@cli.command()
@click.option('-v', '--verbose', is_flag=True, help="Get more detailed transaction info")
@click.pass_context
def display(ctx, verbose):
    """Display the transactions and summary."""
    click.echo(ctx.obj.to_string())
    click.echo(ctx.obj.display(verbose))


class Ledger:

    def __init__(self):
        if os.path.exists('ledger.csv'):
            self.ledger = pd.read_csv('ledger.csv')
        else:
            self.ledger = pd.DataFrame(columns=['date', 'description', 'deposit', 'withdrawal', 'category'])

            self.save()

    def deposit(self, amount, description, category):
        # Put dict in a list so that the value is not a scaler value(Read on this)
        df = pd.DataFrame([{
            'date': datetime.datetime.now().strftime('%d-%m-%y'),
            'description': description,
            'deposit': amount,
            'withdrawal': 0,
            'category': category,

        }])
        self.ledger = self.ledger.append(df, ignore_index=True)
        self.save()

    def withdraw(self, amount, description, category):

        df = pd.DataFrame([{
            'date': datetime.datetime.now().strftime('%d-%m-%y'),
            'description': description,
            'deposit': 0,
            'withdrawal': amount,
            'category': category,
        }])
        self.ledger = self.ledger.append(df, ignore_index=True, sort=False)
        self.save()

    def select_entry(self, ledger_id):
        return self.ledger.iloc[ledger_id]

    def edit_entry(self, ledger_id, amount, description, category):
        if not self.ledger.empty:
            if self.ledger.iloc[ledger_id]['deposit'] == 0:
                self.ledger.at[ledger_id, 'withdrawal'] = amount
            elif self.ledger.iloc[ledger_id]['withdrawal'] == 0:
                self.ledger.at[ledger_id, 'deposit'] = amount
            self.ledger.at[ledger_id, 'description'] = description
            self.ledger.at[ledger_id, 'category'] = category
            self.save()

    def delete_entry(self, ledger_id):
        if not self.ledger.empty:
            self.ledger = self.ledger.drop(self.ledger.index[int(ledger_id)])
            self.save()

    def get_total_income(self):
        return self.ledger['deposit'].sum()

    def get_total_expense(self):
        return self.ledger['withdrawal'].sum()

    def to_string(self):
        total = self.get_total_income() - self.get_total_expense()

        return 'Balance: K{0} \nIncomes: K{1}\tExpenses: K{2}'.format(total, self.get_total_income(), self.get_total_expense())

    def display(self, verbose):
        if verbose:
            return self.ledger
        return self.ledger.tail()

    def save(self):
        # Add index=False to stop dataframe from creating an unnamed column when saving to csv
        self.ledger.to_csv('ledger.csv', index=False)
