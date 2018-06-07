"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from datetime import date

import django
from django.test import TestCase
from django.contrib.auth.models import User

# for test views
from django.urls import reverse    #from django.core.urlresolvers import reverse
from rest_framework.test import APIClient # Extends django's Client class
from rest_framework import status

from .models import Employee, Duration, Retrospective, Evaluation

# TODO: Configure your database in settings.py and sync before running tests.
class ModelTestCase(TestCase):
    """Tests for the application views."""

    # Django requires an explicit setup() when running tests in PTVS
    @classmethod
    def setUpClass(cls):
        #print('thomas ModelTestCase setUpClass')
        super(ModelTestCase, cls).setUpClass()
        django.setup()

    def setUp(self):
        """Define the test client and other test variables."""
        #print('thomas ModelTestCase setUp')
        #self.snippet_title = "Write world class code"
        #self.snippet = Snippet(code='print bbkjkjkk', owner=user_thomas)
        #u = User(username='userAbc'); u.save()
        # 產生測試資料 #日期:date(2016, 1, 1)
        self.du1 = Duration.objects.create(name='2016.Q1', start_date=date(2016,1,1), end_date=date(2016,3,31))
        self.du2 = Duration.objects.create(name='2016.Q2', start_date=date(2016,4,1), end_date=date(2016,6,30))
        self.du3 = Duration.objects.create(name='2016.Q3', start_date=date(2016,7,1), end_date=date(2016,9,30))
        user_yp = User.objects.create(username="yp")
        user_morris = User.objects.create(username="morris")
        user_thomas = User.objects.create(username='thomaschang')
        self.employee_yp = Employee.objects.create(employee_number='P0001', ad_account='ypjou', owner=user_yp, role='正職', current_duration=self.du1)
        self.employee_morris = Employee.objects.create(employee_number='P0099', ad_account='morristsao', owner=user_morris, manager=user_yp, role='顧問', current_duration=self.du2)
        self.employee_thomas = Employee.objects.create(employee_number='P0021', ad_account='thomaschang', owner=user_thomas, manager=user_morris, role='約聘', current_duration=self.du3)

    def test_duration_multi_get(self):
        """Test if we can get multiple items from Duration model"""
        start=date(2015,11,1)
        end=date(2016,6,1)
        queryset = Duration.objects.order_by('start_date').filter(start_date__gte=start).filter(end_date__lt=end) # 取出2016.Q1
        print(queryset.count())
        for q in queryset:
            print(q.name)
        end=date(2016,7,31)
        queryset = Duration.objects.order_by('start_date').filter(start_date__gte=start).filter(end_date__lt=end) # 取出2016.Q1, 2016.Q2
        print(queryset.count())
        for q in queryset:
            print(q.name)
        
    def test_employee_manager(self):
        """Test the Employee model's manager relationship"""
        print('yp.is_member_of(yp):',         self.employee_yp.is_member_of(self.employee_yp))
        print('morris.is_member_of(morris):', self.employee_morris.is_member_of(self.employee_morris))
        print('thomas.is_member_of(thomas):', self.employee_thomas.is_member_of(self.employee_thomas))
        print('yp.is_member_of(morris):',     self.employee_yp.is_member_of(self.employee_morris))
        print('yp.is_member_of(thomas):',     self.employee_yp.is_member_of(self.employee_thomas))
        print('morris.is_member_of(yp):',     self.employee_morris.is_member_of(self.employee_yp))
        print('morris.is_member_of(thomas):', self.employee_morris.is_member_of(self.employee_thomas))
        print('thomas.is_member_of(yp):',     self.employee_thomas.is_member_of(self.employee_yp))
        print('thomas.is_member_of(morris):', self.employee_thomas.is_member_of(self.employee_morris))

    #def test_model_can_create_a_snippet(self):
    #    """Test the Snippet model can create a snippet."""
    #    #print('thomas test create a snippet')
    #    old_count = Snippet.objects.count()
    #   self.snippet.save()
    #    new_count = Snippet.objects.count()
    #    self.assertNotEqual(old_count, new_count)

    #def test_model_can_create_a_employee(self):
    #    """Test the Employee model can create a employee."""
    #    #print('thomas test create a employee')
    #    old_count = Employee.objects.count()
    #    self.employee.save()
    #    new_count = Employee.objects.count()
    #    self.assertNotEqual(old_count, new_count)


# 我們要測試的部份
#Create a employee – Handle POST request
#Read a employee(s) – Handle GET request
#Update a employee – Handle PUT request
#Delete a employee – Handle DELETE request

class ViewTestCase(TestCase):
    """Test suite for the api views."""

    # Django requires an explicit setup() when running tests in PTVS
    @classmethod
    def setUpClass(cls):
        #print('thomas ViewTestCase setUpClass')
        super(ViewTestCase, cls).setUpClass()
        django.setup()

    def setUp(self):
        """Define the test client and other test variables."""
        #print('thomas ViewTestCase setUp')
        self.csrf_client = APIClient(enforce_csrf_checks=True)
        self.non_csrf_client = APIClient(enforce_csrf_checks=False) #預設是這種
        # create a test user
        self.username = 'thomaschang'
        self.password = 'Abc12345'
        self.user = User.objects.create_user(self.username, self.password)
        self.user.set_password("Abc12345") #一定要再存一次才不會出錯
        self.user.save()
        #print('after create a test user, then we get it')
        #u = User.objects.get(username='thomaschang')
        #print('after get user:', u)
        self.employee_data = {'employee_number':'P0022', 'ad_account':'melontung'}
        #要先建這用戶於db 不然login()其實錯了它沒報錯，這邊用基本驗證
        self.csrf_client.login(username='thomaschang', password='Abc12345') # 有 csrf檢查的光login帳密還不夠
        self.non_csrf_client.login(username='thomaschang', password='Abc12345')
        # 先塞進一筆才能 get, patch, delete
        self.employee = Employee.objects.create(employee_number='P0021', ad_account='thomaschang', owner=self.user)
        self.du1 = Duration.objects.create(name='2016.Q1', start_date=date(2016,1,1), end_date=date(2016,3,31))
        self.retrospective = Retrospective.objects.create(wentwell_myself='很好', wentwell_review='不錯', wentwell_approval='verywell', owner=self.employee, current_duration=self.du1)
        self.eva1 = Evaluation.objects.create(score=1.2, type='邀請評分', eval_by=self.employee, retro=self.retrospective)
        self.eva2 = Evaluation.objects.create(comment='這是諮詢註解', type='諮詢', eval_by=self.employee, retro=self.retrospective)
        # rewrite our test case
        self.employee_data = {
            "employee_number": "P0000", "ad_account": "P0000", "current_duration": "2016.Q2",
            "user":{"username": "pengen", "password": "Abc12345", "email": "pengen@ycceth.com"}
        }
        self.non_csrf_client.post(reverse('employee-list'), self.employee_data, format="json")

    def tearDown(self):
        #print('thomas ViewTestCase tearDown')
        self.csrf_client.logout()
        self.non_csrf_client.logout()

    def test_kpi_user_post_non_csrf(self):
        """Test the api has user creation capability."""
        print('thomas ViewTestCase test_kpi_user_post_non_csrf')
        user_data = {'username': 'lilitseng'}
        response = self.non_csrf_client.post(reverse('user-list'), user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_kpi_employee_create_csrf(self):
        """Test the api has employee creation capability."""
        print('thomas ViewTestCase test_kpi_employee_create_csrf')
        response = self.csrf_client.post(reverse('employee-list'), self.employee_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_kpi_employee_create_non_csrf(self):
        """Test the api has employee creation capability."""
        print('thomas ViewTestCase test_kpi_employee_create_non_csrf')
        #response = self.non_csrf_client.post(reverse('employee-list'), self.employee_data, format="json")
        # 多生幾個員工
        another = {
            "employee_number": "P0001", "ad_account": "P0001", "current_duration": "2016.Q2",
            "user":{"username": "ypjou",  "email": "ypjou@ycceth.com"},

            "employees":[
                {"employee_number": "P0002", "ad_account": "P0002", "current_duration": "2016.Q2","user":{"username": "morris", "email": "morris@ycceth.com"}},
                {"employee_number": "P0003", "ad_account": "P0003", "current_duration": "2016.Q2","user":{"username": "brian", "email": "brian@ycceth.com"}}
            ]
        }
        response = self.non_csrf_client.post(reverse('employee-list'), another, format="json")
        # 接著建立其它員工資訊
        add_more = {
            "employee_number": "P0004", "ad_account": "P0004", "current_duration": "2016.Q2",
            "user":{"username": "thomas", "password": "Abc12345", "email": "thomas@ycceth.com"},
            "manager": "morris",
            "employees":[
                {"employee_number": "P0005", "ad_account": "P0005", "current_duration": "2016.Q2","user":{"username": "cloud", "email": "cloud@ycceth.com"}, "manager": "brian"},
                {"employee_number": "P0006", "ad_account": "P0006", "current_duration": "2016.Q2","user":{"username": "kirin", "email": "kirin@ycceth.com"}, "manager": "brian"}
            ]
        }
        response = self.non_csrf_client.post(reverse('employee-list'), add_more, format="json")
        # 未來若要增加新員工資訊
        and_more = {
            "employee_number": "P0007", "ad_account": "P0007", "current_duration": "2016.Q2",
            "user":{"username": "dennis", "email": "dennis@ycceth.com"},
            "manager": "morris"
        }
        response = self.non_csrf_client.post(reverse('employee-list'), and_more, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # 更變 manager
        change_manager = {
            "employee_number": "P0007",
            "manager": "thomas"
        }
        e = Employee.objects.get(employee_number='P0007')
        res = self.non_csrf_client.patch(reverse('employee-detail', kwargs={'pk': e.id}),change_manager, format='json')
        e = Employee.objects.get(employee_number='P0007')
        print('after change manager:', e.manager)
        # owner 假設用工號, 員工第一次評(沒帶分數)
        do_myself = {
            "employee_number": "P0007",
            "retros": [{"wentwell_myself":"verygood", "improve_myself":"somebad"}]
        }
        response = self.non_csrf_client.patch(reverse('employee-detail', kwargs={'pk': e.id}),do_myself, format='json')
        print('response:', response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    '''
    def test_kpi_employee_get(self):
        """Test the kpi can get a given employee."""
        print('thomas ViewTestCase test_kpi_employee_get')
        employee = Employee.objects.get(ad_account='P0001')
        print('employee id:', employee.id)
        #print('reverse:', reverse('employee-detail', kwargs={'pk': employee.id}))
        response = self.non_csrf_client.get(reverse('employee-detail', kwargs={'pk': employee.id}), format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        #print('response:', response.data)
        self.assertContains(response, employee)

    def test_kpi_employee_put(self): # test update
        """Test the kpi can update a given employee."""
        print('thomas ViewTestCase test_kpi_employee_put')
        change_data = {'ad_account': 'SomethingNew'}
        #Employee.objects.create(employee_number='P0021', ad_account='thomaschang', owner=self.user) # 先塞進一筆才能 get
        e = Employee.objects.get(ad_account='thomaschang')
        print('now ad:', e.ad_account)
        # 用 put 的話每個欄位都要填否則報400錯誤碼, patch只要填部份
        res = self.non_csrf_client.patch(
            reverse('employee-detail', kwargs={'pk': e.id}),
            change_data, format='json'
        )
        e = Employee.objects.get(employee_number='P0021')
        print('after ad:', e.ad_account)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_kpi_employee_delete(self):
        """Test the kpi can delete a employee."""
        print('thomas ViewTestCase test_kpi_employee_delete')
        #Employee.objects.create(employee_number='P0021', ad_account='thomaschang', owner=self.user) # 先塞進一筆才能 get
        e = Employee.objects.get(employee_number='P0021')
        print('hey I want to delete ', e)
        response = self.non_csrf_client.delete(
            reverse('employee-detail', kwargs={'pk': e.id}),
            format='json',
            follow=True)
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)

    ################ Retrospective #######################
    def test_kpi_retrospective_get(self):
        """Test the kpi can get a given retrospective."""
        print('thomas ViewTestCase test_kpi_retrospective_get')
        
        response = self.non_csrf_client.get(reverse('retrospective-detail', kwargs={'pk': self.retrospective.id}), format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        #print('response:', response.data)
        self.assertContains(response, self.retrospective)

    def test_kpi_retrospective_put(self): # test update
        """Test the kpi can update a given retrospective."""
        print('thomas ViewTestCase test_kpi_retrospective_put')
        change_data = {'wentwell_myself': 'SomethingNew'}
        print('before patch:', self.retrospective.wentwell_myself)
        res = self.non_csrf_client.patch(
            reverse('retrospective-detail', kwargs={'pk': self.retrospective.id}),
            change_data, format='json'
        )
        r = Retrospective.objects.get(pk=self.retrospective.id)
        print('after patch:', r.wentwell_myself)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_kpi_retrospective_delete(self):
        """Test the kpi can delete a retrospective."""
        print('thomas ViewTestCase test_kpi_retrospective_delete')
        print('hey I want to delete ', self.retrospective)
        response = self.non_csrf_client.delete(
            reverse('retrospective-detail', kwargs={'pk': self.retrospective.id}),
            format='json',
            follow=True)
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)

    ################ Evaluation #######################
    def test_kpi_evaluation_get(self):
        """Test the kpi can get a given evaluation."""
        print('>>>>>>>>>>>>>>>>>>>thomas ViewTestCase test_kpi_evaluation_get')
        
        response = self.non_csrf_client.get(reverse('evaluation-detail', kwargs={'pk': self.eva1.id}), format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print('response:', response.data)
        self.assertContains(response, self.eva1)
    '''