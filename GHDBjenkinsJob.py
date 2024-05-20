import jenkins

# Connect to Jenkins
server = jenkins.Jenkins('https://jenkins.bik8s.gh-bisre.com/', username='dsarkar', password='11726fb927f368765f67749346353408d4')
token= '11726fb927f368765f67749346353408d4'
job_name = 'bisqa_tools/stan%2Fjenkins'
selected_branch = 'stan/jenkins'
old_sample_id = 'A085820601'
new_sample_id = 'A108628801'
project_name = 'GHI_01'
product_name = 'Guardant 360'
report_module_docker_container ='docker.artifactory01.ghdna.io/bi-report-module:2.6-RLS'
cancer_type= 'Lung cancer'
# project_name = 'GHI_20'
report_status = 'PASS'
# ,'OLD_SAMPLE_ID':old_sample_id,'NEW_SAMPLE_ID':new_sample_id

# Verify connection
if server.get_whoami():
    print("Successfully connected to Jenkins")
    if server.job_exists(job_name):
        build_name = server.get_job_info(job_name)
        PARAMETERS = { 'report_module_docker_container':report_module_docker_container, 'old_sample_id': old_sample_id, 'new_sample_id': new_sample_id,
                       'cancer_type':cancer_type,'project_name':project_name,'report_status':report_status
                      }
        server.build_job(job_name, PARAMETERS)
        last_build_number = server.get_job_info(job_name)['lastCompletedBuild']['number']





