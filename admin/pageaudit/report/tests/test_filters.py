from django.test import TestCase

from django.contrib.auth.models import User

from ..models import *

def createSuperuser():
    superuser = User(
        first_name='super',
        is_staff=True,
        is_superuser=True,
        last_name='User',
        username='superuser',
    )
    superuser.set_password('password!')
    superuser.save()
    return superuser

def urls():
  return [
      'https://ibm.com/foo',
      'https://ibm.com/bar/baz/biff',
      'https://ibm.com/bar/#w00t',
  ]

def createFilterParts(filters, filter_arr):
    for filter in filters:
        if filter == 'foo':
            UrlFilterPart.objects.create(
                prop='path_segment',
                filter_val=filter,
                url_filter=filter_arr[0],
            )
        elif filter == 'baz':
            UrlFilterPart.objects.create(
                prop='path_segment',
                filter_val='baz',
                filter_path_index=1,
                url_filter=filter_arr[2],
            )
        elif filter == 'w00t':
            UrlFilterPart.objects.create(
                prop='hash',
                filter_val='w00t',
                url_filter=filter_arr[3]
            )

def createUrlObjects(superuser):
    url_arr = []
    for url in urls():
        url_arr.append(
            Url.objects.create(
                created_by=superuser,
                edited_by=superuser,
                url=url
            )
        )
    

class TestUrlFilterSets(TestCase):
    def setUp(self):
        """
        creates urls and filters, and combines them into a set
        """
        superuser = createSuperuser()
        createUrlObjects(superuser)


        filter_set_arr = [
            UrlFilterSet.objects.create(
                name='foo filter or baz filter',
                description='should return the union of the query results for each',
                mode='OR'
            ),
            UrlFilterSet.objects.create(
                name='w00t filter and bar filter',
                description='should return the intersection of the query results for each',
                mode='AND'
            )
        ]

        # make 3 UrlFilters
        filters = ['foo', 'bar', 'baz', 'w00t']
        filter_arr = []
        for filter in filters:
            filter_arr.append(
                UrlFilter.objects.create(
                    name='%s filter' % filter,
                    description='%s filter description' % filter,
                    mode='AND',
                    url_filter_set=filter_set_arr[0] if filter in ['foo', 'baz'] else filter_set_arr[1]
                )
            )
        createFilterParts(filters, filter_arr)

    def test_UrlFilterSets(self):
        foo = UrlFilterSet.objects.get(name='foo filter or baz filter')
        urls = foo.run_query()
        self.assertEqual(list(map(lambda x: x.url, urls)), ['https://ibm.com/foo', 'https://ibm.com/bar/baz/biff'])
        bar = UrlFilterSet.objects.get(name='w00t filter and bar filter')
        urls = bar.run_query()
        self.assertEqual(list(map(lambda x: x.url, urls)), ['https://ibm.com/bar/#w00t'])


class TestUrlFilters(TestCase):
    def setUp(self):
        """
        create some urls and some filters
        """
        superuser = createSuperuser()
        createUrlObjects(superuser)

        # make 3 UrlFilters
        filters = ['foo', 'bar', 'baz', 'w00t']
        filter_arr = []

        for filter in filters:
            filter_arr.append(
                UrlFilter.objects.create(
                    name='%s filter' % filter,
                    description='%s filter description' % filter,
                    mode='AND'
                )
            )
        createFilterParts(filters, filter_arr)

    def test_UrlFilters(self):
        # import ipdb; ipdb.set_trace()
        foo = UrlFilter.objects.get(name='foo filter')
        # import ipdb; ipdb.set_trace()
        urls = foo.run_query()

        self.assertEqual(urls[0].url, 'https://ibm.com/foo')

        bar = UrlFilter.objects.get(name='baz filter')
        urls = bar.run_query()

        self.assertEqual(urls[0].url, 'https://ibm.com/bar/baz/biff')

        woot = UrlFilter.objects.get(name='w00t filter')
        urls = woot.run_query()

        self.assertEqual(urls[0].url, 'https://ibm.com/bar/#w00t')
