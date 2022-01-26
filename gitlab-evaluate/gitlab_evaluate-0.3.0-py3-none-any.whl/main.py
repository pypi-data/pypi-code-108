#!/usr/bin/python3
import argparse
from gitlab_ps_utils.api import GitLabApi
from gitlab_ps_utils.json_utils import json_pretty
from gitlab_evaluate.lib import api as api_helpers
from gitlab_evaluate.lib import human_bytes as hb
from gitlab_evaluate.lib import utils
import logging

def main():
  logging.basicConfig(filename='evaluate.log', level=logging.DEBUG)
  my_dict = {}
  csv_columns = ['Project','ID','kind','Pipelines','Pipelines_over','Issues','Issues_over','Branches','Branches_over','commit_count','commit_count_over','Merge Requests','Merge Requests_over','storage_size','storage_size_over','repository_size','repository_size_over','Tags','Tags_over']
  parser = argparse.ArgumentParser()
  parser.add_argument("-p", "--pat", help="Personal Access Token: REQ'd")
  parser.add_argument("-s", "--source", help="Source URL: REQ'd")
  parser.add_argument("-f", "--filename", help="CSV Output File Name")
  parser.add_argument("-o", "--output", action='store_true', help="Output Per Project Stats to screen")

  args = parser.parse_args()

  if None not in (args.pat, args.source):
    ### Setup the csv file and write the headers.
    if args.filename:
      csv_file = args.filename
      utils.write_to_csv(csv_file, csv_columns, [])

    ### API and Headers - Setup URLs
    headers = {
        'private-token': args.pat
    }

    payload = {
        'format': 'json'
    }

    app_api_url = "/application/statistics"
    project_api_url = "/projects?statistics=true"
    proj_inf_url = "/projects/"
    app_ver_url = "/version"
    source = args.source
    
    gitlabApi = GitLabApi()
    if resp := api_helpers.getApplicationInfo(args.source,args.pat,app_api_url):
      print('-' * 50)
      print(f'Basic information from source: {args.source}')
      # print("Status code:", 
      print("Total Merge Requests", resp.get('merge_requests'))
      print("Total Projects:", resp.get('projects'))
      print("total Forks:", resp.get('forks'))
      print('-' * 50)
    else:
      print(f"Unable to pull application info from URL: {gl_source_app}")

    if resp := api_helpers.getVersion(args.source, args.pat , app_ver_url):
      print('-' * 50)
      print("GitLab Source Ver:", resp.get('version'))
      print('-' * 50)
    else:
      print(f"Unable to pull application info from URL: {gl_source_ver}")

    ### Start of for loop to gather the API JSON data
    # for p in projects.json():
    
    for p in gitlabApi.list_all(args.source, args.pat, project_api_url):
      if args.output:
        print('+' * 40)
        print(f"Name: {p.get('name')} ID: {p.get('id')}")
        print(f"Desc: {p.get('description')}")
      my_dict["Project"] = p.get('name')
      my_dict["ID"] = p.get('id')

      ## Get the full project info with stats
      
      full_stats_url = api_helpers.proj_info_get(p.get('id'), source)
      api_helpers.check_full_stats(full_stats_url, p, my_dict, headers={'private-token': args.pat})
    
      #  TODO: This could be a dictionary of headers and functions eg:
      # boundaries = { 
      #   "Pipelines": {"threshold": 2500, "url": "/api/v4/projects/:id/pipelines"},
      #   "Issues":  {"threshold": 2500, "url": "/api/v4/projects/:id/issues"}
      # }

      # for k, v in boundaries.items():
      #   check_x_total_value_update_dict(p, k, v, my_dict, payload, headers)

      ## Get the `kind` of project - skip any that are of type `user`.

      # kind_url = api_helpers.proj_info_get(p.get('id'), source)
      # api_helpers.check_x_total_value_update_dict(utils.check_proj_type, p, kind_url, payload, headers, "Kind", my_dict)

      ## Get the number of pipelines per project
      pipelines_url = api_helpers.proj_pl_get(p.get('id'), source)
      api_helpers.check_x_total_value_update_dict(utils.check_num_pl, p, pipelines_url, payload, headers, "Pipelines", "Pipelines_over", my_dict)

      ## Get number of issues per project
      issues_url = api_helpers.proj_issue_get(p.get('id'), source)
      api_helpers.check_x_total_value_update_dict(utils.check_num_issues, p, issues_url, payload, headers, "Issues", "Issues_over", my_dict)
      
      ## Get number of branches per project
      branches_url = api_helpers.proj_branch_get(p.get('id'), source)
      api_helpers.check_x_total_value_update_dict(utils.check_num_br, p, branches_url, payload, headers, "Branches", "Branches_over", my_dict)

      ## Get number of merge requests per project
      mrequests_url = api_helpers.proj_mr_get(p.get('id'), source)
      api_helpers.check_x_total_value_update_dict(utils.check_num_mr, p, mrequests_url, payload, headers, "Merge Requests", "Merge Requests_over", my_dict)

      ## Get number of tags per project
      tags_url = api_helpers.proj_tag_get(p.get('id'), source)
      api_helpers.check_x_total_value_update_dict(utils.check_num_tags, p, tags_url, payload, headers, "Tags", "Tags_over", my_dict)

      if args.filename:
        dict_data = []
        dict_data.append({x: my_dict.get(x) for x in csv_columns})
        utils.write_to_csv(csv_file, csv_columns, dict_data, append=True)

      elif args.output == False:
        print(f"""
          {'+' * 40}
          {json_pretty(my_dict)}
        """)

      if args.output:
        print(json_pretty(my_dict))

      
  else:
    parser.print_help()

