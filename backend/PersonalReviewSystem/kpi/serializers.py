from datetime import date
from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import Employee, Duration, Retrospective, Evaluation, ProfessionReadinessLevel

#class UserSerializer(serializers.ModelSerializer):#---->這個不會處理 foreign key 的關係所以要自己弄
    #snippets.owner 有關聯到 User model
#    snippets = serializers.PrimaryKeyRelatedField(many=True, queryset=Snippet.objects.all())
#    class Meta:
#        model = User
#        fields = ('id', 'username', 'snippets')

# 會多一個 url 指到 {model}-detail 這個 view
# 對於關聯不是用對方的 pk(如 1,2,3) 而是變成 url(如 http://xxx/snippets/1 這樣
class UserSerializer(serializers.HyperlinkedModelSerializer): # 會自動產生一個 'url' field, 沒有 id, 建立的關聯用 HyperlinkedRelated
    #snippets = serializers.PrimaryKeyRelatedField(many=True, queryset=Snippet.objects.all()) # 如果這樣寫 user 底下的 snippets 就會以 id 的方式呈現
    #snippets = serializers.HyperlinkedRelatedField(many=True, view_name='snippet-detail', read_only=True) # 以連結的方式呈現，會自動產生 snippet-detail 對應的 URL link
    #employee = serializers.HyperlinkedRelatedField(many=True, view_name='employee-detail', read_only=True)
    #managee  = serializers.HyperlinkedRelatedField(many=True, view_name='employee-detail', read_only=True)意思會剛好相反yp的manager變成有morris
    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'employee', 'managee')

#class UserSerializer(serializers.HyperlinkedModelSerializer):#---->這邊可試試不同的情況
#    class Meta:
#        model = User
#        fields = ('url', 'username', 'email', 'groups')

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')

class ProfessionReadinessLevelSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer to map the Model instance into JSON format."""
    owner = serializers.ReadOnlyField(source='owner.owner.username') # 這樣才知道它的owner要顯示成什麼
    current_duration = serializers.ReadOnlyField(source='current_duration.name')
    class Meta:
        model = ProfessionReadinessLevel
        fields = ('url', 'id', 'prl', 'status', 'supervisor_feedback', 'owner', 'current_duration')

class EvaluationSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer to map the Model instance into JSON format."""
    retro = serializers.ReadOnlyField(source='retro.owner.owner.username') # 這樣才知道它的owner要顯示成什麼
    eval_by = serializers.ReadOnlyField(source='eval_by.owner.username')
    class Meta:
        model = Evaluation
        fields = ('url', 'id', 'score', 'comment', 'type', 'done', 'eval_by', 'retro', )
        read_only_fields = ('date_created', 'date_modified', )

class RetrospectiveSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer to map the Model instance into JSON format."""
    owner = serializers.ReadOnlyField(source='owner.owner.username') # 這樣才知道它的owner要顯示成什麼
    current_duration = serializers.ReadOnlyField(source='current_duration.name')
    evaluation = EvaluationSerializer(many=True, required=False)#serializers.HyperlinkedRelatedField(many=True, view_name='evaluation-detail', read_only=True) # reverse FK
    # 額外的欄位
    submit_enabled = serializers.SerializerMethodField()
    class Meta:
        model = Retrospective
        fields = ('url', 'id', 'wentwell_myself', 'wentwell_review', 'wentwell_approval', 'improve_myself', 'improve_review', 'improve_approval', 
                  'support', 'support_reason', 'inspire', 'inspire_reason', 'metrics', 'owner', 'current_duration', 'evaluation', 'submit_enabled')

    def get_submit_enabled(self, obj):
        #print('[RetrospectiveSerializer] get_submit_enabled')
        all_eva = obj.evaluation.all()
        for item in all_eva:
            #print('eva id:{}, done:{}'.format(item.id, item.done))
            if item.done == False:
                return False
        return True

class EmployeeSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer to map the Model instance into JSON format."""
    owner = serializers.ReadOnlyField(source='owner.username') # 這樣才知道它的owner要顯示成什麼
    manager = serializers.ReadOnlyField(source='manager.username')
    current_duration = serializers.ReadOnlyField(source='current_duration.name')
    profession_readiness_level = ProfessionReadinessLevelSerializer(many=True, required=False)                                              # reverse FK
    retrospective = RetrospectiveSerializer(many=True, required=False)#serializers.HyperlinkedRelatedField(many=True, view_name='retrospective-detail', read_only=True)# # reverse FK
    #evaluation = EvaluationSerializer(many=True, required=False)#serializers.HyperlinkedRelatedField(many=True, view_name='evaluation-detail', read_only=True)# reverse FK
    # 額外的欄位
    uppermanager = serializers.SerializerMethodField()
    class Meta:
        model = Employee
        fields = ('url', 'id', 'employee_number', 'ad_account', 'owner', 'manager', 'current_duration', 'retrospective', 'profession_readiness_level',
                  'role', 'kpi_state', 'department', 'job_title', 'onboard_date', 'school', 'school_major', 'academic_degree', 'uppermanager') # 可以再隨時新加想回傳給client的欄位
        #read_only_fields = (,)

    def get_uppermanager(self, obj):
        if obj.manager:
            user = obj.manager.employee.get().manager
            if user:
                return str(user)
        return ''

    @classmethod
    def make_time_tuple(cls, name):
        # return start_date, end_date in date(2016,1,1) format
        # name may be '2015.Q1'
        year, duration = name.split(sep='.')
        if duration in ['Q1', 'q1']:
            return date(int(year), 1, 1), date(int(year), 3, 31)
        elif duration == ['Q2', 'q2']:
            return date(int(year), 4, 1), date(int(year), 6, 30)
        elif duration == ['Q3', 'q3']:
            return date(int(year), 7, 1), date(int(year), 9, 30)
        elif duration == ['Q4', 'q4']:
            return date(int(year), 10, 1), date(int(year), 12, 31)
        elif duration == ['H1', 'h1']:
            return date(int(year), 1, 1), date(int(year), 6, 30)
        else:
            return date(int(year), 7, 1), date(int(year), 12, 31)
        

    def create(self, validated_data):
        #處理 duration，若找不到 duration自動產生
        #Duration.objects.create(name='2016.Q1', start_date=date(2016,1,1), end_date=date(2016,3,31))
        duration_data = validated_data.pop('current_duration', None)#把這取出來是因型態不對，傳進來是字串我們自行處理
        duration = None
        if duration_data:
            try:
                duration = Duration.objects.get(name=duration_data)
            except Duration.DoesNotExist:
                s, e = EmployeeSerializer.make_time_tuple(duration_data)
                print('Create a new one duration object : {}'.format(duration_data))
                duration = Duration.objects.create(name=duration_data, start_date=s, end_date=e)
            except Duration.MultipleObjectsReturned:
                print('should not go here [create] 001')
        #處理 user，若找不到自動產生
        user_dic_data = validated_data.pop('user', None)
        if user_dic_data:
            try:
                u = User.objects.get(username=user_dic_data['username'])
            except User.DoesNotExist:
                print('Create a new User object : {}'.format(user_dic_data['username']))
                u = User.objects.create(**user_dic_data)
                u.set_password(user_dic_data['password'])
                u.save()
            except User.MultipleObjectsReturned:
                print('should not go here [create] 002')
        #處理 addition_employees, 要先取出這額外資料才能把剩下的 validated_data 拿去寫 model
        addition_employees_list = validated_data.pop('addition_employees', [])
        print('Create a new Employee object : {}'.format(user_dic_data['username']))
        employee = Employee.objects.create(owner=u, current_duration=duration, **validated_data) #最外層的 employee：他的 manager已在view的perform_create處理過了
        
        for item in addition_employees_list:
            # 一樣先處理 duration
            dd = item.pop('current_duration', None)
            if dd:
                try:
                    duration = Duration.objects.get(name=dd)
                except Duration.DoesNotExist:
                    s, e = EmployeeSerializer.make_time_tuple(dd)
                    print('Create a new one duration object for {}'.format(dd))
                    duration = Duration.objects.create(name=dd, start_date=s, end_date=e)
                except Duration.MultipleObjectsReturned:
                    print('should not go here [create] 003')
            # 再處理 user
            udd = item.pop('user', None)
            if udd:
                try:
                    u = User.objects.get(username=udd['username'])
                except User.DoesNotExist:
                    print('2nd layer, Create a new User object : {}'.format(udd['username']))
                    u = User.objects.create(**udd)
                    u.set_password(udd['password'])
                    u.save()
                except User.MultipleObjectsReturned:
                    print('should not go here [create] 004')
            # 再處理 manager
            mgr_string = item.pop('manager', None)
            m = None
            if mgr_string:
                try:
                    m = User.objects.get(username=mgr_string)
                except User.DoesNotExist:
                    raise serializers.ValidationError('Cannot find manager {} user object'.format(m))
                except User.MultipleObjectsReturned:
                    print('should not go here [create] 005')
                    raise serializers.ValidationError('should not go here [create] 005')
            print('2nd layer, Create a new Employee object : {}'.format(udd['username']))
            employee = Employee.objects.create(owner=u, current_duration=duration, manager=m, **item)
        return employee

    def update(self, instance, validated_data):
        print('update begin from here')
        #kpi_state = 'edit' # 只要有進到這就視為 edit 狀態
        #若最外層有提供duration則以它為預設值 2016.Q3
        #處理 duration，若找不到 duration自動產生
        #Duration.objects.create(name='2016.Q1', start_date=date(2016,1,1), end_date=date(2016,3,31))
        duration_data = validated_data.pop('current_duration', None)#把這取出來是因型態不對，傳進來是字串我們自行處理
        duration = None
        if duration_data:
            try:
                duration = Duration.objects.get(name=duration_data)
            except Duration.DoesNotExist:
                s, e = EmployeeSerializer.make_time_tuple(duration_data)
                print('Create a new one duration object for {}'.format(duration_data))
                duration = Duration.objects.create(name=duration_data, start_date=s, end_date=e)
            except Duration.MultipleObjectsReturned:
                    print('should not go here [update] 001')
        # 找 employee_number對應的user obj (叫前端不要送owner好了)
        # 處理關聯 owner (此時一定有 employee_number 所指定的 employee obj，retro的話則可能有可能沒有
        kpi_employee = Employee.objects.get(employee_number=validated_data['employee_number']) # 受評者
        duration = duration if duration else kpi_employee.current_duration
        print('受評者:{}, 期間:{}'.format(kpi_employee, duration))

        #把 retro 拿出來，先找到它的 owner
        retros_dict = validated_data.pop('retros', [])
        if retros_dict:
            for oneRetro in retros_dict:
                evaluation_dict = oneRetro.pop('evaluation', None) # 把 oneRetro 字典中 evaluation 的部份抽出來
                retro = None
                try:
                    print('總 retro 數量:{}'.format(Retrospective.objects.all().count()))
                    retro = Retrospective.objects.filter(current_duration=duration).get(owner=kpi_employee)
                    r = Retrospective.objects.filter(current_duration=duration).filter(owner=kpi_employee).update(**oneRetro) #
                    print('順利更新後總 retro 筆數:{}，更新 {} 筆，此owner當期筆數:{}'.format(Retrospective.objects.all().count(), r, Retrospective.objects.filter(current_duration=duration).filter(owner=kpi_employee).count()))
                except Retrospective.DoesNotExist:
                    print('找不到，產生新retro owner:{}'.format(kpi_employee))
                    print('產生前總 retro:{} 筆'.format(Retrospective.objects.all().count()))
                    retro = Retrospective.objects.create(owner=kpi_employee, current_duration=duration, **oneRetro)
                    print('產生後總 retro:{} 筆'.format(Retrospective.objects.all().count()))
                except Retrospective.MultipleObjectsReturned:
                    print('should not go here [update] 002')
                    raise serializers.ValidationError('should not go here [update] 002')
                # 接下來處理它的兒子，Evaluation
                if evaluation_dict:
                    eval_by = evaluation_dict.pop('eval_by', None) # 把 evaluation_dict字典中 eval_by 的部份抽出來
                    eval_by = Employee.objects.get(employee_number=eval_by)
                    # 生成新的 Evaluation obj 但要處理兩個 fk: eval_by, retro 以及 type
                    #若retro_dict['wentwell_myself'] =>自評；'wentwell_review' =>主管評分；'wentwell_approval' => 核准
                    #若evaluation_dict['comment'] => 諮詢； 若上面都沒有只有分數，就是「邀請評分」
                    retro_type = '邀請評分'
                    if 'wentwell_myself' in oneRetro:
                        retro_type = '自評'
                        #kpi_state = 'employee_submit'
                    elif 'wentwell_review' in oneRetro:
                        retro_type = '主管評分'
                    elif 'wentwell_approval' in oneRetro:
                        retro_type = '核准'
                    elif 'comment' in evaluation_dict:
                        retro_type = '諮詢'
                    try:
                        print('先get看看該筆retro是否這個評分者{}的記錄存在'.format(eval_by))
                        e = retro.evaluation.get(eval_by=eval_by)
                        if 'score' in evaluation_dict and retro_type == '邀請評分':
                            print('找到，且有帶score且為邀請評分，把done=True')
                            r = retro.evaluation.filter(eval_by=eval_by).update(done=True, **evaluation_dict)
                        else:
                            print('找到，當作更新')
                            r = retro.evaluation.filter(eval_by=eval_by).update(**evaluation_dict)
                        print('retro.evaluation成功更新 {} 筆'.format(r))
                    except Evaluation.DoesNotExist:
                        print('找不到，生一筆 Evaluation 物件給 {} 的 retro，且 done=True，type:{}'.format(kpi_employee, retro_type))
                        print('產生前總 Evaluation {} 筆'.format(Evaluation.objects.all().count()))
                        e = Evaluation.objects.create(eval_by=eval_by, retro=retro, done=True, type=retro_type, **evaluation_dict)#有資料所以done=True
                        print('產生後總 Evaluation {} 筆'.format(Evaluation.objects.all().count()))
                    except Evaluation.MultipleObjectsReturned:
                        print('should not go here [update] 003')
                        raise serializers.ValidationError('should not go here [update] 003')

        #把 prls 拿出來, 這邊跟 retro 的處理不一樣，要先把舊的通通刪掉
        prls_list = validated_data.pop('prls', [])
        if prls_list:
            print('原先 {} 的當期 PRL 有 {} 筆'.format(kpi_employee, ProfessionReadinessLevel.objects.filter(owner=kpi_employee, current_duration=duration).count()))
            r = ProfessionReadinessLevel.objects.filter(owner=kpi_employee, current_duration=duration).delete()
            print('清除結果 {} 通通清除後剩 {} 筆'.format(r, ProfessionReadinessLevel.objects.filter(owner=kpi_employee, current_duration=duration).count()))
            # 用個 for 迴圈處理，並生成 prl 物件
            for onePRL in prls_list:
                # 還要處理它的 fk： owner, duration
                print('產生一筆 PRL objects 給 {}'.format(kpi_employee))
                ProfessionReadinessLevel.objects.create(owner=kpi_employee, current_duration=duration, **onePRL)
            print('現在 {} 的當期 PRL 有 {} 筆'.format(kpi_employee, ProfessionReadinessLevel.objects.filter(owner=kpi_employee, current_duration=duration).count()))

        #把邀請評分新增的兩個拿出來
        reviewer = validated_data.pop('reviewer', None) # User object
        mail_list = validated_data.pop('mail_list', []) # User object list
        if mail_list:
            #拿出來後替他們建立 Evaluation object，但要小心可能不要總是用 create (也許被邀請人會有保存動作)
            for invited_mgr in mail_list:
                # 得到受評者該期的 retrospective
                retro = Retrospective.objects.filter(current_duration=duration).get(owner=kpi_employee)
                invited_evaluation = None
                try:
                    # 先看看它這個 retro 裡是否已被 invited_mgr 評過，所以先把它過慮出來
                    invited_evaluation = retro.evaluation.get(eval_by=invited_mgr.employee.get())
                    # 如果有的話再，代表可能這封邀請信是重複發送了，印個訊息就好
                    print('The invited manager () already has a record on Evaluation table'.format(invited_mgr))
                    #r = Evaluation.objects.filter(eval_by=invited_mgr.employee).update(**SOME_DICT)
                except Evaluation.DoesNotExist:
                    print('Create a new Evaluation objects for invited_mgr:{}, retro owner:{}'.format(invited_mgr.username, kpi_employee))
                    invited_evaluation = Evaluation.objects.create(eval_by=invited_mgr.employee.get(), retro=retro, done=False, type='邀請評分') # 此時沒有score/comment
                except Evaluation.MultipleObjectsReturned:
                    print('should not go here [update] 004')
                    raise serializers.ValidationError('should not go here [update] 004')


        #從 validated_data 取出要更新的資料再寫到原本
        instance.kpi_state = validated_data.get('kpi_state', instance.kpi_state)#後端自行處理
        instance.manager = validated_data.get('manager', instance.manager)
        if duration:
            instance.current_duration = duration
        instance.save() # serializer.save() 會到 model.save()
        return instance



