from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from .models import Host
import pytz
from datetime import datetime, timedelta
from influxdb import InfluxDBClient

DT_FORMAT = '%d-%m-%Y %H:%M:%S'
EVENT_INTERVAL = 61


def home(request):
    return HttpResponse('<h1>hello world</h1>')


@csrf_exempt
@require_POST
def handle_event(request):
    hostname = request.POST.get('hostname')
    is_online = request.POST.get('is_online')
    is_online = True if is_online == 'true' else False
    try:
        timestamp = int(request.POST.get('timestamp'))
    except ValueError:
        return HttpResponse('event time not valid', status=400)
    try:
        host = Host.objects.get(hostname=hostname, is_active=True)
    except Host.DoesNotExist:
        return HttpResponse('host not registered')
    date_time = datetime.fromtimestamp(timestamp, tz=pytz.timezone(host.timezone))

    event_json = [
            {
            "measurement": "host_status",
            "tags": {
                "hostname": hostname,
            },
            "time": date_time,
            "fields": {
                "is_online": is_online
            }
        }
    ]
    client = InfluxDBClient(host=settings.INFLUXDB_HOST, port=8086)
    client.switch_database(settings.INFLUXDB_DB_NAME)
    client.write_points(event_json)
    return HttpResponse('event has been registered', status=200)


def str_to_date(datestr):
    return datetime.strptime(datestr, '%Y-%m-%dT%H:%M:%SZ')


def get_host_stats(request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    hostname = request.GET.get('hostname')
    params = {'is_active': True}
    if hostname:
        params['hostname'] = hostname
    hosts = Host.objects.filter(**params)
    if not hosts:
        return HttpResponse('hosts not registered', status=404)
    try:
        if start:
            start = datetime.strptime(start, "%d-%m-%Y")
        if end:
            end = datetime.strptime(end, "%d-%m-%Y")
    except ValueError:
        return HttpResponse('time data does not match format \'%d-%m-%Y\'', status=400)

    client = InfluxDBClient(host=settings.INFLUXDB_HOST, port=8086)
    client.switch_database(settings.INFLUXDB_DB_NAME)
    query = """
        SELECT * FROM host_status
        WHERE true
    """
    if start:
        query += " and time >= '{0}'".format(start)
    if end:
        query += " and time < '{0}'".format(end)
    if len(hosts) == 1:
        query += " and hostname = '{0}'".format(hosts[0].hostname)
    query += " order by time asc"
    raw_results = client.query(query)
    if not raw_results:
        return HttpResponse('Host hasn\'t been online', status=200)
    results = {}
    for h in hosts:
        host_points = list(raw_results.get_points(tags={'hostname': h.hostname}))
        if not host_points:
            continue
        start = None
        prev = None
        ranges = []
        for i in range(len(host_points)):
            point_time = str_to_date(host_points[i]['time'])
            if not start:
                start = point_time
                prev = point_time
            elif point_time - prev <= timedelta(seconds=EVENT_INTERVAL):
                prev = point_time
            elif point_time - prev > timedelta(seconds=EVENT_INTERVAL):
                if start == prev:
                    ranges.append((start.strftime(DT_FORMAT),))
                else:
                    ranges.append({'from': start.strftime(DT_FORMAT), 'to': prev.strftime(DT_FORMAT)})
                start = point_time
                prev = point_time
        if prev and start == prev:
            ranges.append((start.strftime(DT_FORMAT),))
        else:
            ranges.append({'from': start.strftime(DT_FORMAT), 'to': prev.strftime(DT_FORMAT)})
        if ranges:
            results[h.hostname] = ranges
    return JsonResponse({'has been online': results})
