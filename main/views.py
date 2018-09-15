import csv,bisect,json
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render,redirect,reverse
from .models import Nation,Applicant,FamilyFatent,Patent,Note
from django.contrib.auth.decorators import login_required

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
def add_patent_from_row(zh_cn,row,request_files):
    if zh_cn:
        applicants,nations=add_applicants_and_nations(row['申请人'], row['同族国家'])
        p=Patent(title=row['标题'],title_cn=row['标题（翻译）'],abstract=row['摘要'],
                         abstract_cn=row['摘要（翻译）'],index=row['标引'],branch1=row['一级分支'],
                         branch2=row['二级分支'],branch3=row['三级分支'],invent_desc=row['发明点'],
                         tech_prob=row['技术问题'],pub_id=row['公开（公告）号'],pub_date=row['公开（公告）日'].replace('/','-'),
                         application_id=row['申请号'],application_date=row['申请日'].replace('/','-'),
                       patent_type=row['专利类型'],cat_id=row['主分类号'])
    else:
        applicants,nations=add_applicants_and_nations(row['applicants'], row['nations'])
        p=Patent(title=row['title'],title_cn=row['title_cn'],abstract=row['abstract'],
                         abstract_cn=row['abstract_cn'],index=row['index'],branch1=row['branch1'],
                         branch2=row['branch2'],branch3=row['branch3'],invent_desc=row['invent_desc'],
                         tech_prob=row['tech_prob'],pub_id=row['pub_id'],pub_date=row['pub_date'].replace('/','-'),
                         application_id=row['application_id'],application_date=row['application_date'].replace('/','-'),
                       patent_type=row['patent_type'],cat_id=row['cat_id'],pdf_file=request_files['pdf_file'])
    #if request_files:
    #    p.pdf_file=request_files['pdf_file']
    p.save()
    for applicant in applicants:
        p.applicants.add(applicant)
    for nation in nations:
        p.nations.add(nation)
    if(zh_cn):
        add_same_family_patents(p,row['简单同族'])
    else:
        add_same_family_patents(p,row['same_family_patent'])


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
            add_patent_from_row(True,row,pdf_files[t])

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

@login_required
def index(request):
    return redirect(reverse('main:query'))

@login_required
def add_data(request):
    if request.method=='POST':
        #form=PatentForm(request.POST,request.FILES)
        #1 for success 2 for failure 0 for default
        message='添加成功'
        try:
            add_patent_from_row(False,request.POST,request.FILES)
        except Exception as e:
            print(e)
            message='添加失败'
        return render(request, 'main/add.html', {'patent_types':PATENT_TYPES,
                                                 'user_name':request.user.get_username(),
                                                 'message':message})
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
        return render(request, 'main/add.html', {'patent_types':PATENT_TYPES,
                                                 'user_name':request.user.get_username(),
                                                 'message':''})

@login_required
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
            return render(request,'main/show_message.html',{'message':'\n'.join(errors),
                                                            'success':0})

        return render(request,'main/show_message.html',{'message':'数据导入成功',
                                                        'success':1})

    else:
        return render(request,'main/import.html',{
            'user_name':request.user.get_username(),
        })

QUERY_FIELDS=(
    ('title','标题'),('title_cn','标题（翻译）'),('abstract','摘要'),
    ('abstract_cn','摘要（翻译）'),('index','标引'),('branch1','一级分支'),('branch2','二级分支'),
    ('branch3','三级分支'),('invent_desc','发明点'),('tech_prob','技术问题'),('pub_id','公开（公告）号'),
    ('pub_date','公开（公告）日'),('application_id','申请号'),
    ('application_date','申请日'),('applicants__name','申请人'),('patent_type','专利类型'),
    ('cat_id','主分类号'),('nations__name','同族国家'),
)
SHOW_FIELDS=(('标题','20%'),('标题（翻译）','20%'),('公开号','10%'),
             ('公开（公告）日','10%'),('申请号','10%'),('申请日','10%'),('申请人','10%'),
             ('专利类型','10%'))
@login_required
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
            applicant_str=';'.join([a.name for a in item.applicants.all()])
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
                                                              'user_name':request.user.get_username(),
                                                              'show_fields':SHOW_FIELDS,
                                                              'result_count':result_count})
    else:
        query_raw_result=Patent.objects.all()[:50]
        query_result=[]
        for item in query_raw_result:
            applicant_str=';'.join([a.name for a in item.applicants.all()])
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
                                                 'user_name':request.user.get_username(),
                                                 'result_count':result_count,
                                                 'query_result':query_result})
@login_required
def change_data(request):
    pub_id=request.POST['pub_id']
    p=Patent.objects.get(pk=pub_id)

    family_patents=FamilyFatent.objects.filter(patent=p)
    family_patents.delete()

    row=request.POST
    applicants,nations=add_applicants_and_nations(row['applicants'], row['nations'])

    p.title=row['title']
    p.title_cn=row['title_cn']
    p.abstract=row['abstract']
    p.abstract_cn=row['abstract_cn']
    p.index=row['index']
    p.branch1=row['branch1']
    p.branch2=row['branch2']
    p.branch3=row['branch3']
    p.invent_desc=row['invent_desc']
    p.tech_prob=row['tech_prob']
    p.pub_id=row['pub_id']
    p.pub_date=row['pub_date'].replace('/','-')
    p.application_id=row['application_id']
    p.application_date=row['application_date'].replace('/','-')
    p.patent_type=row['patent_type']
    p.cat_id=row['cat_id']
    #if request_files:
    #    p.pdf_file=request_files['pdf_file']
    p.save()

    p.applicants.clear()
    p.nations.clear()
    for applicant in applicants:
        p.applicants.add(applicant)
    for nation in nations:
        p.nations.add(nation)

    add_same_family_patents(p,row['same_family_patent'])

@login_required
def del_data(request):
    pub_id=request.POST['pub_id']
    return_dict={'success':1}
    try:
        patent=Patent.objects.get(pk=pub_id)
        patent.delete()
    except Exception as e:
        print(e)
        return_dict['success']=0

    return HttpResponse(json.dumps(return_dict))
def get_notes(user,patent):
    #print(user.groups.all())
    if user.has_perm('main.view_private_notes'):
        notes=Note.objects.filter(patent=patent)
    else:
        notes=Note.objects.filter(patent=patent,type=0) | \
              Note.objects.filter(patent=patent,user=user)
    return notes
@login_required
def show_data(request):
    if request.method=='POST':
        change_data(request)
        return render(request,'main/show_message.html',{'message':'数据修改成功',
                                                        'success':1})
    else:
        pub_id=request.GET['pub_id']
        try:
            patent=Patent.objects.get(pk=pub_id)
        except Exception as e:
            print(e)
            return render(request,'main/show_message.html',
                          {'message':'数据库中查不到本专利，请检查公开号',
                           'success':0})

        applicant_str=';'.join([a.name for a in patent.applicants.all()])
        nation_str=','.join([a.name for a in patent.nations.all()])
        family_patents=FamilyFatent.objects.filter(patent=patent)
        family_patent_str=';'.join([a.same_family_patent for a in family_patents])

        notes=get_notes(request.user,patent)
        return_dict={
            'item':patent,
            'applicant_str':applicant_str,
            'nation_str':nation_str,
            'family_patent_str':family_patent_str,
            'notes':notes,
            'user_name':request.user.get_username(),

            'patent_types':PATENT_TYPES,
            'note_types':NOTE_TYPE,
        }
        return render(request,'main/detail.html',return_dict)

@login_required
def view_file(request,pub_id):
    patent=Patent.objects.get(pk=pub_id)
    #print(patent.pdf_file.name)
    filename=''
    if patent.pdf_file:
        filename = patent.pdf_file.name.split('/')[-1]
        response = HttpResponse(patent.pdf_file, content_type='application/pdf')
    else:
        return render(request,'main/show_message.html',{'message':'该专利没有文件',
                                                        'success':0})
    #response['Content-Disposition'] = 'attachment; filename=%s' % filename

    return response
NOTE_TYPE=(
    (0,'公有'),
    (1,'私有'),
)
def add_notes(request):
    user=request.user
    note=request.POST['note']
    type=request.POST['note_type']
    pub_id=request.POST['patent_id']
    try:
        Note.objects.create(patent_id=pub_id,user=user,note=note,type=type)
    except Exception as e:
        print(e)
        return render(request,'main/show_message.html',{'message':'添加批注失败',
                                                        'success':0})
    return redirect(reverse("main:detail")+'?pub_id='+pub_id)

# Create your views here.
