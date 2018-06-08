from rest_framework import permissions
from .models import Employee, Evaluation, Retrospective

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.owner == request.user


# 要實作之前讀一下 http://www.django-rest-framework.org/api-guide/permissions/
# https://stackoverflow.com/questions/23447157/how-do-i-set-up-permissions-in-django-rest-framework-so-that-the-session-user-ca
class IsOwnerOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit/view it.
    """

    def has_object_permission(self, request, view, obj):
        # 要寫一個判斷是不是上一層主管的 函式!!!! 若是主管那也可以 Read
        # Write permissions are only allowed to the owner of the snippet.
        return obj.owner == request.user

class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    認證完後會針對 permission list 中所有的 permission 都呼叫這個方法
    """
    #def has_permission(self, request, view):
    #    print('thomas >>>>> has_permission')
    #    return request.user and request.user.is_authenticated

    # only runs when called on a view for a single object, so that won't work to enforce permissions for list views
    # 這邊只有當要存取 detail view 時會被叫，若要檔 list view 要改 queryset
    def has_object_permission(self, request, view, obj):
        #print('thomas >>>>> has_object_permission')
        request_user_employee = None
        try:
            request_user_employee = request.user.employee.get()
        except Employee.DoesNotExist:
            if request.user.username in ['thomaschang', 'admin']:
                print('[permission] this is the develop mode, return all queryset')
                return True
            print('[permission] request user has no employee relationship')
            return False
        except AttributeError as error:
            print('[permission] WRONG:', error)
            return False

        if obj.owner == request.user:
            print('[permission] request user is owner')
            return True
        elif obj.is_member_of(request_user_employee):
            print('[permission] request user is manager')
            return True
        else:
            #print('[permission] request user is not owner')
            # 對於受邀與諮詢評分的主管也要能看到該員的資料，因此需從 Evaluation.eval_by 去看
            # 方法一：直接用 Evaluation 物件過濾
            emp = request.user.employee.get()
            evas = Evaluation.objects.filter(eval_by=emp).filter(eval_by__current_duration=emp.current_duration).count()
            if evas != 0:
                print('[permission] request user is not owner but invited manager')
                return True
            # 方法二：這方法先找 owner 本期的 retro 再去找 evaluation 的 eval_by 是 request.user 的
            #retro = Retrospective.objects.filter(current_duration=obj.current_duration).get(owner=obj)
            #try:
            #    invited_evaluation = retro.evaluation.get(eval_by=request.user.employee.get()) # 是不是還要加個 type='邀請評分'
                # 如果有就充許他看
            #    return True
            #except Evaluation.DoesNotExist:
            #    print('[permission] Not invited manager relationship')
            #    return False
        return False
