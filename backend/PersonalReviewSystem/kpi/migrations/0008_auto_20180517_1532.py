# Generated by Django 2.0.5 on 2018-05-17 07:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kpi', '0007_employee_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='academic_degree',
            field=models.CharField(choices=[('博士', '博士'), ('碩士', '碩士'), ('學士', '學士'), ('專科', '專科')], default='專科', max_length=10),
        ),
        migrations.AddField(
            model_name='employee',
            name='department',
            field=models.CharField(choices=[('大數據研發處(BDL)', '大數據研發處(BDL)'), ('數據工程處(DED)', '數據工程處(DED)'), ('專利雲開發處(PCDD)', '專利雲開發處(PCDD)'), ('智慧財產軟體企劃處(IPSPD)', '智慧財產軟體企劃處(IPSPD)'), ('智慧財產交易平台處(IPEXD)', '智慧財產交易平台處(IPEXD)'), ('投資營運系統處(INCD)', '投資營運系統處(INCD)'), ('技術資產營運系統處(IACD)', '技術資產營運系統處(IACD)'), ('軟體事業群 Ⅱ 開發處(SBG2DD)', '軟體事業群 Ⅱ 開發處(SBG2DD)'), ('UI/UX/GUI設計處(UUGD)', 'UI/UX/GUI設計處(UUGD)'), ('商務發展處(BDD)', '商務發展處(BDD)'), ('數位服務處(DSD)', '數位服務處(DSD)'), ('產品服務維運處(DOD)', '產品服務維運處(DOD)'), ('雲端架構與資安處(CASD)', '雲端架構與資安處(CASD)'), ('財會租稅處(FAT)', '財會租稅處(FAT)'), ('人力運營處(POD)', '人力運營處(POD)'), ('服務支援處(SSD)', '服務支援處(SSD)')], default='服務支援處(SSD)', max_length=256),
        ),
        migrations.AddField(
            model_name='employee',
            name='job_level',
            field=models.CharField(choices=[('S5', 'S5'), ('S4', 'S4'), ('S3', 'S3'), ('S2', 'S2'), ('S1', 'S1'), ('C3', 'C3'), ('C2', 'C2'), ('C1', 'C1'), ('A3', 'A3'), ('A2', 'A2'), ('A1', 'A1')], default='A1', max_length=10),
        ),
        migrations.AddField(
            model_name='employee',
            name='job_title',
            field=models.CharField(choices=[('董事長', '董事長'), ('執行長', '執行長'), ('財務長', '財務長'), ('總經理', '總經理'), ('副總經理', '副總經理'), ('高級顧問', '高級顧問'), ('顧問', '顧問'), ('資深協理', '資深協理'), ('協理', '協理'), ('總監', '總監'), ('資深經理', '資深經理'), ('經理', '經理'), ('資深工程師', '資深工程師'), ('高級工程師', '高級工程師'), ('工程師', '工程師'), ('助理工程師', '助理工程師'), ('秘書', '秘書'), ('', '')], default='秘書', max_length=100),
        ),
        migrations.AddField(
            model_name='employee',
            name='kpi_state',
            field=models.CharField(choices=[('ready', 'ready'), ('open', 'open'), ('edit', 'edit'), ('employee_submit', 'employee_submit'), ('manager_feedback', 'manager_feedback'), ('manager_submit', 'manager_submit'), ('hr_confirm', 'hr_confirm'), ('ceo_feedback', 'ceo_feedback'), ('finish', 'finish')], default='ready', max_length=30),
        ),
        migrations.AddField(
            model_name='employee',
            name='onboard_date',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='employee',
            name='school',
            field=models.CharField(choices=[('台灣大學', '台灣大學'), ('清華大學', '清華大學'), ('交通大學', '交通大學'), ('成功大學', '成功大學')], default='交通大學', max_length=30),
        ),
        migrations.AddField(
            model_name='employee',
            name='school_major',
            field=models.CharField(choices=[('資訊工程', '資訊工程'), ('環境工程', '環境工程'), ('土木工程', '土木工程'), ('化學工程', '化學工程')], default='資訊工程', max_length=30),
        ),
    ]
