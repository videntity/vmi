from django.core.management.base import BaseCommand


def create_sample_organizations():
    # Pass - removing this command because is
    # was causing errors and can be done manually.
    # problematic and unnecessary.
    return []


class Command(BaseCommand):

    help = 'Create sample organizations.'

    def handle(self, *args, **options):
        orgs = create_sample_organizations()
        print("Organizations %s created if they did not already exist." % (orgs))
