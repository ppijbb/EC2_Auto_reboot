# -*- coding: utf-8 -*-
import boto3
from datetime import datetime

# 서울 리전
region = 'ap-northeast-2'
# 월 ~ 일요일
t = ["월", "화", "수", "목", "금", "토", "일"]


def lambda_handler(event, context):
    # 람다 호출된시점의 시간을 구합니다.
    print("===== lambda get started =====")
    now_date = t[datetime.today().weekday()]
    now_hour = int(datetime.now().strftime('%H')) + 9
    print("now >> date: " + now_date + ", hour: " + str(now_hour))

    # ec2 인스턴스의 모든 태그를 조회합니다.
    ec2 = boto3.client('ec2', region_name=region)
    response = ec2.describe_tags(
        Filters=[
            {
                'Name': 'resource-type',
                'Values': ['instance']
            }
        ]
    )

    # 값 임시 저장
    enable_instances = []
    day_instances = {}
    time_instances = {}

    # AUTO_STOP_ENABLE 태그가 true인 값만 추출합니다/
    for tag in response['Tags']:
        name = ""
        if tag['Key'] == "AUTOSTOP_ENABLE" and tag['Value'].lower() == "true":
            enable_instances.append(tag['ResourceId'])
        if tag['Key'] == "DAY":
            day_instances[tag['ResourceId']] = tag['Value']
        if tag['Key'] == "TIME":
            time_instances[tag['ResourceId']] = tag['Value']

    for i, instance in enumerate(enable_instances):
        try:
            # 요일이 일치하는지 확인합니다.
            days = day_instances[instance].split(",")
            is_day = False
            for d in days:
                if now_date == d:
                    is_day = True

            # 시간이 일치하는지 확인합니다.
            times = time_instances[instance].split("~")
            is_start_time = False
            is_end_time = False

            if int(times[1].strip()) == now_hour:
                is_end_time = True
            elif int(times[0].strip()) == now_hour:
                is_start_time = True

            if is_day == True and is_end_time == True:
                # 중지 인스턴스 호출
                ec2.stop_instances(InstanceIds=[instance])
                print(f"ec2 instance({instance}) will stop")
            elif is_day == True and is_start_time == True:
                # 시작 인스턴스 호출
                ec2.start_instances(InstanceIds=[instance])
                print(f"ec2 instance({instance}) will start")
        except Exception as ex:
            print(ex)

    print("===== lambda exit =====")