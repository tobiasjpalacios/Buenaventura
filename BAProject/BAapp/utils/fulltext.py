# -*- coding: utf-8 -*-
from django.core import exceptions
from django.db import models, connection
from django.db import migrations

__author__ = 'confirm IT solutions'
__email__ = 'contactus@confirm.ch'
__version__ = '0.2.0'


class SearchQuerySet(models.query.QuerySet):
    '''
    QuerySet which supports MySQL and MariaDB full-text search.
    '''

    def __init__(self, fields=None, **kwargs):
        super(SearchQuerySet, self).__init__(**kwargs)
        self.search_fields = fields

    def get_query_set(self, query, columns, mode):
        '''
        Returns the query set for the columns and search mode.
        '''
        # Create the WHERE MATCH() ... AGAINST() expression.
        fulltext_columns = ', '.join(columns)
        where_expression = ('MATCH({}) AGAINST("%s" {})'.format(fulltext_columns, mode))

        # Get query set via extra() method.
        return self.extra(where=[where_expression], params=[query])

    def search(self, query, fields=None, mode=None):
        '''
        Runs a fulltext search against the fields defined in the method's
        kwargs. If no fields are defined in the method call, then the fields
        defined in the constructor's kwargs will be used.
        Just define a query (the search term) and a fulltext search will be
        executed. In case mode is set to None, the method will automatically
        switch to "BOOLEAN" in case any boolean operators were found.
        Of course you can set the search mode to any type you want, e.g.
        "NATURAL LANGUAGE".
        '''
        #
        # Get all requried attributes and initialize our empty sets.
        #

        meta       = self.model._meta
        quote_name = connection.ops.quote_name
        seperator  = models.constants.LOOKUP_SEP

        columns        = set()
        related_fields = set()

        #
        # Loop through the defined search fields to build a list of all
        # searchable columns. We need to differ between simple fields and
        # fields with a related model, because the meta data of those fields
        # are stored in the related model itself.
        #

        fields = self.search_fields if not fields else fields

        for field in fields:

            # Handling fields with a related model.
            if seperator in field:
                field, rfield = field.split(seperator)
                rmodel        = meta.get_field(field).related_model
                rmeta         = rmodel._meta
                table         = rmeta.db_table
                column        = rmeta.get_field(rfield).column
                related_fields.add(field)

            # Handle fields without a related model.
            else:
                table  = meta.db_table
                column = meta.get_field(field).column

            # Add field with `table`.`column` style to columns set.
            columns.add('{}.{}'.format(quote_name(table), quote_name(column)))

        #
        # We now have all the required informations to build the query with the
        # fulltext "MATCH(…) AGAINST(…)" WHERE statement. However, we also need
        # to conside the search mode. Thus, if the mode argument is set to
        # None, we need to inspect the search query and enable the BOOLEAN mode
        # in case any boolean operators were found. This is also a workaround
        # for using at-signs (@) in search queries, because we don't enable the
        # boolean mode in case no other operator was found.
        #

        # Set boolean mode if mode argument is set to None.
        if mode is None and any(x in query for x in '+-><()*"'):
            mode = 'BOOLEAN'

        # Convert the mode into a valid "IN … MODE" or empty string.
        if mode is None:
            mode = ''
        else:
            mode = 'IN {} MODE'.format(mode)

        # Get the query set.
        query_set = self.get_query_set(query, columns, mode)

        #
        # If related fields were involved we've to select them as well.
        #

        if related_fields:
            query_set = query_set.select_related(','.join(related_fields))

        # Return query_set.
        return query_set

    def count(self):
        '''
        Returns the count database records.
        '''
        #
        # We need to overwrite the default count() method. Unfortunately
        # Django's internal count() method will clone the query object and then
        # re-create the SQL query based on the default table and WHERE clause,
        # but without the related tables. So if related tables are included in
        # the query (i.e. JOINs), then Django will forget about the JOINs and
        # the MATCH() of the related fields will fail with an "unknown column"
        # error.
        #

        return self.__len__()


class SearchManager(models.Manager):
    '''
    SearchManager which supports MySQL and MariaDB full-text search.
    '''
    query_set = models.QuerySet
    def __init__(self, fields=None):
        super(SearchManager, self).__init__()
        self.search_fields = fields
        if (fields):
            self.query_set = SearchQuerySet

    def contribute_to_class(self, cls, name):
        super(SearchManager, self).contribute_to_class(cls, name);

        # this is the function that sets the model attribute. So we check
        # here if it actually has the fields in the Meta class.
        if (hasattr(self.model._meta,"search_fields")):
            self.search_fields = self.model._meta.search_fields
            self.query_set = SearchQuerySet

    def get_query_set(self):
        '''
        Returns the query set.
        '''
        return self.query_set(model=self.model, fields=self.search_fields)

    def search(self, query, **kwargs):
        '''
        Runs a fulltext search against the fields defined in the method's kwargs
        or in the constructor's kwargs.
        For more informations read the documentation string of the
        SearchQuerySet's search() method.
        '''
        if (not self.search_fields):
            raise exceptions.ImproperlyConfigured(
                "Missing search_fields in the {} model".format(
                    self.model._meta.label
                )
            )
        return self.get_query_set().search(query, **kwargs)

    def get_operation(self):
        if (not self.search_fields):
            return None
        index_name = "{}_fulltext_index".format(
            self.model._meta.label.replace(".","_")
        )
        forward = 'CREATE FULLTEXT INDEX {index} ON {table} {fields}'.format(
            index=index_name,
            table=self.model._meta.db_table,
            fields=str(self.search_fields).replace("'", "")
        )
        back = 'DROP INDEX {index} ON {table}'.format(
            index=index_name,
            table=self.model._meta.db_table
        )
        operation = migrations.RunSQL(
            (forward,),
            (back,)
        )
        return operation
