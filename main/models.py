import datetime
from django.db import models

def pdf_directory_path(instance,filename):
    year=datetime.datetime.strptime(instance.pub_date,"%Y-%m-%d").year
    return f'patent_pdf/{year}/{instance.pub_id}.pdf'
#def test_dir_path(instance,filename):
#    return f'test_pdf/{instance.name}.pdf'

class Applicant(models.Model):
    name=models.CharField(max_length=50,primary_key=True)

class Nation(models.Model):
    name=models.CharField(max_length=5,primary_key=True)

class Patent(models.Model):
    #PATENT_TYPES=(
    #    (0,'不确定'),
    #    (1,'发明申请'),
    #    (2,'发明授权'),
    #    (3,'实用新型'),
    #    (4,'外观设计'),
    #)
    title = models.TextField()
    title_cn=models.TextField()
    abstract=models.TextField()
    abstract_cn=models.TextField()
    index=models.CharField(max_length=60)

    pub_id=models.CharField(max_length=20,primary_key=True)
    pub_date = models.DateField('date published')
    application_id=models.CharField(max_length=20,unique=True)
    application_date=models.DateField()
    patent_type=models.CharField(max_length=40)

    cat_id=models.CharField(max_length=50,blank=True)
    branch1=models.CharField(max_length=60,blank=True)
    branch2=models.CharField(max_length=60,blank=True)
    branch3=models.CharField(max_length=60,blank=True)
    invent_desc=models.CharField(max_length=200,blank=True)
    tech_prob=models.CharField(max_length=200,blank=True)

    applicants=models.ManyToManyField(Applicant)
    nations=models.ManyToManyField(Nation)
    pdf_file=models.FileField(upload_to=pdf_directory_path)


#class apply_patent(models.Model):
#    patent = models.ForeignKey(Patent, on_delete=models.CASCADE)
#    applicant=models.CharField(max_length=50)

class FamilyFatent(models.Model):
    patent = models.ForeignKey(Patent, on_delete=models.CASCADE)
    same_family_patent=models.CharField(max_length=20)

# nation should have choices
#class family_nation(models.Model):
#    patent = models.ForeignKey(Patent, on_delete=models.CASCADE)
#    nation= models.CharField(max_length=5)



#class file_test(models.Model):
#    name=models.CharField(max_length=100)
#    file=models.FileField(upload_to=test_dir_path)



# Create your models here.
