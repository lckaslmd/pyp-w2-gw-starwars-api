from starwars_api.client import SWAPIClient
from starwars_api.exceptions import SWAPIClientError

api_client = SWAPIClient()

class BaseModel(object):

    def __init__(self, json_data):
        """
        Dynamically assign all attributes in `json_data` as instance
        attributes of the Model.
        """
        for key, value in json_data.items():
            setattr(self, key, value)

    @classmethod
    def get(cls, resource_id):
        """
        Returns an object of current Model requesting data to SWAPI using
        the api_client.
        """
        return cls(cls.dispatcher('get_resource_from_api')(resource_id))

    @classmethod
    def all(cls):
        """
        Returns an iterable QuerySet of current Model. The QuerySet will be
        later in charge of performing requests to SWAPI for each of the
        pages while looping.
        """
        return cls.dispatcher('create_query_set')()


class OperationsForPeople(object):

    @classmethod
    def dispatcher(cls, fun):
        return { 'get_resource_from_api': lambda x: api_client.get_people(x),
                 'create_query_set':      lambda: PeopleQuerySet(),
                 'max_resources':         lambda: api_client.get_people()['count'],
               }[fun]


class OperationsForFilms(object):

    @classmethod
    def dispatcher(cls, fun):
        return { 'get_resource_from_api': lambda x: api_client.get_films(x),
                 'create_query_set':      lambda: FilmsQuerySet(),
                 'max_resources':         lambda: api_client.get_films()['count'],
               }[fun]


class People(BaseModel, OperationsForPeople):
    """Representing a single person"""
    
    def __init__(self, json_data):
        super(People, self).__init__(json_data)

    def __repr__(self):
        return 'Person: {0}'.format(self.name)


class Films(BaseModel, OperationsForFilms):

    def __init__(self, json_data):
        super(Films, self).__init__(json_data)
        
    def __repr__(self):
        return 'Film: {0}'.format(self.title)


class BaseQuerySet(object):
    
    def __init__(self):
        self.counter = 0
            
    def __iter__(self):
        self.counter = 0
        return self

    def __next__(self):
        if self.counter < self.dispatcher('max_resources')():
            self.counter += 1
            return self.__class__.resource_class.get(self.counter)
        raise StopIteration()

    next = __next__

    def __len__(self):
        return self.count()

    def count(self):
        """
        Returns the total count of objects of current model.
        If the counter is not persisted as a QuerySet instance attr,
        a new request is performed to the API in order to get it.
        """
        return len([ resource for resource in self ])


class PeopleQuerySet(BaseQuerySet, OperationsForPeople):
    resource_class = People

    def __init__(self):
        super(PeopleQuerySet, self).__init__()

    def __repr__(self):
        return 'PeopleQuerySet: {0} objects'.format(str(len(self)))


class FilmsQuerySet(BaseQuerySet, OperationsForFilms):
    resource_class = Films
    
    def __init__(self):
        super(FilmsQuerySet, self).__init__()

    def __repr__(self):
        return 'FilmsQuerySet: {0} objects'.format(str(len(self)))
