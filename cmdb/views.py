# -*- coding: utf-8 -*-
'''
    Author: smallmi
    Blog: http://www.smallmi.com
'''
import os
import xlrd as xlrd
from openpyxl import Workbook
from django.db.models import Count
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.urls import reverse
from openpyxl.writer.excel import save_virtual_workbook
from pytz import unicode

from cmdb.forms import ServerForm, SystemUserForm
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, FileResponse
from django.shortcuts import render
from commons.paginator import paginator
from cmdb.models import *
import json
from django.contrib.auth.decorators import permission_required, login_required
# Create your views here.
from controller.public.permissions import check_perms
from controller.ansible_api.get_hosts_api import *
from release.models import Platform
import logging

logger = logging.getLogger('omms')

PAGE_SIZE = 10  # 每页显示条数
current_page_total = 10  # 分页下标


@login_required
def index(request):
    user = request.user
    if user.is_superuser:
        role = '超级管理员'
    elif user.is_anonymous():
        role = '匿名用户'
    else:
        role = '普通用户'
    request.role = role
    return render_to_response('base/index.html', {'request': request})


# def time_count(content, start_time, end_time):
#
#     start_time = time.strptime(str(start_time).split('+')[0], "%Y-%m-%d %H:%M:%S")
#     end_time = time.strptime(
#         str(end_time).split('+')[0], "%Y-%m-%d %H:%M:%S")
#     timestamp = int(time.mktime(end_time)) - int(time.mktime(start_time))
#
#     setattr(content, 'time', str(timestamp // 3600) + '小时' + str(timestamp % 3600 // 60) + '分')

@login_required
@permission_required('cmdb.view_server', raise_exception=True)
def server_list(request):
    form = ServerForm()
    server = Server.objects.order_by('id')
    groups = ServerGroup.objects.values_list('id', 'name')
    idcs = Idc.objects.values_list('id', 'name')
    apps = AppProject.objects.values_list('id', 'app_name_cn', 'app_name_en')
    users = SystemUser.objects.values_list('id', 'name', 'username')

    data = paginator(request, server)

    request.breadcrumbs((('首页', '/'), ('资产列表', reverse('server_list'))))

    data['groups'] = json.dumps([(i[0], i[1]) for i in groups])
    data['idcs'] = json.dumps([(i[0], i[1]) for i in idcs])
    data['apps'] = json.dumps([(i[0], i[1], i[2]) for i in apps])
    data['users'] = json.dumps([(i[0], i[1], i[2]) for i in users])
    data['form'] = form

    return render_to_response('cmdb/server.html', data)


@login_required
@permission_required('cmdb.view_serverGroup', raise_exception=True)
def server_group(request):
    group = ServerGroup.objects.annotate(average_server=Count('servers')).order_by('id')
    data = paginator(request, group)
    request.breadcrumbs((('首页', '/'), ('资产组列表', reverse('server_group'))))

    return render_to_response('cmdb/group.html', data)


@login_required
@permission_required('cmdb.view_idc', raise_exception=True)
def server_idc(request):
    idc = Idc.objects.annotate(average_server=Count('servers')).order_by('id')
    data = paginator(request, idc)
    request.breadcrumbs((('首页', '/'), ('IDC列表', reverse('server_idc'))))
    if request.method != "POST":
        return render_to_response('cmdb/idc.html', data)
    else:
        return render_to_response('cmdb/server.html', data)


@login_required
@permission_required('cmdb.view_systemUser', raise_exception=True)
def system_user(request):
    data = {}

    form = SystemUserForm()
    users = SystemUser.objects.order_by('id')
    data = paginator(request, users)
    request.breadcrumbs((('首页', '/'), ('登录用户列表', reverse('system_user'))))

    data['form'] = form
    return render_to_response('cmdb/user.html', data)


@login_required
def system_user_add(request):
    # 新增登录用户
    error = ""
    response = HttpResponse()
    if check_perms(request, 'cmdb.add_systemUser', raise_exception=True):
        if request.method == "POST":
            new_name = request.POST.get('name')
            user = SystemUser.objects.filter(name=new_name)

            form = SystemUserForm(request.POST)

            if user:
                error = u"该名称已存在!"
                # response.write(json.dumps(u'该机器已存在!'))
            elif new_name == '':
                error = u"你闲的蛋疼么？字都懒得打！"
                # response.write(json.dumps(u'你闲的蛋疼么？字都懒得打！'))
                # return render(request, 'error.html', {'request': request, 'error': error})
            else:
                if form.is_valid():
                    user = form.save(commit=False)
                    user.save()
                    # response.write(json.dumps(u'成功'))
                    return HttpResponseRedirect(reverse('system_user'))
        # return render(request, 'error.html', {'request': request, 'error': error})
    else:
        error = u'您没有权限操作@^@，请联系管理员！'

    return render(request, 'error.html', {'request': request, 'error': error})


@login_required
# @permission_required('cmdb.change_server', raise_exception=True)
def system_user_edit(request):
    # 编辑机器
    response = HttpResponse()
    if check_perms(request, 'cmdb.change_systemUser', raise_exception=True):
        data = json.loads(request.POST.get('data', ''))

        id = data['id']
        name = data['name']
        username = data['username']
        password = data['password']
        comment = data['comment']

        user = SystemUser.objects.get(pk=id)
        user.name = name
        user.username = username
        user.password = password
        user.comment = comment
        user.save()
        response.write(json.dumps(u'成功'))
    else:
        response.write(json.dumps(u'您没有权限操作@^@，请联系管理员！'))

    return response


@login_required
# @permission_required('cmdb.delete_server', raise_exception=True)
def system_user_delete(request):
    # 删除机器信息
    response = HttpResponse()
    if check_perms(request, 'cmdb.delete_systemUser', raise_exception=True):

        data = json.loads(request.POST.get('data', ''))
        id = int(data['id'])
        SystemUser.objects.get(pk=id).delete()
        response.write(json.dumps(u'成功'))
    else:
        response.write(json.dumps(u'您没有权限操作@^@，请联系管理员！'))

    return response


def server_add_page(request):
    # 新增机器页面
    return render_to_response('cmdb/server_add.html', locals(), context_instance=RequestContext(request))


@login_required
# @permission_required('cmdb.add_server', raise_exception=True)
def server_add(request):
    # 新增机器
    error = ""
    response = HttpResponse()
    if check_perms(request, 'cmdb.add_server', raise_exception=True):
        if request.method == "POST":
            groups = request.POST.getlist('groups')
            new_in_ip = request.POST.get('in_ip')
            server = Server.objects.filter(in_ip=new_in_ip)

            form = ServerForm(request.POST)

            if server:
                error = u"该机器已存在!"
                # response.write(json.dumps(u'该机器已存在!'))
            elif new_in_ip == '':
                error = u"你闲的蛋疼么？字都懒得打！"
                # response.write(json.dumps(u'你闲的蛋疼么？字都懒得打！'))
                # return render(request, 'error.html', {'request': request, 'error': error})
            else:
                if form.is_valid():
                    server = form.save(commit=False)
                    server.author = request.user
                    server.save()
                    server.groups.clear()
                    server.groups.add(*groups)
                    # response.write(json.dumps(u'成功'))
                    return HttpResponseRedirect(reverse('server_list'))
        # return render(request, 'error.html', {'request': request, 'error': error})
    else:
        error = u'您没有权限操作@^@，请联系管理员！'

    return render(request, 'error.html', {'request': request, 'error': error})


@login_required
# @permission_required('cmdb.add_servergroup', raise_exception=True)
def group_add(request):
    # 新增资产组
    response = HttpResponse()

    if check_perms(request, 'cmdb.add_serverGroup', raise_exception=True):
        if request.method == "POST":
            user = request.user
            data = json.loads(request.POST.get('data', ''))

            groupName = data['group_name']

            group = ServerGroup.objects.filter(name=groupName)

            if group:
                response.write(json.dumps(u'尼玛，重复了！'))
            elif len(groupName) == 0:
                response.write(json.dumps(u'你闲的蛋疼么？字都懒得打！'))
            else:
                group = ServerGroup()
                group.created_by_id = user.id
                group.name = groupName
                group.comment = data['group_comment']
                try:
                    group.save()
                except:
                    response.write(json.dumps(u'异常'))
                else:
                    response.write(json.dumps(u'成功'))

        else:
            pass
    else:
        response.write(json.dumps(u'您没有权限操作@^@，请联系管理员！'))

    return response


@login_required
# @permission_required('cmdb.add_idc', raise_exception=True)
def idc_add(request):
    # 新增IDC
    response = HttpResponse()

    if check_perms(request, 'cmdb.add_idc', raise_exception=True):
        error = ""
        if request.method == "POST":
            user = request.user
            data = json.loads(request.POST.get('data', ''))

            idcName = data['idc_name']
            idc = Idc.objects.filter(name=idcName)

            if idc:
                response.write(json.dumps(u'尼玛，重复了！'))
            elif len(idcName) == 0:
                response.write(json.dumps(u'你闲的蛋疼么？字都懒得打！'))
            else:
                try:
                    idc = Idc()
                    idc.created_by_id = user.id
                    idc.name = idcName
                    idc.contact = data['idc_contact']
                    idc.phone = data['idc_phone']
                    idc.address = data['idc_address']
                    idc.intranet = data['idc_intranet']
                    idc.extranet = data['idc_extranet']
                    idc.operator = data['idc_operator']
                    idc.save()
                except:
                    response.write(json.dumps(u'异常'))
                else:
                    response.write(json.dumps(u'成功'))

        else:
            pass
    else:
        response.write(json.dumps(u'您没有权限操作@^@，请联系管理员！'))

    return response


def server_edit_page(request, id):
    pass
    # 编辑机器页面
    # server = Server.objects.get(pk=id)
    # return render_to_response('cmdb/server_edit.html', locals(), context_instance=RequestContext(request))


@login_required
# @permission_required('cmdb.change_server', raise_exception=True)
def server_edit(request):
    # 编辑机器
    response = HttpResponse()
    if check_perms(request, 'cmdb.change_server', raise_exception=True):
        data = json.loads(request.POST.get('data', ''))

        id = data['id']
        # project_name = data['project_name']
        # service_name = data['service_name']
        groups_id = data['groups']
        in_ip = data['in_ip']
        ex_ip = data['ex_ip']
        idc = data['idc']
        app = data['app']
        user = data['user']

        server = Server.objects.get(pk=id)
        # server.project_name = project_name
        # server.service_name = service_name
        server.in_ip = in_ip
        server.ex_ip = ex_ip
        server.idc_id = idc
        server.system_user_id = user
        server.app_project_id = app
        try:
            server.groups.clear()
            if groups_id:
                groups = ServerGroup.objects.filter(id__in=groups_id)
                server.groups.add(*groups)
        except Exception as e:
            print(e)
        server.save()

        response.write(json.dumps(u'成功'))
    else:
        response.write(json.dumps(u'您没有权限操作@^@，请联系管理员！'))

    return response


@login_required
@permission_required('cmdb.update_server', raise_exception=True)
def server_webssh(request):
    if request.method == 'POST':
        id = request.POST.get('id', None)
        server = Server.objects.get(pk=id)
        ip = server.in_ip + ":22"
        if server.system_user_id is not None:
            username = server.system_user.username
            password = server.system_user.password
        else:
            username = ""
            password = ""
        # login_ip = request.META['REMOTE_ADDR']

        ret = {"ip": ip, "username": username, 'password': password, "static": True}

    # web_history.objects.create(user=request.user, ip=login_ip, login_user=obj.system_user.username, host=ip)
    return HttpResponse(json.dumps(ret))


@login_required
# @permission_required('cmdb.change_servergroup', raise_exception=True)
def group_edit(request):
    # 编辑机器
    response = HttpResponse()
    if check_perms(request, 'cmdb.change_serverGroup', raise_exception=True):
        data = json.loads(request.POST.get('data', ''))

        id = data['id']
        group_name = data['group_name']
        group_comment = data['group_comment']

        group = ServerGroup.objects.get(pk=id)
        group.name = group_name
        group.comment = group_comment
        group.save()

        response.write(json.dumps(u'成功'))
    else:
        response.write(json.dumps(u'您没有权限操作@^@，请联系管理员！'))

    return response


@login_required
# @permission_required('cmdb.change_idc', raise_exception=True)
def idc_edit(request):
    # 编辑IDC

    response = HttpResponse()

    if check_perms(request, 'cmdb.change_idc', raise_exception=True):
        data = json.loads(request.POST.get('data', ''))

        id = data['id']

        idc = Idc.objects.get(pk=id)
        idc.name = data['idc_name']
        idc.contact = data['idc_contact']
        idc.phone = data['idc_phone']
        idc.address = data['idc_address']
        idc.intranet = data['idc_intranet']
        idc.extranet = data['idc_extranet']
        idc.operator = data['idc_operator']
        try:
            idc.save()
        except:
            response.write(json.dumps(u'失败'))
        else:
            response.write(json.dumps(u'成功'))
    else:
        response.write(json.dumps(u'您没有权限操作@^@，请联系管理员！'))

    return response


@login_required
# @permission_required('cmdb.delete_server', raise_exception=True)
def server_delete(request):
    # 删除机器信息
    response = HttpResponse()
    if check_perms(request, 'cmdb.delete_server', raise_exception=True):

        data = json.loads(request.POST.get('data', ''))
        id = int(data['id'])
        Server.objects.get(pk=id).delete()
        response.write(json.dumps(u'成功'))
    else:
        response.write(json.dumps(u'您没有权限操作@^@，请联系管理员！'))

    return response


@login_required
# @permission_required('cmdb.delete_servergroup', raise_exception=True)
def group_delete(request):
    # 删除资产组
    response = HttpResponse()

    if check_perms(request, 'cmdb.delete_serverGroup', raise_exception=True):
        data = json.loads(request.POST.get('data', ''))

        id = int(data['id'])
        ServerGroup.objects.get(pk=id).delete()

        response.write(json.dumps(u'成功'))
    else:
        response.write(json.dumps(u'您没有权限操作@^@，请联系管理员！'))

    return response


@login_required
# @permission_required('cmdb.delete_idc', raise_exception=True)
def idc_delete(request):
    # 删除IDC
    response = HttpResponse()

    if check_perms(request, 'cmdb.delete_idc', raise_exception=True):
        data = json.loads(request.POST.get('data', ''))

        id = int(data['id'])
        Idc.objects.get(pk=id).delete()

        response.write(json.dumps(u'成功'))
    else:
        response.write(json.dumps(u'您没有权限操作@^@，请联系管理员！'))

    return response


@login_required
def group_server_detail(request, id):
    form = ServerForm()
    groups = ServerGroup.objects.values_list('id', 'name')
    idcs = Idc.objects.values_list('id', 'name')
    apps = AppProject.objects.values_list('id', 'app_name_cn', 'app_name_en')

    groupName = ServerGroup.objects.get(pk=id)
    servers = groupName.servers.all().order_by('id')

    data = paginator(request, servers)

    data['groups'] = json.dumps([(i[0], i[1]) for i in groups])
    data['idcs'] = json.dumps([(i[0], i[1]) for i in idcs])
    data['apps'] = json.dumps([(i[0], i[1], i[2]) for i in apps])
    data['groupName'] = groupName
    data['groupId'] = id
    data['form'] = form
    request.breadcrumbs((('首页', '/'), ('资产组', reverse('server_group'))))

    return render_to_response('cmdb/group_server_detail.html', data)


@login_required
def idc_server_detail(request, id):
    form = ServerForm()
    groups = ServerGroup.objects.values_list('id', 'name')
    idcs = Idc.objects.values_list('id', 'name')
    apps = AppProject.objects.values_list('id', 'app_name_cn', 'app_name_en')

    idcName = Idc.objects.get(pk=id)
    servers = idcName.servers.all().order_by('id')

    data = paginator(request, servers)

    data['groups'] = json.dumps([(i[0], i[1]) for i in groups])
    data['idcs'] = json.dumps([(i[0], i[1]) for i in idcs])
    data['apps'] = json.dumps([(i[0], i[1], i[2]) for i in apps])
    data['idcName'] = idcName
    data['idcId'] = id
    data['form'] = form
    request.breadcrumbs((('首页', '/'), ('IDC机房', reverse('server_idc'))))

    return render_to_response('cmdb/idc_server_detail.html', data)
    # pass


@login_required
# @permission_required('cmdb.update_server', raise_exception=True)
def postmachineinfo(request):
    response = HttpResponse()
    if check_perms(request, 'cmdb.update_server', raise_exception=True):
        # 提交服务器信息
        data = json.loads(request.GET.get('data', ''))
        id = int(data['id'])
        server = Server.objects.get(pk=id)
        system_username = server.system_user.username
        system_passwd = server.system_user.password
        assets = [
            {
                "hostname": server.in_ip,
                "ip": server.in_ip,
                "port": '22',
                "username": system_username,
                "password": system_passwd,
            }
        ]

        infoList = get_host_info(assets)
        logger.info('请求成功！采集该主机信息开始，host:{}'.format(server.in_ip))

        if not infoList[0]['status']:
            response.write(json.dumps(u'主机网络不可达'))
        else:
            for data in infoList:
                if data['status']:
                    server.os_version = data['sysinfo']
                    server.host_name = data['host_name']
                    server.os_kernel = data['os_kernel']
                    server.cpu_model = data['cpu']
                    server.cpu_count = data['cpu_count']
                    server.cpu_cores = data['cpu_cores']
                    server.mem = data['mem']
                    server.disk = data['disk']
                    server.status = data['status']

                    ulimit = get_ulimit(assets)
                    for limit in ulimit:
                        server.max_open_files = limit['ulimit']

                    uptime = get_uptime(assets)
                    for tim in uptime:
                        server.uptime = tim['uptime']

                else:
                    server.status = data['status']
                server.save()

            # set_service_port(server)  # 设置服务端口信息
            response.write(json.dumps(u'刷新成功'))
    else:
        response.write(json.dumps(u'您没有权限操作@^@，请联系管理员！'))

    return response


@login_required
# @permission_required('cmdb.update_server', raise_exception=True)
def flushAllHosts(request):
    response = HttpResponse()
    if check_perms(request, 'cmdb.update_server', raise_exception=True):
        server = Server.objects.order_by('id')
        hostsInfo = server.values_list('in_ip', 'system_user__username', 'system_user__password')
        hostList = []
        for i in hostsInfo:
            hostDic = {
                "hostname": i[0],
                "ip": i[0],
                "port": '22',
                "username": i[1],
                "password": i[2],
            }
            hostList.append(hostDic)
        infoList = get_host_info(hostList)

        if not infoList:
            response.write(json.dumps(u'批量刷新异常'))
        else:
            for data in infoList:
                servers = Server.objects.filter(in_ip=data['ipadd_in'])
                if data['status']:
                    servers.update(os_version=data['sysinfo'], host_name=data['host_name'], os_kernel=data['os_kernel'],
                                   cpu_model=data['cpu'], cpu_count=data['cpu_count'], cpu_cores=data['cpu_cores'],
                                   mem=data['mem'], disk=data['disk'], status=data['status'])
                else:
                    servers.update(status=data['status'])

            ulimit = get_ulimit(hostList)
            for data in ulimit:
                servers = Server.objects.filter(in_ip=data['host_ip'])
                servers.update(max_open_files=data['ulimit'])

            uptime = get_uptime(hostList)
            for data in uptime:
                servers = Server.objects.filter(in_ip=data['host_ip'])
                servers.update(uptime=data['uptime'])

            # set_service_port(server)  # 设置服务端口信息
            response.write(json.dumps(u'批量刷新成功'))
    else:
        response.write(json.dumps(u'您没有权限操作@^@，请联系管理员！'))

    return response


@login_required
# @permission_required('cmdb.update_server', raise_exception=True)
def export_hosts(request):
    server = Server.objects.order_by('id')
    servers = server.values_list('in_ip', 'system_user__username', 'system_user__password', 'app_project__app_name_en',
                                 'cpu_cores', 'cpu_count', 'mem', 'disk', 'groups__name', 'app_project__platform__name',
                                 'idc__name', 'author__username', 'ctime')
    header_text = "IP,用户名,密码,服务名称,CPU核数,CPU个数,内存,磁盘,所属资产组,所属平台,IDC机房,创建者,创建时间"
    excel_name = unicode(u'服务器详细列表')
    headers = unicode(header_text).split(',')
    book = Workbook()
    sheet = book.create_sheet(title=excel_name, index=0)
    sheet.append(headers)
    if servers:
        for server in servers:
            serverList = list(server)
            sheet.append(serverList)
    else:
        logger.info('资产查询无数据')
    response = HttpResponse(content=save_virtual_workbook(book), content_type='application/msexcel')
    response['Content-Disposition'] = 'attachment; filename=servers_list.xlsx'
    return response


@login_required
# @permission_required('cmdb.update_server', raise_exception=True)
def download_template(request):
    file = open('./doc/file/Template.xlsx', 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="Template.xlsx"'
    return response


@login_required
# @permission_required('cmdb.update_server', raise_exception=True)
def upload_hosts(request):
    result = {"data": []}
    createAuthor = request.user
    response = HttpResponse()
    response['Content-Type'] = "text/javascript"
    hostsFile = request.FILES.getlist('hostsFile')
    if hostsFile is not None:
        tmpDir = os.path.dirname('/tmp/')
        for i in hostsFile:
            filename = os.path.join(tmpDir, i.name)
            file = open(filename, 'wb')
            for chrunk in i.chunks():
                file.write(chrunk)
            file.close()
        result["filename"] = filename

    excel_table_by_name(filename, createAuthor)
    return JsonResponse(result)


def excel_table_by_name(file_excel, createAuthor, col_name_index=0, by_name=u'Sheet1'):
    """
        根据名称获取Excel表格中的数据
        参数: file_excel：Excel文件路径
             col_name_index：表头列名所在行的所以
             by_name：Sheet1名称
    """
    data = xlrd.open_workbook(file_excel)
    table = data.sheet_by_name(by_name)
    n_rows = table.nrows  # 行数
    # col_names = table.row_values(col_name_index)  # 某一行数据

    row_list = []
    for row_num in range(1, n_rows):
        row_dict = {}
        row = table.row_values(row_num)
        row_dict['in_ip'] = row[0]
        row_dict['username'] = row[1]
        row_dict['password'] = row[2]
        row_dict['app_name_cn'] = row[3]
        row_dict['app_name_en'] = row[4]
        row_dict['groupName'] = row[5]
        row_dict['platform_name'] = row[6]
        row_dict['idcName'] = row[7]
        row_list.append(row_dict)

    for rl in row_list:
        server = Server.objects.filter(in_ip=rl['in_ip'])
        if not server:
            logger.info('主机不存在，开始导入；host:{}'.format(str(rl['in_ip'])))

            try:
                pn = Platform.objects.get(name=rl['platform_name']).id
            except Platform.DoesNotExist:
                logger.info('平台不存在，准备创建；platform:{}'.format(rl['platform_name']))
                Platform.objects.create(name=rl['platform_name'], created_by=createAuthor)
                pn = Platform.objects.get(name=rl['platform_name']).id

            try:
                an = AppProject.objects.get(app_name_en=rl['app_name_en']).id
            except (AppProject.DoesNotExist, ServerGroup.DoesNotExist, Idc.DoesNotExist, SystemUser.DoesNotExist, Platform.DoesNotExist):
                logger.info('应用不存在，准备创建；app:{}'.format(rl['app_name_en']))
                AppProject.objects.create(app_name_en=rl['app_name_en'], app_name_cn=rl['app_name_cn'], platform_id=int(pn), author=createAuthor)
                an = AppProject.objects.get(app_name_en=rl['app_name_en']).id

            try:
                sg = ServerGroup.objects.get(name=rl['groupName']).id
            except ServerGroup.DoesNotExist:
                logger.info('资产组不存在，准备创建；group:{}'.format(rl['groupName']))
                ServerGroup.objects.create(name=rl['groupName'], created_by=createAuthor)
                sg = ServerGroup.objects.get(name=rl['groupName']).id

            try:
                idcn = Idc.objects.get(name=rl['idcName']).id
            except Idc.DoesNotExist:
                logger.info('IDC不存在，准备创建；IDC:{}'.format(rl['idcName']))
                Idc.objects.create(name=rl['idcName'], created_by=createAuthor)
                idcn = Idc.objects.get(name=rl['idcName']).id

            try:
                un = SystemUser.objects.get(username=rl['username']).id
            except SystemUser.DoesNotExist:
                logger.info('linux系统用户不存在，准备创建；user:{}'.format(rl['username']))
                SystemUser.objects.create(name=rl['username'], username=rl['username'], password=rl['password'])
                un = SystemUser.objects.get(username=rl['username']).id

            sb = Server.objects.create(in_ip=rl['in_ip'], app_project_id=int(an), idc_id=int(idcn), system_user_id=int(un), author=createAuthor)
            sb.groups.add(int(sg))
        else:
            logger.info('主机存在，导入操作不执行；host:{}'.format(str(rl['in_ip'])))
