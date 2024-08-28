#!/usr/bin/env python
 
import argparse
import json
import html
import requests
import re
import chump
import time
import os
import notifypy
from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict
 
@dataclass
class Project:
    pid: str
    name: str
    pay: float
    task_count: int
 
def get_html_with_cookie(cookie):
    url = 'https://app.dataannotation.tech/workers/projects'
    headers = { 'Cookie': cookie }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.text
    else:
        raise Exception()
 
def get_data_props(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    element_id = 'workers/WorkerProjectsTable-hybrid-root'
    element = soup.find(id=element_id)
    
    if element:
        data_props = element.get('data-props')
        return data_props
    else:
        return None
 
def parse_data_props(data_props_string):
    unescaped_string = html.unescape(data_props_string)
    json_data = json.loads(unescaped_string)
    
    return json_data
 
def props_to_projects(props) -> list[Project]:
    projs = props['dashboardMerchTargeting']['projects']
    converted = []
    pay_patt = re.compile(r'\$(\d+(?:\.\d+)?)/hr')
    
    for p in projs:
        if m := re.match(pay_patt, p['pay']):
            converted.append(Project(
                pid=p['id'],
                name=p['name'],
                pay=float(m[1]),
                task_count=int(p['availableTasksFor']),
            ))
 
    return converted
 
def write_projects_to_json(file_path: str, projects: list[Project]):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump([asdict(project) for project in projects], f, ensure_ascii=False, indent=4)
 
def read_projects_from_json(file_path: str) -> list[Project]:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [Project(**item) for item in data]
    except FileNotFoundError:
        return []
 
def new_good_projects_present(old_projs: list[Project],
                              new_projs: list[Project],
                              threshold: int) -> list[Project]:
    old_ids = set(p.pid for p in old_projs if p.pay >= threshold)
    added = []
 
    for good_p in [p for p in new_projs if p.pay >= threshold]:
        if not good_p.pid in old_ids:
            added.append(good_p)
 
    return added
 
def notify_projects(added_projects: list[Project], user: chump.User):
    message = '\n'.join(f'[${p.pay} | {p.task_count}] {p.name}' for p in added_projects)
    title = 'New DA Project(s)'
    print(f"Projects:\n{message}")
 
    # Push notification to phone
    user.send_message(
        title=title,
        message=message,
        url='https://app.dataannotation.tech/workers/projects'
    )
 
    notif = notifypy.Notify()
    notif.title = title
    notif.message = message
    notif.send(block=False)
 
def main(interval: int, threshold: int):
    project_file = '.projects'
    cookie = os.environ.get('DA_COOKIE') # 'word-thing=fadfe5f3fffffffffffffffffff; _dd_s=.....&expire=172...'
    pushover_app_key = os.environ.get('PUSHOVER_DA_KEY')
    pushover_user_key = os.environ.get('PUSHOVER_USER_KEY')
    push_app = chump.Application(pushover_app_key)
    push_user = chump.User(push_app, pushover_user_key)
 
    print(f"Running. Looking for projects with pay starting at ${threshold}/hour, checking every {interval} minutes.")
 
    while True:
        print("Fetching up to date project list...")
 
        try:
            html = get_html_with_cookie(cookie)
        except:
            print("Failed to fetch projects: cookie expired, or connection lost.")
 
        props = get_data_props(html)
        props_json = parse_data_props(props)
        projects = props_to_projects(props_json)
 
        previous_projects = read_projects_from_json(project_file)
 
        if ps := new_good_projects_present(previous_projects, projects, threshold):
            print("New projects detected. Sending notification...")
            notify_projects(ps, push_user)
            print("Notification sent.")
        else:
            print("No new projects detected.")
        
        write_projects_to_json(project_file, projects)
 
        print(f"Sleeping for {interval} minutes.")
        time.sleep(60*interval)
 
 
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--interval',
                        type=int,
                        default=30,
                        help='Time between updates, in minutes')
    parser.add_argument('-t', '--threshold',
                        type=float,
                        default=35,
                        help='Minimum $/hour amount to notify for')
    args = parser.parse_args()
 
    main(interval=args.interval, threshold=args.threshold)
 
