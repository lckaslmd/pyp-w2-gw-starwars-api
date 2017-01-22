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
            if key is 'results':
                for r_key, r_value in value[0].items():
                    setattr(self, r_key, r_value)
            setattr(self, key, value)

        
    @classmethod
    def get(cls, resource_id):
        """
        Returns an object of current Model requesting data to SWAPI using
        the api_client.
        """
        if cls.RESOURCE_NAME is 'people':
            return People(api_client.get_people(resource_id))
        elif cls.RESOURCE_NAME is 'films':
            return Films(api_client.get_films(resource_id))
        else:
            return None

    @classmethod
    def all(cls):
        """
        Returns an iterable QuerySet of current Model. The QuerySet will be
        later in charge of performing requests to SWAPI for each of the
        pages while looping.
        """
        if cls.RESOURCE_NAME is 'people':
            return PeopleQuerySet()
        elif cls.RESOURCE_NAME is 'films':
            return FilmsQuerySet()
        else:
            return None


class People(BaseModel):
    """Representing a single person"""
    RESOURCE_NAME = 'people'

    def __init__(self, json_data):
        super(People, self).__init__(json_data)

    def __repr__(self):
        return 'Person: {0}'.format(self.name)


class Films(BaseModel):
    RESOURCE_NAME = 'films'

    def __init__(self, json_data):
        super(Films, self).__init__(json_data)

    def __repr__(self):
        return 'Film: {0}'.format(self.title)


class BaseQuerySet(object):

    def __init__(self):
        self.current = None
        self.counter = 1
            
    def __iter__(self):
        self.counter = 1
        if isinstance(self, PeopleQuerySet):
            self.current = People(api_client.get_people(self.counter))
        elif isinstance(self, FilmsQuerySet):
            self.current = Films(api_client.get_films(self.counter))
        return self

    def __next__(self):
        if isinstance(self, PeopleQuerySet):
            while self.counter <= api_client.get_people()['count']:
                self.current = People.get(self.counter)
                self.counter += 1
                return self.current
        elif isinstance(self, FilmsQuerySet):
            while self.counter <= api_client.get_films()['count']:
                self.current = Films.get(self.counter)
                self.counter += 1
                return self.current
        raise StopIteration()

    next = __next__

    def count(self):
        """
        Returns the total count of objects of current model.
        If the counter is not persisted as a QuerySet instance attr,
        a new request is performed to the API in order to get it.
        """
        return len([resource for resource in self])


class PeopleQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'people'

    def __init__(self):
        super(PeopleQuerySet, self).__init__()

    def __repr__(self):
        return 'PeopleQuerySet: {0} objects'.format(str(len(self.objects)))


class FilmsQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'films'

    def __init__(self):
        super(FilmsQuerySet, self).__init__()

    def __repr__(self):
        return 'FilmsQuerySet: {0} objects'.format(str(len(self.objects)))
