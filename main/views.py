import csv,bisect,json,logging
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.shortcuts import render,redirect,reverse
from .models import Nation,Applicant,FamilyFatent,Patent,Note
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse

logger=logging.getLogger(__name__)
PAGE_SIZE=10
PATENT_TYPES=('不确定',
        '发明申请',
        '发明授权',
        '实用新型',
        '外观设计', )
FILE_CACHE_DIR='patent_cache/'
#PATENT_TYPE_DICT_REVERSE={0:'不确定',
#        1:'发明申请',
#        2:'发明授权',
#        3:'实用新型',
#        4:'外观设计',}
def log_and_print(msg):
    logger.info(msg)
    print(msg)

def find(a, x):
    'Locate the leftmost value exactly equal to x'
    i = bisect.bisect_left(a, x)
    if i != len(a) and a[i] == x:
        return i
    return -1

def add_patent_from_csv_row(row,pdf_file):
    #error_id=''
    #pdf_path=settings.MEDIA_ROOT+FILE_CACHE_DIR+row['公开（公告）号']+'.pdf'
    p=None
    try:
        p=Patent(title=row['标题'],title_cn=row['标题（翻译）'],abstract=row['摘要'],
                     abstract_cn=row['摘要（翻译）'],index=row['标引'],branch1=row['一级分支'],
                     branch2=row['二级分支'],branch3=row['三级分支'],invent_desc=row['发明点'],
                     tech_prob=row['技术问题'],pub_id=row['公开（公告）号'],pub_date=row['公开（公告）日'].replace('/','-'),
                     application_id=row['申请号'],application_date=row['申请日'].replace('/','-'),
                     patent_type=row['专利类型'],law_state=row['法律状态'],
                     cat_id=row['主分类号'],pdf_file=pdf_file)
    except:
        p=Patent(title=row['标题'],title_cn=row['标题（翻译）'],abstract=row['摘要'],
                     abstract_cn=row['摘要（翻译）'],index=row['标引'],pub_id=row['公开（公告）号'],pub_date=row['公开（公告）日'].replace('/','-'),
                     application_id=row['申请号'],application_date=row['申请日'].replace('/','-'),
                   patent_type=row['专利类型'],cat_id=row['主分类号'],pdf_file=pdf_file)
    p.save()

    #codes below are for implementation 2
    #if pdf_file:
       # p.pdf_file=pdf_file
       # may raise exception
       # p.save()
    #else:
        # may raise exception
    #    f=open(pdf_path, 'rb')
    #    p.pdf_file=File(f)
    #    p.save()
    #    f.close()
    applicants,nations=add_applicants_and_nations(row['申请人'], row['同族国家'])

    #if request_files:
    #    p.pdf_file=request_files['pdf_file']

    for applicant in applicants:
        p.applicants.add(applicant)
    for nation in nations:
        p.nations.add(nation)

    add_same_family_patents(p,row['简单同族'])


def add_patent_from_row(row,pdf_file):
    #error_patents=[]

    p=Patent(title=row['title'],title_cn=row['title_cn'],abstract=row['abstract'],
                     abstract_cn=row['abstract_cn'],index=row['index'],branch1=row['branch1'],
                     branch2=row['branch2'],branch3=row['branch3'],invent_desc=row['invent_desc'],
                     tech_prob=row['tech_prob'],pub_id=row['pub_id'],pub_date=row['pub_date'],
                     law_state=row['law_state'],
                     application_id=row['application_id'],application_date=row['application_date'],
                   patent_type=row['patent_type'],cat_id=row['cat_id'],pdf_file=pdf_file)
    #if request_files:
    #    p.pdf_file=request_files['pdf_file']

    #may raise exception

    p.save()

    applicants,nations=add_applicants_and_nations(row['applicants'], row['nations'])

    for applicant in applicants:
        p.applicants.add(applicant)
    for nation in nations:
        p.nations.add(nation)

    add_same_family_patents(p,row['same_family_patent'])

    #return error_patents


def add_patents_from_csv_and_pdfs(csv_file,pdf_files):
    error_messages=[]

    f_csv = csv.DictReader(csv_file)

    #implementation 1 ---------correct code------------
    '''for myfile in pdf_files:
        fs = FileSystemStorage()
        fs.save(FILE_CACHE_DIR+myfile.name, myfile)

    for row in f_csv:
        try:
            add_patent_from_csv_row(row,None)
        except Exception as e:
            print(e)
            error_messages.append(row['公开（公告）号']+"出错!")'''

    #implementation 2
    pdf_files.sort(key=lambda file: file.name)
    pdf_names=[f.name for f in pdf_files]
    for row in f_csv:
        pub_id=row['公开（公告）号']
        t=find(pdf_names,pub_id+'.pdf')
        #print(pdf_files[t].name)
        if t!=-1:
            try:
                add_patent_from_csv_row(row,pdf_files[t])
            except Exception as e:
                log_and_print(e)
                error_messages.append(pub_id+"出错!")

            ####### 此处正式应用时删除###########
            #break
            ###########################
        else:
            error_messages.append(pub_id+" 没有文件!\n")

    return error_messages

def add_same_family_patents(patent,same_family_str):

    same_family_patents=same_family_str.split(';')
    for sfpatent in same_family_patents:
        sfpatent=sfpatent.strip()
        if sfpatent:
            try:
                FamilyFatent(patent=patent, same_family_patent=sfpatent).save()
            except Exception as e:
                log_and_print(e)

def add_applicants_and_nations(applicant_str, nation_str):
    applicants=applicant_str.split(';')
    applicant_list=[]
    nation_list=[]
    for applicant in applicants:
        a=applicant.strip()
        if a:
            obj,created=Applicant.objects.get_or_create(name=a)
            applicant_list.append(obj)

    nations=nation_str.split(',')
    for nation in nations:
        nation=nation.strip()
        if nation:
            obj,created=Nation.objects.get_or_create(name=nation)
            nation_list.append(obj)

    return applicant_list,nation_list

@login_required
def index(request):
    logger.info('zypang: get index')
    return redirect(reverse('main:query'))

@login_required
def add_data(request):
    if request.method=='POST':
        #form=PatentForm(request.POST,request.FILES)
        #1 for success 2 for failure 0 for default
        message='添加成功'
        try:
            add_patent_from_row(request.POST,request.FILES['pdf_file'])

        except Exception as e:
            log_and_print(e)
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
SHOW_FIELDS=(('标题','15%'),('标题（翻译）','15%'),('公开号','8%'),
             ('申请日','8%'),('申请人','14%'),
             ('标引','8%'),('法律状态','8%'),('公有标记','12%'),('私有标记','12%'))

             #('公开（公告）日','10%')
             #('申请人','10%'),
             #('专利类型','10%'))
def get_query_results_str(request,query_raw_result):
    query_result=[]
    for item in query_raw_result:
        applicant_str=';'.join([a.name for a in item.applicants.all()])
        #patent_type=PATENT_TYPE_DICT_REVERSE[item.patent_type]
        pub_notes,pri_notes=get_my_notes(request.user,item)
        pub_notes_str=''
        pri_notes_str=''
        if pub_notes:
            pub_notes_str='; '.join([note.note[:10] for note in pub_notes])
        if pri_notes:
            pri_notes_str='; '.join([note.note[:10] for note in pri_notes])
        query_result.append([item.title,item.title_cn,item.pub_id,#item.pub_date.strftime('%Y-%m-%d'),
                             item.application_date.strftime('%Y-%m-%d'),applicant_str,
                             item.index,item.law_state,pub_notes_str,pri_notes_str])
                                 #item.patent_type])
    return query_result

@login_required
def query_data(request):
    if request.method=='POST':
        return_dict={}
        query_page=int(request.POST['page'])
        #query_page=1
        query_field_count=request.POST['field_count']
        QObject=Q()
        #process year
        year=request.POST['year']
        print(year)
        return_dict['query_year']=False
        if year!='1':
            QObject &= Q(application_date__year=year)
            return_dict['query_year']=True

        for i in range(1,int(query_field_count)+1):
            query_field=request.POST['query_field_'+str(i)]
            query_text=request.POST['query_text_'+str(i)].strip()
            #get or object--------correct code----------
            #if '|' in query_text:
            #    or_object=Q()
            #    or_texts=query_text.split('|')
            #    for text in or_texts:
            #        or_object |= Q(**{query_field+'__icontains':text.strip()})
            #    QObject &= or_object
            #else:
            #    QObject &=Q(**{query_field+'__icontains':query_text})
            QObject &=Q(**{query_field+'__icontains':query_text})

        query_raw_result=Patent.objects.order_by('-application_date').filter(QObject).distinct()
        application_years=query_raw_result.values('application_date__year').distinct().order_by()
        application_years_list=[a['application_date__year'] for a in application_years]#.sort(reverse=True)
        application_years_list.sort(reverse=True)

        return_dict['application_years']=application_years_list
        result_length=query_raw_result.count()
        if result_length<=query_page*PAGE_SIZE:
            #no next page
            return_dict['has_next']=0
        else:
            return_dict['has_next']=1
        query_raw_result=query_raw_result[(query_page-1)*PAGE_SIZE:query_page*PAGE_SIZE]


        query_result=get_query_results_str(request,query_raw_result)

        return_dict['result_count']=result_length
        return_dict['query_result']=query_result
        return_dict['page']=query_page

        print(json.dumps(return_dict))

        return HttpResponse(json.dumps(return_dict))
        #return render(request,'main/query.html',{'query_fields':QUERY_FIELDS,
        #                                         'query_result':query_result,
        #                                         'show_fields':SHOW_FIELDS})
        #return render(request,'main/query_result_table.html',{'query_result':query_result,
        #                                                      'user_name':request.user.get_username(),
        #                                                      'show_fields':SHOW_FIELDS,
        #                                                      'result_count':result_length})
    else:
        query_raw_result=Patent.objects.order_by('-application_date').all()
        application_years=query_raw_result.values('application_date__year').distinct().order_by()
        application_years_list=[a['application_date__year'] for a in application_years]#.sort(reverse=True)
        application_years_list.sort(reverse=True)

        result_length=query_raw_result.count()
        has_next=0
        if result_length>PAGE_SIZE:
            has_next=1
            query_raw_result=query_raw_result[:PAGE_SIZE]

        query_result=get_query_results_str(request,query_raw_result)

        return render(request,'main/query.html',{'query_fields':QUERY_FIELDS,
                                                 'show_fields':SHOW_FIELDS,
                                                 'user_name':request.user.get_username(),
                                                 'result_count':result_length,
                                                 'has_next':has_next,
                                                 'application_years':application_years_list,
                                                 'query_result':query_result})
@login_required
def change_data(request):
    pub_id=request.POST['pub_id']
    p=Patent.objects.get(pk=pub_id)



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
    p.pub_date=row['pub_date']
    p.application_id=row['application_id']
    p.application_date=row['application_date']
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

    family_patents=FamilyFatent.objects.filter(patent=p)
    family_patents.delete()
    add_same_family_patents(p,row['same_family_patent'])

@login_required
def del_data(request):
    pub_id=request.POST['pub_id']
    return_dict={'success':1}

    try:
        patent=Patent.objects.get(pk=pub_id)
        patent.delete()
    except Exception as e:
        log_and_print(e)
        return_dict['success']=0
    else:
        log_and_print(request.user.get_username()+' : delete patent : '+pub_id)

    return HttpResponse(json.dumps(return_dict))
def get_notes(user,patent):
    #print(user.groups.all())
    if user.has_perm('main.view_private_notes'):
        notes=Note.objects.filter(patent=patent)
    else:
        notes=Note.objects.filter(patent=patent,type=0) | \
              Note.objects.filter(patent=patent,user=user)
    return notes

def get_my_notes(user,patent):
    #if user.has_perm('main.view_private_notes'):
    #    notes=Note.objects.filter(patent=patent,type=1)
    #else:
    #    notes=Note.objects.filter(patent=patent,user=user,type=1)
    pub_notes=Note.objects.filter(patent=patent,user=user,type=0)
    private_notes=Note.objects.filter(patent=patent,user=user,type=1)

    return pub_notes,private_notes

@login_required
def show_data(request):
    #below code for change data---------correct code---------------
    #if request.method=='POST':
    #    try:
    #        change_data(request)
    #    except Exception as e:
    #        log_and_print(e)
    #        return render(request,'main/show_message.html',{'success':0,
    #                                                    'message':'修改数据失败，请检查输入是否有错'})
    #    return render(request,'main/show_message.html',{'message':'数据修改成功',
    #                                                    'success':1})
    #else:
    pub_id=request.GET['pub_id']
    try:
        patent=Patent.objects.get(pk=pub_id)
    except Exception as e:
        log_and_print(e)
        return render(request,'main/show_message.html',
                      {'message':'数据库中查不到本专利，请检查公开号',
                       'success':0})

    applicant_str=';'.join([a.name for a in patent.applicants.all()])
    nation_str=','.join([a.name for a in patent.nations.all()])
    family_patents=FamilyFatent.objects.filter(patent=patent)
    family_patent_str=';'.join([a.same_family_patent for a in family_patents])

    notes=get_notes(request.user,patent)
    can_del=False
    if request.user.has_perm('main.view_private_notes'):
        can_del=True
    return_dict={
        'item':patent,
        'applicant_str':applicant_str,
        'nation_str':nation_str,
        'family_patent_str':family_patent_str,
        'notes':notes,
        'user_name':request.user.get_username(),

        'patent_types':PATENT_TYPES,
        'note_types':NOTE_TYPE,
        'can_del':can_del,
    }
    return render(request,'main/detail.html',return_dict)

@login_required
def view_file(request,pub_id):
    patent=Patent.objects.get(pk=pub_id)
    #print(patent.pdf_file.name)
    #filename=''
    #if patent.pdf_file:
    try:
        #filename = patent.pdf_file.name.split('/')[-1]
        response = HttpResponse(patent.pdf_file, content_type='application/pdf')
    except Exception as e:
        log_and_print(e)
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
        log_and_print(e)
        return render(request,'main/show_message.html',{'message':'添加批注失败',
                                                        'success':0})
    return redirect(reverse("main:detail")+'?pub_id='+pub_id)

#clear_all function ONLY FOR DEBUG!
def clear_all(request):
    Patent.objects.all().delete()
    return render(request,'main/show_message.html',{'message':'清空成功',
                                                    'success':1})

# Create your views here.
