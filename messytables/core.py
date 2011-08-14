from messytables.util import OrderedDict

class Cell(object):
    """ A cell is the basic value type. It always has a ``value`` (that
    may be ``None`` and may optionally also have a type and column name
    associated with it. If no ``type`` is set, the String type is set
    but no type conversion is set. """

    def __init__(self, value, column=None, type=None):
        if type is None:
            from messytables.types import StringType
            type = StringType()
        self.value = value
        self.column = column
        self.column_autogenerated = False
        self.type = type

    def __repr__(self):
        if self.column is not None:
            return "<Cell(%s=%s:%s>" % (self.column, 
                    self.type, self.value)
        return "<Cell(%r:%s>" % (self.type, self.value)

    @property
    def empty(self):
        """ Stringify the value and check that it has a length. """
        if self.value is None:
            return True
        value = self.value
        if not isinstance(value, basestring):
            value = unicode(value)
        if len(value.strip()):
            return False
        return True


class TableSet(object):
    """ A table set is used for data formats in which multiple tabular
    objects are bundeled. This might include relational databases and 
    workbooks used in spreadsheet software (Excel, LibreOffice). """

    @classmethod
    def from_fileobj(cls, fileobj):
        """ The primary way to instantiate is through a file object 
        pointer. This means you can stream a table set directly off 
        a web site or some similar source. """
        pass

    @property
    def tables(self):
        """ Return a listing of tables in the ``TableSet``. Each table
        has a name. """
        pass


class RowSet(object):
    """ A row set (aka: table) is a simple wrapper for an iterator of 
    rows (which in turn is a list of ``Cell`` objects). The main table
    iterable can only be traversed once, so on order to allow analytics 
    like type and header guessing on the data, a sample of ``window``
    rows is read, cached, and made available. """
    
    def __init__(self, typed=False):
        self.typed = typed
        self._processors = []
        self._types = None

    def set_types(self, types):
        self.typed = True
        self._types = types

    def get_types(self):
        return self._types

    types = property(get_types, set_types)

    def register_processor(self, processor):
        """ Register a stream processor to be used on each row. A 
        processor is a function called with the ``RowSet`` as its 
        first argument and the row to be processed as the second 
        argument. """
        self._processors.append(processor)

    def __iter__(self):
        """ Apply several filters to the row data. """
        for row in self.raw():
            for processor in self._processors:
                row = processor(self, row)
                if row is None:
                    break
            if row is not None:
                yield row

    def dicts(self):
        """ Return a representation of the data as an iterator of
        ordered dictionaries. This is less specific than the cell
        format returned by the generic iterator but only gives a 
        subset of the information. """
        if not self.column_headers:
            raise TypeError("No column headers are defined!")
        for row in self:
            yield OrderedDict([(c.column, c.value) for c in row])

    def __repr__(self):
        return "RowSet(%s)" % self.name

