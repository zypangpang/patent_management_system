import csv,bisect
from django.db.models import Q
from django.shortcuts import render
from .models import Nation,Applicant,FamilyFatent,Patent
from .PatentForm import PatentForm

from django.http import HttpResponse
PATENT_TYPES=('不确定',
        '发明申请',
        '发明授权',
        '实用新型',
        '外观设计', )
#PATENT_TYPE_DICT_REVERSE={0:'不确定',
#        1:'发明申请',
#        2:'发明授权',
#        3:'实用新型',
#        4:'外观设计',}
def find(a, x):
    'Locate the leftmost value exactly equal to x'
    i = bisect.bisect_left(a, x)
    if i != len(a) and a[i] == x:
        return i
    raise -1
def add_patent_from_row(row,pdf_file):
    applicants,nations=add_applicants_and_nations(row['申请人'], row['同族国家'])
    p=Patent(title=row['标题'],title_cn=row['标题（翻译）'],abstract=row['摘要'],
                     abstract_cn=row['摘要（翻译）'],index=row['标引'],branch1=row['一级分支'],
                     branch2=row['二级分支'],branch3=row['三级分支'],invent_desc=row['发明点'],
                     tech_prob=row['技术问题'],pub_id=row['公开（公告）号'],pub_date=row['公开（公告）日'].replace('/','-'),
                     application_id=row['申请号'],application_date=row['申请日'].replace('/','-'),
                   patent_type=row['专利类型'],cat_id=row['主分类号'],pdf_file=pdf_file)
    p.save()
    for applicant in applicants:
        p.applicants.add(applicant)
    for nation in nations:
        p.nations.add(nation)
    add_same_family_patents(p,row['简单同族'])


def add_patents_from_csv_and_pdfs(csv_file,pdf_files):
    error_messages=[]

    f_csv = csv.DictReader(csv_file)

    pdf_files.sort(key=lambda file: file.name)
    pdf_names=[f.name for f in pdf_files]
    for row in f_csv:
        pub_id=row['公开（公告）号']
        t=find(pdf_names,pub_id+'.pdf')
        print(pdf_files[t].name)
        if t!=-1:
            add_patent_from_row(row,pdf_files[t])

            ####### 此处正式应用时删除###########
            break
            ###########################
        else:
            error_messages.append(pub_id+" no file!")

    return error_messages

def add_same_family_patents(patent,same_family_str):
    same_family_patents=same_family_str.split(';')
    for sfpatent in same_family_patents:
        sfpatent=sfpatent.strip()
        try:
            FamilyFatent(patent=patent, same_family_patent=sfpatent).save()
        except Exception as e:
            print(e)

def add_applicants_and_nations(applicant_str, nation_str):
    applicants=applicant_str.split(';')
    applicant_list=[]
    nation_list=[]
    for applicant in applicants:
        a=applicant.strip()
        obj,created=Applicant.objects.get_or_create(name=a)
        applicant_list.append(obj)

    nations=nation_str.split(',')
    for nation in nations:
        nation=nation.strip()
        obj,created=Nation.objects.get_or_create(name=nation)
        nation_list.append(obj)

    return applicant_list,nation_list

def index(request):
    return HttpResponse("hello")

def add_data(request):
    if request.method=='POST':
        #form=PatentForm(request.POST,request.FILES)
        add_patent_from_row(request.POST,request.FILES['pdf_file'])
        return HttpResponse("save successful")
        '''if form.is_valid():
            patent=form.save()
            print(request.POST['same_family_patent'])
            add_applicants_and_nations(patent, request.POST['applicant'], request.POST['same_family_patent'],
                                       request.POST['nation'])
            return HttpResponse("save successful")
        else:
            print(form.errors)
            return HttpResponse("form not valid")'''
    else:
        return render(request,'main/index.html', {'patent_types':PATENT_TYPES})

def import_data(request):
    if request.method=='POST':
        csv_file=request.FILES['csv_file']
        file_utf8=csv_file.read().decode('utf-8').splitlines()
        files=request.FILES.getlist('pdf_files')
        errors=add_patents_from_csv_and_pdfs(file_utf8,files)
        #for f in files:
        #    print(f.name)
            #test_file=file_test(name='hello',file=f)
            #test_file.save()
        if errors:
            return HttpResponse('\n'.join(errors))
        return HttpResponse('success')

    else:
        return render(request,'main/import.html')

QUERY_FIELDS=(
    ('title','标题'),('title_cn','标题（翻译）'),('abstract','摘要'),
    ('abstract_cn','摘要（翻译）'),('index','标引'),('branch1','一级分支'),('branch2','二级分支'),
    ('branch3','三级分支'),('invent_desc','发明点'),('tech_prob','技术问题'),('pub_id','公开（公告）号'),
    ('pub_date','公开（公告）日'),('application_id','申请号'),
    ('application_date','申请日'),('applicants__name','申请人'),('patent_type','专利类型'),
    ('cat_id','主分类号'),('nations__name','同族国家'),
)
SHOW_FIELDS=('标题','标题（翻译）','公开号','公开（公告）日','申请号','申请日','申请人','专利类型')
def query_data(request):
    if request.method=='POST':

        query_field_count=request.POST['field_count']
        QObject=Q()
        for i in range(1,int(query_field_count)+1):
            query_field=request.POST['query_field_'+str(i)]
            query_text=request.POST['query_text_'+str(i)]
            #get or object
            if '|' in query_text:
                or_object=Q()
                or_texts=query_text.split('|')
                for text in or_texts:
                    or_object |= Q(**{query_field+'__icontains':text.strip()})
                QObject &= or_object
            else:
                QObject &=Q(**{query_field+'__icontains':query_text})
        query_raw_result=Patent.objects.filter(QObject).distinct()
        if len(query_raw_result)>100:
            query_raw_result=query_raw_result[:100]
        query_result=[]
        for item in query_raw_result:
            applicant_str=','.join([a.name for a in item.applicants.all()])
            #patent_type=PATENT_TYPE_DICT_REVERSE[item.patent_type]
            query_result.append([item.title,item.title_cn,item.pub_id,item.pub_date.strftime('%Y-%m-%d'),
                                 item.application_id,item.application_date.strftime('%Y-%m-%d'),applicant_str,
                                 item.patent_type])
        result_length=len(query_raw_result)
        result_count=str(result_length)
        if(result_length>100):
            result_count+=',只显示前100'

        #return render(request,'main/query.html',{'query_fields':QUERY_FIELDS,
        #                                         'query_result':query_result,
        #                                         'show_fields':SHOW_FIELDS})
        return render(request,'main/query_result_table.html',{'query_result':query_result,
                                                              'show_fields':SHOW_FIELDS,
                                                              'result_count':result_count})
    else:
        query_raw_result=Patent.objects.all()[:50]
        query_result=[]
        for item in query_raw_result:
            applicant_str=','.join([a.name for a in item.applicants.all()])
            #patent_type=PATENT_TYPE_DICT_REVERSE[item.patent_type]
            query_result.append([item.title,item.title_cn,item.pub_id,item.pub_date.strftime('%Y-%m-%d'),
                                 item.application_id,item.application_date.strftime('%Y-%m-%d'),applicant_str,
                                 item.patent_type])
        result_length=len(query_raw_result)
        result_count=str(result_length)
        if(result_length>100):
            result_count+=',只显示前100'
        return render(request,'main/query.html',{'query_fields':QUERY_FIELDS,
                                                 'show_fields':SHOW_FIELDS,
                                                 'result_count':result_count,
                                                 'query_result':query_result})

def show_data(request):
    return HttpResponse(request.GET['pub_id'])


# Create your views here.
