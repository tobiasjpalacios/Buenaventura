from django.apps import apps
from django.core.management.commands.makemigrations import Command as CoreMakeMigrationsCommand

from BAapp.utils.fulltext import SearchManager 


class Command(CoreMakeMigrationsCommand):
    def handle(self, *app_labels, **options):
        options['empty'] = True
        options['verbosity'] = 1
        options['interactive'] = True
        options['dry_run'] = False
        options['merge'] = False
        options['check_changes'] = False
        super(Command, self).handle(*app_labels, **options)

    def write_migration_files(self, changes):
        search = changes.keys()
        for app in search:
            models = apps.get_app_config(app).get_models()
            for model in models:
                if isinstance(model._default_manager, SearchManager):
                    op = model._default_manager.get_operation()
                    if (op):
                        changes[app][0].operations.append(op)
        super(Command, self).write_migration_files(changes)