from django.conf.urls import url, include
from rest_framework import renderers
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import DefaultRouter
from rest_framework.documentation import include_docs_urls

from rest_framework.authtoken import views
#from rest_framework.schemas import get_schema_view
#from . import views
from .views import UserViewSet, EmployeeViewSet, RetrospectiveViewSet, EvaluationViewSet, PRLViewSet, hello, send_mail, SendMailView, CustomAuthToken#, api_root


#snippet_list = SnippetViewSet.as_view({'get': 'list', 'post': 'create'})
#snippet_detail = SnippetViewSet.as_view({
#    'get': 'retrieve',
#    'put': 'update',
#    'patch': 'partial_update',
#    'delete': 'destroy'
#})
#snippet_highlight = SnippetViewSet.as_view({'get': 'highlight'}, renderer_classes=[renderers.StaticHTMLRenderer])
#user_list = UserViewSet.as_view({'get': 'list'})
#user_detail = UserViewSet.as_view({'get': 'retrieve'})
# 上面那幾個都不用再自己寫了，只要把它們註冊進 router就好，它也會自動生成 API root view 故 views.py 那份不用了!!!
router = DefaultRouter()
#router.register(r'snippets', SnippetViewSet)
router.register(r'users', UserViewSet)
router.register(r'employee', EmployeeViewSet)
router.register(r'retrospective', RetrospectiveViewSet)
router.register(r'evaluation', EvaluationViewSet)
router.register(r'prl', PRLViewSet)

#schema_view = get_schema_view(title='Pastebin API') #自動產生 schema view


print('kpi.urls.py begin >>>>>')
# API endpoints
urlpatterns = [
    #url(r'^$', api_root), # 這裡是我們 api 的入口
    #url(r'^snippets/$', snippet_list, name='snippet-list'),
    #url(r'^snippets/(?P<pk>[0-9]+)/$', snippet_detail, name='snippet-detail'),
    #url(r'^snippets/(?P<pk>[0-9]+)/highlight/$', snippet_highlight, name='snippet-highlight'),
    #url(r'^users/$', user_list, name='user-list'),
    #url(r'^users/(?P<pk>[0-9]+)/$', user_detail, name='user-detail'),
    # 上面也可簡化成一行
    url(r'^', include(router.urls)),
    url(r'^hello/$', hello, name='kpi.hello'),
    url(r'^send_mail/$', SendMailView.as_view(), name='kpi.send_mail'),
    #url(r'^employee/$', EmployeeView.as_view(), name="employee-list"),
    #來試試內建的得到 token 的 view，需用 post 方法送 username/password
    #url(r'^api-token-auth/', views.obtain_auth_token),
    url(r'^get-token/', CustomAuthToken.as_view(), name='kpi.get_token'),

    #url(r'^schema/$', schema_view), #試不出來
    url(r'^docs/', include_docs_urls(title="InQuartik's PRS API")), #預設其request=None
    # Generate schema with valid `request` instance:
    #url(r'^docs/', include_docs_urls(title='My API title', public=False)),
]
#urlpatterns = format_suffix_patterns(urlpatterns) #現在也不用了，有了ViewSet/Router
print('kpi.urls.py end >>>>>')
