from django.core.management.base import BaseCommand, CommandError
from main.views import check_deadman_switch

class Command(BaseCommand):
    help = 'Checks the timers for each deadman switch'

    def handle(self, *args, **options):
        check_deadman_switch()
