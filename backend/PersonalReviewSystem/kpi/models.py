from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings

# 使用參考 http://quke.org/post/django-model-choices.html
ROLE_CHOICES = [('待定', '待定'), ('工讀','工讀'), ('約聘','約聘'), ('正職','正職'), ('顧問','顧問'), ('留職停薪','留職停薪')]
# kpiState: open -> edit -> employee_submit -> manager_feedback -> (waiting_for_consult) -> manager_submit -> hr_confirm -> ceo_feedback -> finish
KPISTATE_CHOICES = [('ready','ready'), ('open','open'),('edit','edit'),('employee_submit','employee_submit'),('manager_feedback','manager_feedback'),('manager_submit','manager_submit'),
                    ('hr_confirm','hr_confirm'),('ceo_feedback','ceo_feedback'),('finish','finish')]
DEPARTMENT_CHOICES = [('大數據研發處(BDL)', '大數據研發處(BDL)'), ('數據工程處(DED)', '數據工程處(DED)'), ('專利雲開發處(PCDD)', '專利雲開發處(PCDD)'), 
                      ('智慧財產軟體企劃處(IPSPD)', '智慧財產軟體企劃處(IPSPD)'), ('智慧財產交易平台處(IPEXD)', '智慧財產交易平台處(IPEXD)'), 
                      ('投資營運系統處(INCD)', '投資營運系統處(INCD)'), ('技術資產營運系統處(IACD)', '技術資產營運系統處(IACD)'), 
                      ('軟體事業群 Ⅱ 開發處(SBG2DD)', '軟體事業群 Ⅱ 開發處(SBG2DD)'), ('UI/UX/GUI設計處(UUGD)', 'UI/UX/GUI設計處(UUGD)'), 
                      ('商務發展處(BDD)', '商務發展處(BDD)'), ('數位服務處(DSD)', '數位服務處(DSD)'), ('產品服務維運處(DOD)', '產品服務維運處(DOD)'), 
                      ('雲端架構與資安處(CASD)', '雲端架構與資安處(CASD)'), ('財會租稅處(FAT)', '財會租稅處(FAT)'), ('人力運營處(POD)', '人力運營處(POD)'), 
                      ('服務支援處(SSD)', '服務支援處(SSD)')]
JOBTITLE_CHOICES = [('董事長', '董事長'), ('執行長', '執行長'), ('財務長', '財務長'), ('總經理', '總經理'), ('副總經理', '副總經理'), ('高級顧問', '高級顧問'), 
                    ('顧問', '顧問'), ('資深協理', '資深協理'), ('協理', '協理'), ('總監', '總監'), ('資深經理', '資深經理'), ('經理', '經理'), 
                    ('資深工程師', '資深工程師'), ('高級工程師', '高級工程師'), ('工程師', '工程師'), ('助理工程師', '助理工程師'), ('秘書', '秘書'), ('', ''), ]
JOBLEVEL_CHOICES = [('S5', 'S5'), ('S4', 'S4'), ('S3', 'S3'), ('S2', 'S2'), ('S1', 'S1'), ('C3', 'C3'), ('C2', 'C2'), ('C1', 'C1'), ('A3', 'A3'), ('A2', 'A2'), ('A1', 'A1')]
SCHOOL_CHOICES = [('台灣大學', '台灣大學'), ('清華大學', '清華大學'), ('交通大學', '交通大學'), ('成功大學', '成功大學')]
ACADEMIC_DEGREE_CHOICES = [('博士', '博士'), ('碩士', '碩士'), ('學士', '學士'), ('專科', '專科')]
SCHOOLMAJOR_CHOICES = [('資訊工程', '資訊工程'), ('環境工程', '環境工程'), ('土木工程', '土木工程'), ('化學工程', '化學工程')]
SCORE_CHOICES = [('0', '0'), ('0.1', '0.1'), ('0.2', '0.2'), ('0.3', '0.3'), ('0.4', '0.4'), ('0.5', '0.5'), ('0.6', '0.6'), ('0.7', '0.7'), ('0.8', '0.8'), 
                 ('0.9', '0.9'), ('1.0', '1.0'), ('1.1', '1.1'), ('1.2', '1.2'), ('1.3', '1.3'), ('1.4', '1.4'), ('1.5', '1.5'), ('1.6', '1.6'), 
                 ('1.7', '1.7'), ('1.8', '1.8'), ('1.9', '1.9'), ('2.0', '2.0'), ]
EVALUATION_TYPE_CHOICES = [('自評', '自評'), ('邀請評分', '邀請評分'), ('諮詢', '諮詢'), ('主管評分', '主管評分'), ('核准', '核准'),]
#DEPARTMENT_CHOICES = [('', ''), ('', ''), ('', ''), ('', ''), ('', ''), ('', ''), ('', ''), ('', ''), ('', ''), ('', ''), ('', ''), ('', ''), ('', ''), ]

# Create your models here.
# This code is triggered whenever a new user has been created and saved to the database
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

class Duration(models.Model):
    name = models.CharField(max_length=30)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    
    def __str__(self):
        return self.name

    #def get_items_between_duration(start, end):
    #    queryset = Duration.objects.order_by('start_date').filter(star_date__gte=start).filter(end_date__lt=end)
    #    print('Duration model get item between date result:', queryset.count())
    #    return queryset

class Employee(models.Model):
    level = 1
    #created = models.DateTimeField(auto_now_add=True)
    employee_number = models.CharField(max_length=10, unique=True)
    ad_account = models.CharField(max_length=30)
    role = models.CharField(choices=ROLE_CHOICES, default='待定', max_length=10, help_text=_("CHOICE default 待定"))
    kpi_state = models.CharField(choices=KPISTATE_CHOICES, default='ready', max_length=30, help_text=_("CHOICE default ready"))
    department = models.CharField(choices=DEPARTMENT_CHOICES, default='服務支援處(SSD)', max_length=256, help_text=_("CHOICE default 服務支援處"))
    job_title = models.CharField(choices=JOBTITLE_CHOICES, default='秘書', max_length=100, help_text=_("CHOICE default 秘書"))
    job_level = models.CharField(choices=JOBLEVEL_CHOICES, default='A1', max_length=10, help_text=_("CHOICE default A1"))
    school = models.CharField(choices=SCHOOL_CHOICES, default='交通大學', max_length=30, help_text=_("CHOICE default 交通大學"))
    school_major = models.CharField(choices=SCHOOLMAJOR_CHOICES, default='資訊工程', max_length=30, help_text=_("CHOICE default 資訊工程"))
    academic_degree = models.CharField(choices=ACADEMIC_DEGREE_CHOICES, default='專科', max_length=10, help_text=_("CHOICE default 專科"))
    onboard_date = models.DateField(null=True)
    # foreign key relationships
    current_duration = models.ForeignKey(Duration, related_name='employee', null=True, on_delete=models.CASCADE)
    owner = models.ForeignKey('auth.User', related_name='employee', on_delete=models.CASCADE) # 或這樣寫 models.OneToOneField(User, on_delete=models.CASCADE)
    manager = models.ForeignKey('auth.User', related_name='managee', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.owner.username

    @classmethod
    def traverse(self, user):
        name_list = []
        print('#' * Employee.level + user.username)
        name_list.append(user.username)
        for member in user.managee.all():
            Employee.level += 1
            name_list.extend(Employee.traverse(member.owner))
            Employee.level -= 1
        return name_list

    def get_members(self):
        """Get the members of one Employee"""
        # 要拿self所管的如下，managees = self.owner.managee.all()

        if self.owner.managee.count == 0:
            print('{} has no any member.'.format(self))
            return []
        #setattr(Employee.traverse, "level", 1) #Employee.traverse.level = 1
        Employee.level = 1
        return Employee.traverse(self.owner) # User object
        #delattr(Employee.traverse, "level")

    def is_member_of(self, anEmployee):
        """Determine if self is a member of anEmployee"""
        if not self.manager or self.employee_number == anEmployee.employee_number:
            return False
        if self.manager.id == anEmployee.owner.id:
            return True
        try:
            supervisor = User.objects.get(pk=self.manager.id) # 拿到主管的 User Object
        except User.DoesNotExist:
            print('Employee exception User.DoesNotExist id:', self.manager.id)
            supervisor = None
        while supervisor:
            if supervisor.id == anEmployee.owner.id: # 用 User Object 的 id 比較
                return True
            # 繼續往上找 self.manager.manager 去跟 anEmployee比
            # supervisor.employee 是 'RelatedManager' 原因 https://stackoverflow.com/questions/1823880/relatedmanager-object-has-no-attribute
            supervisor_employ = supervisor.employee.get() # now its type is really Employ model
            if not supervisor_employ.manager:
                return False
            supervisor = User.objects.get(pk=supervisor_employ.manager.id) #supervisor.employee.manager ===> error: 'RelatedManager' object has no attribute 'manager'
        return False

class ProfessionReadinessLevel(models.Model):
    prl = models.CharField(max_length=256)
    status = models.CharField(max_length=256)
    supervisor_feedback = models.CharField(max_length=256)
    # foreign key relationships
    owner = models.ForeignKey(Employee, related_name='profession_readiness_level', on_delete=models.CASCADE)
    current_duration = models.ForeignKey(Duration, related_name='profession_readiness_level', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.owner.owner.username

class Retrospective(models.Model):
    wentwell_myself = models.TextField(blank=True)
    wentwell_review = models.TextField(blank=True)
    wentwell_invite = models.TextField(blank=True)
    wentwell_approval = models.TextField(blank=True)
    improve_myself = models.TextField(blank=True)
    improve_review = models.TextField(blank=True)
    improve_approval = models.TextField(blank=True)
    support = models.CharField(max_length=100, blank=True)#models.ForeignKey(Employee, related_name='support', on_delete=models.CASCADE, blank=True, null=True)
    support_reason = models.TextField(blank=True)
    inspire = models.CharField(max_length=100, blank=True)
    inspire_reason = models.TextField(blank=True)
    metrics = models.TextField(blank=True)
    # OKRs
    okr_contribution_score = models.CharField(max_length=20, default='50')
    okr_contribution_proportion = models.CharField(max_length=20, default='50/300')
    okr_cumulative_score = models.CharField(max_length=20, default='50/300')
    #score 參考到外部 Evaluation
    owner = models.ForeignKey(Employee, related_name='retrospective', on_delete=models.CASCADE)
    current_duration = models.ForeignKey(Duration, related_name='retrospective', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.owner.owner.username

class Evaluation(models.Model):
    score = models.FloatField(default=0.0)
    comment = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True) # read only field
    date_modified = models.DateTimeField(auto_now=True)    # read only field
    type = models.CharField(choices=EVALUATION_TYPE_CHOICES, default='不明', max_length=30)
    done = models.BooleanField(default=0)
    eval_by = models.ForeignKey(Employee, related_name='evaluation', on_delete=models.CASCADE)    # reverse: Employee.evaluation
    retro = models.ForeignKey(Retrospective, related_name='evaluation', on_delete=models.CASCADE) # reverse: Retrospective.evaluation

    def __str__(self):
            return self.retro.owner.owner.username
    
