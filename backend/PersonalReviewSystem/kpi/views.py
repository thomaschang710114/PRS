from datetime import date
#from django.shortcuts import render
from django.contrib.auth.models import User, Group

from django.http import Http404, HttpResponse
#from django.http import HttpResponse, JsonResponse
#from django.views.decorators.csrf import csrf_exempt
#from rest_framework.renderers import JSONRenderer
#from rest_framework.parsers import JSONParser
from django.core.mail import send_mail, send_mass_mail
from django.conf import settings

#from rest_framework import status
from rest_framework import mixins
from rest_framework import generics
from rest_framework import permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework import renderers
from rest_framework.decorators import api_view, action, detail_route, list_route
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .models import Employee, Duration, Retrospective, Evaluation, ProfessionReadinessLevel
from .models import ROLE_CHOICES, DEPARTMENT_CHOICES, JOBTITLE_CHOICES, SCHOOL_CHOICES, SCHOOLMAJOR_CHOICES, ACADEMIC_DEGREE_CHOICES
from .serializers import UserSerializer, GroupSerializer, EmployeeSerializer, RetrospectiveSerializer, EvaluationSerializer, ProfessionReadinessLevelSerializer
from .permissions import IsOwnerOrReadOnly, IsOwner

   
# Create your views here.
# 這邊的每個 view 就是 API endpoint

# 將由 DefaultRoute class 自動生成，因為我們有把 ViewSet 註冊進去了
#@api_view(['GET'])
#def api_root(request, format=None):
#    return Response({
#        'users': reverse('user-list', request=request, format=format),
#        'snippets': reverse('snippet-list', request=request, format=format)
#    })

#class UserList(generics.ListAPIView): # 只有 List 功能(不能Create)
#    queryset = User.objects.all()
#    serializer_class = UserSerializer

#class UserDetail(generics.RetrieveAPIView): # 只有 Read 功能
#    queryset = User.objects.all()
#    serializer_class = UserSerializer
# 用 ViewSet 就可將上面兩個二合一 (注意目前這個是 ReadOnly)
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.

    retrieve:
    [中]：回傳給定的 User 物件.<br />
    [英]：Return the given user.

    list:
    [中]：回傳所有用戶串列.<br />
    [英]：Return a list of all the existing users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
#class UserViewSet(viewsets.ModelViewSet):
#    """
#    API endpoint that allows users to be viewed or edited.
#    """
#    queryset = User.objects.all().order_by('-date_joined')
#    serializer_class = UserSerializer


#class GroupViewSet(viewsets.ModelViewSet):
#    """
#    API endpoint that allows groups to be viewed or edited.
#    """
#    queryset = Group.objects.all()
#    serializer_class = GroupSerializer

class EmployeeViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`, `update` and `destroy` actions.

    list:
    [中]：回傳所有 Employee 物件串列.<br />
    [英]：Return all Employee as a list.

    create:
    [中]：生成 Employee 物件.<br />
    [英]：Creating the given Employee.
    ## Post JSON Data Format:
    ```python
    {
       "employee_number":"P0022",
       "ad_account":"melontung"
    }
    {
        "employee_number": "P0014",
        "ad_account": "supingchia",
        "current_duration": "2016.Q1",
        "role": "工讀",
        "department": "智慧財產軟體企劃處(IPSPD)",
        "job_title": "資深協理"
    }
    {
        "employee_number": "P0015",
        "ad_account": "mondela",
        "current_duration": "2016.Q2",
        "role": "正職",
        "department": "智慧財產軟體企劃處(IPSPD)",
        "job_title": "經理",
        "school": "台灣大學",
        "academic_degree": "碩士",
        "manager": "morris"
    }
    ```

    retrieve:
    [中]：回傳給定的 Employee 物件.<br />
    [英]：Return the given Employee.

    update:
    [中]：更新給定的 Employee 物件.<br />
    [英]：Update the given Employee.

    partial_update:
    [中]：部份更新給定的 Employee 物件.<br />
    [英]：Partially update the given Employee.
    ## Patch JSON Data Format:
    ```python
    {
       "ad_account":"something_new"
    }
    ```

    destroy:
    [中]：刪除給定的 Employee 物件.<br />
    [英]：Delete the given Employee.
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = (permissions.IsAuthenticated , IsOwner,)
    #parser_classes = (MyJSONParser,)

    def get_queryset(self):
        """
        This view should return an employee data only for the currently authenticated user.
        tips not used : username = self.request.query_params.get('username', None)
        """
        #user = self.request.user
        request_user_employee = None
        try:
            request_user_employee = self.request.user.employee.get()
        except Employee.DoesNotExist:
            print('[queryset] request user has no employee relationship')
            if self.request.user.username == 'thomaschang':
                print('[queryset] this is the develop mode, return all queryset')
                return Employee.objects.all()
            return None
        except AttributeError as error:
            print('[queryset] WRONG:', error)
            return None

        print('[queryset] request_user_employee:', request_user_employee)
        members = request_user_employee.get_members()
        print('[queryset] its members:', members)

        # 看是不是有接受 request_user 評分的對象，有的話也加入 members
        # 以當期的 evaluation, eval_by=request_user_employee
        evas = Evaluation.objects.filter(eval_by=request_user_employee).filter(eval_by__current_duration=request_user_employee.current_duration)
        #evas = Evaluation.objects.filter(eval_by__role__contains='abc')#
        # 這些 evas 的 retro.owner 通通加進 members
        for eva in evas:
            members.append(eva.retro.owner.owner.username)
        print('[queryset] after adding some members:', members)
        
        #要在 model 新增一個功能能列出 morris 的所有下屬，再用這個 list 去 filter
        #語法 Model.objects.filter(pk__in=[1, 4, 7])
        return Employee.objects.filter(owner__username__in=members)

    def perform_update(self, serializer):
        # 千萬小心在這下斷點可能會導致異常
        param = {}
        print('thomer EmployeeView.perform_update request.user:', self.request.user)
        # 確保要有 'employee_number' 否則 raise
        if 'employee_number' not in self.request.data:
            raise serializers.ValidationError('Must have employee_number field for update.')
        # make sure the manager user object already exist
        if 'manager' in self.request.data:
            try:
                user = User.objects.get(username=self.request.data['manager'])
                param['manager'] = user
            except User.DoesNotExist:
                raise serializers.ValidationError('Cannot find manager {} user object'.format(self.request.data['manager']))
        # user may change Employee's duration
        duration_string = self.request.data.get('current_duration', None)
        if duration_string:
            if duration_string.find('.') == -1:
                raise serializers.ValidationError("Content of current_duration field error. no dot")
            year, du = duration_string.split('.')
            if not year.isdecimal() or du not in ['Q1', 'q1', 'Q2', 'q2', 'Q3', 'q3', 'Q4', 'q4', 'H1', 'h1', 'H2', 'h2']:
                raise serializers.ValidationError("Content of current_duration field error. format")
            param['current_duration'] = duration_string
        # 新增 retrospective
        retros_list = self.request.data.get('retros', None)
        if retros_list:
            for oneRetro in retros_list:
                # 若有 Evaluation 則 eval_by 必填
                eval = oneRetro.get('evaluation', None)
                if eval:
                    if not 'eval_by' in eval:
                        raise serializers.ValidationError('Must have eval_by field in evaluation')
            param['retros'] = retros_list
        # 新增 prls，裡面是個 {} 組成的 list
        # embedded prls 要自己處理
        prls_list = self.request.data.get('prls', None)
        if prls_list:
            param['prls'] = prls_list
        # 邀請評分者
        if 'reviewer' in self.request.data:
            try:
                reviewer = User.objects.get(username=self.request.data['reviewer'])
                param['reviewer'] = reviewer
            except User.DoesNotExist:
                raise serializers.ValidationError('Cannot find reviewer {} user object'.format(self.request.data['reviewer']))
        # mail_list
        #print('[perform_update] self:', self)
        mail_list = self.request.data.get('mail_list', None)
        if mail_list:
            #param['mail_list'] = mail_list
            #同時處理送信 send_mail('Subject', 'the message.', settings.DEFAULT_FROM_EMAIL, ['yachih_chang@yahoo.com.tw'], fail_silently=False)
            mail_subject = '!!KPI Evaluation Invited!!'
            to_be_evaluated = Employee.objects.get(employee_number=self.request.data['employee_number'])
            comment = self.request.data.get('comment', '')
            mail_message = '{} want to invite you to evaluate {} kpi.\nHere is the link:{}\n\nComment:\n{}\n'.format(reviewer, to_be_evaluated, reverse('employee-detail', kwargs={'pk': to_be_evaluated.id}, request=self.request), comment)
            #mail_list = [User.objects.get(username=invite_user) for invite_user in mail_list]
            #send_mail(mail_subject, mail_message, settings.DEFAULT_FROM_EMAIL, mail_list, fail_silently=False)
            invite_manager = []
            # 另一種方式評估一下
            datatuple = []
            for invite_user in mail_list:
                prefix = 'Dear {},\n\n'.format(invite_user)
                postfix = '\nBest Regards,\nPersonal Review System.'
                who = User.objects.get(username=invite_user)
                invite_manager.append(who)
                tp = (mail_subject, prefix+mail_message+postfix, settings.DEFAULT_FROM_EMAIL, [who.email])
                datatuple.append(tp)
            send_mass_mail(tuple(datatuple))
            param['mail_list'] = invite_manager
        print('thomas >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        serializer.save(**param)

    def perform_create(self, serializer):
        param = {} #{'owner':self.request.user}
        print('thomer EmployeeView.perform_create request.user:', self.request.user)
        role_choice = [j for i,j in ROLE_CHOICES]
        dept_choice = [j for i,j in DEPARTMENT_CHOICES]
        jb_choice = [j for i,j in JOBTITLE_CHOICES]
        sch_choice = [j for i,j in SCHOOL_CHOICES]
        sch_major_choice = [j for i,j in SCHOOLMAJOR_CHOICES]
        aca_degree_choice = [j for i,j in ACADEMIC_DEGREE_CHOICES]
        check_choice = [('role', role_choice), ('department', dept_choice), ('job_title', jb_choice),
                        ('school', sch_choice), ('school_major', sch_major_choice), ('academic_degree', aca_degree_choice)]
        for item, choice in check_choice:
            get_item = self.request.data.get(item, None)
            if get_item and get_item not in choice:
                raise serializers.ValidationError("Content of {} field error.".format(item))

        # check current_duration format, current_duration 是 fk 要自行帶入
        duration_string = self.request.data.get('current_duration', None)
        if duration_string:
            if duration_string.find('.') == -1:
                raise serializers.ValidationError("Content of current_duration field error. no dot")
            year, du = duration_string.split('.')
            if not year.isdecimal() or du not in ['Q1', 'q1', 'Q2', 'q2', 'Q3', 'q3', 'Q4', 'q4', 'H1', 'h1', 'H2', 'h2']:
                raise serializers.ValidationError("Content of current_duration field error. format")
            param['current_duration'] = duration_string

        # make sure the manager user object already exist
        if 'manager' in self.request.data:
            try:
                user = User.objects.get(username=self.request.data['manager'])
                param['manager'] = user
            except User.DoesNotExist:
                raise serializers.ValidationError('Cannot find manager {} user object'.format(self.request.data['manager']))

        # 從employee_number 與 request.user 比對一下是否為「自評」
        #employee_number = self.request.data.get('employee_number', None) # 這欄位必填
        #if not employee_number:
        #    raise serializers.ValidationError("Must have employee_number field.")
        #try:
        #    employee = Employee.objects.get(employee_number=employee_number)
        #    print('this form is filled by employee {} request send by {}'.format(employee.owner.username, self.request.user.username))
        #except User.DoesNotExist:
        #    raise serializers.ValidationError('Cannot find employee object belong to {}'.format(employee_number))

        # embedded user dic doesn't contain in serializer.validated_data 要自己從 self.request.data 加
        user_dict = self.request.data.get('user', None)
        if user_dict:
            param['user'] = user_dict
        # embedded employees dic 要自己處理
        additional_employee_data = self.request.data.get('employees', None)
        if additional_employee_data:
            param['addition_employees'] = additional_employee_data
        # EmployeeSerilizer.save() -> create() / update()
        serializer.save(**param)

class RetrospectiveViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`, `update` and `destroy` actions.

    list:
    [中]：回傳所有 Retrospective 物件串列.<br />
    [英]：Return all retrospective as a list.

    create:
    [中]：生成 Retrospective 物件.<br />
    [英]：Creating the given Retrospective.

    retrieve:
    [中]：回傳給定的 Retrospective 物件.<br />
    [英]：Return the given Retrospective.

    update:
    [中]：更新給定的 Retrospective 物件.<br />
    [英]：Update the given Retrospective.

    partial_update:
    [中]：部份更新給定的 Retrospective 物件.<br />
    [英]：Partially update the given Retrospective.
    ## Patch JSON Data Format:
    ```python
    {
        "wentwell_myself": "SomethingNew"
    }
    ```

    destroy:
    [中]：刪除給定的 Retrospective 物件.<br />
    [英]：Delete the given Retrospective.
    """
    queryset = Retrospective.objects.all()
    serializer_class = RetrospectiveSerializer
#    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,) #這邊權限要比 Snippets 更嚴格，之後再來改!!

    def perform_create(self, serializer):
        param = {'owner':self.request.user}
        print('thomer [Not Implement well] RetrospectiveView.perform_create request.user:', self.request.user)
        serializer.save(**param)

class EvaluationViewSet(viewsets.ModelViewSet):
    queryset = Evaluation.objects.all()
    serializer_class = EvaluationSerializer

class PRLViewSet(viewsets.ModelViewSet):
    queryset = ProfessionReadinessLevel.objects.all()
    serializer_class = ProfessionReadinessLevelSerializer

# 未來可以再加強 http://cheng.logdown.com/posts/2015/10/27/how-to-use-django-rest-frameworks-token-based-authentication
# 這個 token有幾個缺點上文有提
# https://chrisbartos.com/articles/how-to-implement-token-authentication-with-django-rest-framework/ 這範例值得看
class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })

class SendMailView(APIView):
    """
    List some, or create some.
    """
    authentication_classes = (TokenAuthentication,)#(SessionAuthentication, BasicAuthentication)
    def get(self, request, format=None):
        #snippets = Snippet.objects.all()
        #serializer = SnippetSerializer(snippets, many=True)
        #return Response(serializer.data)
        #send_mail('Subject here', 'Here is the message.', settings.DEFAULT_FROM_EMAIL, ['yachih_chang@yahoo.com.tw'], fail_silently=False)
        # learn the authentication
        user = UserSerializer(request.user, context={'request': request})
        content = {
            'user': user.data,  #serializers.Serializer('json', request.user),  # `django.contrib.auth.User` instance.
            #'auth': request.auth,  # None
        }
        return Response(content)
        #return Response('OK!') #you should return some JSON

    def patch(self, request, format=None):
        print('111111111111111')
        print('222222222222222', request.data)
        pass

def send_mail(request):
    #應該要用 @api_view 在函式外以確保收到的是 drf 的 Request/Response 而非 dj 的 HttpRequest/HttpResponse
    #所以這邊要改用 APIView class 之類的
    from django.core.mail import send_mail
    from django.conf import settings
    send_mail('Subject here', 'Here is the message.', settings.DEFAULT_FROM_EMAIL, ['yachih_chang@yahoo.com.tw'], fail_silently=False)
    return HttpResponse('OK!')

def hello(request):
    print('say hello')
    du1 = Duration.objects.get(name='2016.Q1')#Duration.objects.create(name='2016.Q1', star_date=date(2016,1,1), end_date=date(2016,3,31))
    du2 = Duration.objects.get(name='2016.Q2')#Duration.objects.create(name='2016.Q2', star_date=date(2016,4,1), end_date=date(2016,6,30))
    #du3 = Duration.objects.get(name='2016.Q3')#Duration.objects.create(name='2016.Q3', star_date=date(2016,7,1), end_date=date(2016,9,30))
    #start=date(2015,11,1)
    #end=date(2016,6,1)
    #queryset = Duration.objects.order_by('start_date').filter(start_date__gte=start).filter(end_date__lt=end) # 取出2016.Q1
    #print(queryset.count())
    #end=date(2016,7,31)
    #queryset = Duration.objects.order_by('start_date').filter(start_date__gte=start).filter(end_date__lt=end) # 取出2016.Q1, 2016.Q2
    #print(queryset.count())
    user_yp = User.objects.get(username="yp")
    employee_yp = user_yp.employee.get()
    Retrospective.objects.create(wentwell_myself='很好', wentwell_review='不錯', wentwell_approval='verywell', owner=employee_yp, current_duration=du1)
    Retrospective.objects.create(wentwell_myself='認真', wentwell_review='負責', wentwell_approval='可靠', owner=employee_yp, current_duration=du2)
    #user_morris = User.objects.get(username="morris")
    #user_thomas = User.objects.get(username='thomaschang')
    #employee_yp = Employee.objects.filter(ad_account='ypjou').update(role='正職', current_duration=du1)
    #employee_morris = Employee.objects.filter(ad_account='morristsao').update(role='顧問', current_duration=du2)
    #employee_thomas = Employee.objects.filter(ad_account='thomaschang').update(role='約聘', current_duration=du3)
    #print('morris.is_member_of(thomas):', employee_morris.is_member_of(employee_thomas))
    #print('thomas.is_member_of(yp):',     employee_thomas.is_member_of(employee_yp))
    #print('thomas.is_member_of(morris):', employee_thomas.is_member_of(employee_morris))
    return HttpResponse('OK!')

