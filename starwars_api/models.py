from starwars_api.client import SWAPIClient
from starwars_api.exceptions import SWAPIClientError

api_client = SWAPIClient()

class OperationsForAll(object):

    @classmethod
    def go_to_next(cls, instance):
        """ Assumes instance is a QuerySet for a resource category """
        if instance.counter < instance.dispatcher('max_resources'):
            instance.counter += 1
            return cls.resource_class.get(instance.counter)
        raise StopIteration()


class OperationsForPeople(OperationsForAll):

    @classmethod
    def dispatcher(cls, fun, *params):
        funs = { 'get_resource_from_api': lambda xs: api_client.get_people(xs[0]),
                 'create_query_set':      lambda xs: PeopleQuerySet(),
                 'max_resources':         lambda xs: api_client.get_people()['count'] }
        return funs[fun](params)


class OperationsForFilms(OperationsForAll):

    @classmethod
    def dispatcher(cls, fun, *params):
        funs = { 'get_resource_from_api': lambda xs: api_client.get_films(xs[0]),
                 'create_query_set':      lambda xs: FilmsQuerySet(),
                 'max_resources':         lambda xs: api_client.get_films()['count'] }
        return funs[fun](params)


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
        return cls(cls.dispatcher('get_resource_from_api', resource_id))

    @classmethod
    def all(cls):
        """
        Returns an iterable QuerySet of current Model. The QuerySet will be
        later in charge of performing requests to SWAPI for each of the
        pages while looping.
        """
        return cls.dispatcher('create_query_set')


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
        return self.__class__.go_to_next(self)

    next = __next__

    def count(self):
        """
        Returns the total count of objects of current model.
        If the counter is not persisted as a QuerySet instance attr,
        a new request is performed to the API in order to get it.
        """
        return len([resource for resource in self])


class PeopleQuerySet(BaseQuerySet, OperationsForPeople):
    resource_class = People

    def __init__(self):
        super(PeopleQuerySet, self).__init__()

    def __repr__(self):
        return 'PeopleQuerySet: {0} objects'.format(str(len(self)))
        
    def __len__(self):
        return self.count()        


class FilmsQuerySet(BaseQuerySet, OperationsForFilms):
    resource_class = Films
    
    def __init__(self):
        super(FilmsQuerySet, self).__init__()

    def __repr__(self):
        return 'FilmsQuerySet: {0} objects'.format(str(len(self)))

    def __len__(self):
        return self.count()
