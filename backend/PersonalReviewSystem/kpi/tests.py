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
        #要先建這用戶於db 不然login()其實錯了它沒報錯，這邊用基本驗證
        self.csrf_client.login(username='thomaschang', password='Abc12345') # 有 csrf檢查的光login帳密還不夠
        self.non_csrf_client.login(username='thomaschang', password='Abc12345')
        '''# 先塞進一筆才能 get, patch, delete
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
        self.non_csrf_client.post(reverse('employee-list'), self.employee_data, format="json")'''
        self.token_based = True

    def tearDown(self):
        #print('thomas ViewTestCase tearDown')
        self.csrf_client.logout()
        self.non_csrf_client.logout()

    #def test_kpi_user_post_non_csrf(self):
    #    """Test the api has user creation capability."""
    #    print('thomas ViewTestCase test_kpi_user_post_non_csrf')
    #    user_data = {'username': 'lilitseng'}
    #    response = self.non_csrf_client.post(reverse('user-list'), user_data, format="json")
    #    self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    #def test_kpi_employee_create_csrf(self):
        #"""Test the api has employee creation capability."""
        #print('thomas ViewTestCase test_kpi_employee_create_csrf')
        #response = self.csrf_client.post(reverse('employee-list'), self.employee_data, format="json")
        #self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def create_fake_employee_data(self):
        # 多生幾個員工
        another = {
            "employee_number": "P0001", "ad_account": "P0001", "current_duration": "2016.Q2",
            "user":{"username": "ypjou", "password": "Abc12345",  "email": "ypjou@ycceth.com"},
            "employees":[
                {"employee_number": "P0002", "ad_account": "P0002", "current_duration": "2016.Q2","user":{"username": "morris", "password": "Abc12345", "email": "morris@ycceth.com"}, "manager": "ypjou"},
                {"employee_number": "P0003", "ad_account": "P0003", "current_duration": "2016.Q2","user":{"username": "brian", "password": "Abc12345", "email": "brian@ycceth.com"}, "manager": "ypjou"}
            ]
        }
        response = self.non_csrf_client.post(reverse('employee-list'), another, format="json")
        print('建完第一批員工假資料')
        # 接著建立其它員工資訊
        add_more = {
            "employee_number": "P0004", "ad_account": "P0004", "current_duration": "2016.Q2",
            "user":{"username": "thomas", "password": "Abc12345", "email": "thomas@ycceth.com"},
            "manager": "morris",
            "employees":[
                {"employee_number": "P0005", "ad_account": "P0005", "current_duration": "2016.Q2","user":{"username": "cloud", "password": "Abc12345", "email": "cloud@ycceth.com"}, "manager": "brian"},
                {"employee_number": "P0006", "ad_account": "P0006", "current_duration": "2016.Q2","user":{"username": "kirin", "password": "Abc12345", "email": "kirin@ycceth.com"}, "manager": "brian"}
            ]
        }
        response = self.non_csrf_client.post(reverse('employee-list'), add_more, format="json")
        print('建完第二批員工假資料')
        # 未來若要增加新員工資訊
        and_more = {
            "employee_number": "P0007", "ad_account": "P0007", "current_duration": "2016.Q2",
            "user":{"username": "dennis", "password": "Abc12345", "email": "dennis@ycceth.com"},
            "manager": "morris"
        }
        response = self.non_csrf_client.post(reverse('employee-list'), and_more, format="json")
        print('建完第三批員工假資料')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def change_manager(self):
        # 更變 manager
        e = Employee.objects.get(employee_number='P0007')
        print('更改前的主管:', e.manager)
        change_manager = {
            "employee_number": "P0007",
            "manager": "thomas"
        }
        res = self.non_csrf_client.patch(reverse('employee-detail', kwargs={'pk': e.id}), change_manager, format='json')
        e = Employee.objects.get(employee_number='P0007') # 改完後要再取一次才會正確
        print('更改後的主管:', e.manager)

    def dennis_read_employee_list(self):
        print('dennis 取得員工清單開始')
        r = self.client_dennis.get(reverse('employee-list'), format="json")# 讓 dennis 存取一下 employee-list 看幾筆
        #print('dennis get employee-list content:', r.content)
        #print('dennis get employee-list data:', r.data)  # 此時是個 OrderdDict
        #print('dennis get employee-list json():', r.json())
        self.assertEqual(r.json()['count'], 1)
        self.assertEqual(r.data['count'], 1)#len(r.data)會有額外三筆資訊 >.<
        print('dennis 取得員工清單結束')

    def get_employee_detail(self):
        print('dennis 取得員工明細開始')
        r = self.client_dennis.get(reverse('employee-detail', kwargs={'pk': self.dennis_employee_id}), format="json")
        #print('dennis get employee-detail data:', r.data) #此時 data 是個 dict 不用再用 r.json()
        self.assertTrue('id' in r.data)
        print('dennis 取得員工明細結束')

    def thomas_read_employee_list(self):
        print('thomas 取得員工清單開始')
        r = self.client_thomas.get(reverse('employee-list'), format="json")
        self.assertEqual(r.json()['count'], 2)
        print('thomas 取得員工清單結束')

    def login_tested_users(self):
        if self.token_based:
            # Include an appropriate `Authorization:` header on all requests.(務必在settings加 'rest_framework.authentication.TokenAuthentication')
            token = Token.objects.get(user__username='dennis')
            print('方法一取得 token:', token.key)
            ''' 或用下面這個方法取得 token 也行
            resp = self.non_csrf_client.post(reverse('kpi.get_token'), {'username': 'dennis', 'password':'Abc12345'}, format='json')
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            self.assertTrue('token' in resp.data)
            token = resp.data['token']
            print('方法二取得 token:', token)
            '''
            self.client_dennis = APIClient()
            self.client_dennis.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

            token = Token.objects.get(user__username='thomas')
            self.client_thomas = APIClient()
            self.client_thomas.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        else:
            self.client_dennis = APIClient(enforce_csrf_checks=False)
            self.client_dennis.login(username='dennis', password='Abc12345') # 登入失敗不會報錯@@
            self.client_thomas = APIClient(enforce_csrf_checks=False)
            self.client_thomas.login(username='thomas', password='Abc12345') # 登入失敗不會報錯@@

    def employee_myself_kpi(self):
        #dennis 登入填一筆 retro
        # owner 假設用工號, 員工第一次評(沒帶分數)
        print('owner 假設用工號, 員工第一次評(沒帶分數)')
        do_myself = {
            "employee_number": "P0007",
            "retros": [{"wentwell_myself":"verygood", "improve_myself":"somebad"}],
            "kpi_state" : "edit"
        }
        response = self.client_dennis.patch(reverse('employee-detail', kwargs={'pk': self.dennis_employee_id}),do_myself, format='json')
        #print('response:', response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 員工第二次評，有帶分數，順便改資料(模擬保存的狀況)
        print('員工第二次評，有帶分數，順便改資料(模擬保存的狀況)')
        do_myself = {
            "employee_number": "P0007",
            "retros": [ { "wentwell_myself":"modified21", "improve_myself":"modified22", 
                          "evaluation":{
                                         "score":"0.8", 
                                         "eval_by":"P0007"
                           }
                         }],
            "kpi_state" : "edit"
        }
        response = self.client_dennis.patch(reverse('employee-detail', kwargs={'pk': self.dennis_employee_id}),do_myself, format='json')
        #print('response:', response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        print('員工加上三條 PRL')
        do_myself = {
            "employee_number": "P0007",
            "prls": [
                {"prl":"done some vdi test", "status":"80%"},
                {"prl":"done some cpc setup", "status":"90%"},
                {"prl":"fix so many bugs", "status":"70%"}
            ],
            "current_duration": "2016.Q2",
            "kpi_state" : "edit"
        }
        response = self.client_dennis.patch(reverse('employee-detail', kwargs={'pk': self.dennis_employee_id}),do_myself, format='json')
        #print('response:', response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        print('員工修改成兩條 PRL 並完成自評')
        do_myself = {
            "employee_number": "P0007",
            "prls": [
                {"prl":"make good on ipexplex", "status":"80%"},
                {"prl":"doing better in ci/cd", "status":"90%"}
            ],
            "current_duration": "2016.Q2",
            "kpi_state" : "employee_submit"
        }
        response = self.client_dennis.patch(reverse('employee-detail', kwargs={'pk': self.dennis_employee_id}),do_myself, format='json')
        #print('response:', response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_kpi_employee_function_non_csrf(self):
        """Test the api has employee creation capability."""
        print('ViewTestCase test_kpi_employee_create_non_csrf')
        #response = self.non_csrf_client.post(reverse('employee-list'), self.employee_data, format="json")
        # 產生幾筆假資料
        self.create_fake_employee_data()
        self.dennis_employee_id = Employee.objects.get(employee_number='P0007').id
        self.change_manager()
        # 讓幾位主角登場
        self.login_tested_users()
        # 測試權限
        self.dennis_read_employee_list() # dennis 看 employee-list 應該只有 1 筆
        self.thomas_read_employee_list() # thomas 看 employee-list 應該只有 2 筆
        # 測試員工基本資料
        self.get_employee_detail()
        # 測試員工自評
        self.employee_myself_kpi()
        

        
        
        print('這邊想想想想想想要要要要測測測測測什麼什麼什麼什麼什麼')
        
        
        

        
        print('然後除錯然後除錯然後除錯然後除錯然後除錯然後除錯然後除錯')
        
        
        

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