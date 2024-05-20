import os.path
import sys
import time
import traceback
from tkinter import END, dialog
from tkinter import messagebox

# import openpyxl as openpyxl
# from IPython.core import payload
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import pdb
from colorama import Fore, Style

# import LIMSDBConnect
import requests
import json
import xml.etree.ElementTree as ET
import tkinter
import customtkinter
from PIL import Image

import datetime
import json
import this
# import pandas as pd

import oracledb
import jenkins


global env,copies, refrequest, refsample,taskname,sessionid , __connection, __cursor

def load_config():
    global config
#Open Config File
    with open('config.json', 'r') as f:
        config = json.load(f)

#Conect to DB

__connection = None
__cursor = None
driver= None
previousTaskName = 0

def connect_DB():
    global __cursor, __connection
    try:
        env= config['CURRENT_ENV']
        if env == 'SQA':
            USERNAME = config['SQA_DATABASE']['username']
            PASSWORD = config['SQA_DATABASE']['password']
            HOST = config['SQA_DATABASE']['host']
            DB = config['SQA_DATABASE']['db']
        elif env == 'VAL':
            USERNAME = config['VAL_DATABASE']['username']
            PASSWORD = config['VAL_DATABASE']['password']
            HOST = config['VAL_DATABASE']['host']
            DB = config['VAL_DATABASE']['db']
        elif env == 'STAGING':
            USERNAME = config['STAGING_DATABASE']['username']
            PASSWORD = config['STAGING_DATABASE']['password']
            HOST = config['STAGING_DATABASE']['host']
            DB = config['STAGING_DATABASE']['db']
        elif env == 'DEV':
            USERNAME = config['DEV_DATABASE']['username']
            PASSWORD = config['DEV_DATABASE']['password']
            HOST = config['DEV_DATABASE']['host']
            DB = config['DEV_DATABASE']['db']
        #     Connect to DB
        if __connection == None:
            __connection = oracledb.connect(user=USERNAME, password=PASSWORD,
                                            host=HOST, service_name = DB)
            print ("Connection to the LIMS DB is successful")

        # Obtain a cursor
            __cursor = __connection.cursor()
    except Exception as e:
        traceback.print_exc()


def getDatafromLIMS(requestId):

    collection_lims_data ={}

    try:
        # Connect to LIMS DB
        connect_DB()

        # Execute the query
        # sql = "SELECT * FROM LABVANTAGE.S_REQUEST where S_REQUESTID = '"+ReqID+"'"

        # QUERY to FETCH
        query =  """SELECT REQUEST, MEDCOVERAGE ,TESTCODE , PAYOR ,  TXSTATUS , POD,DOS,ERRORDETAILS   FROM LABVANTAGE.U_GHFINANCEINFO WHERE  
        REQUEST = '""" +requestId+"""'"""

        curs = __cursor
        curs.execute(query)
        # data = curs.execute(query)
        print(curs)
        print('------')
        # print(data)
        # df = pd.DataFrame(rows, columns=['MEDCOVERAGE' , 'PAYOR' , 'TESTCODE' , 'TXSTATUS' ,'DOS', 'POD'])
        excel_file_path = '../testData/G360_Clinical.xlsx'
        # df.to_excel(excel_file_path, index=2)

        temp_list=[]
        # for row in (this.__cursor.fetchone()):
        #     for each_resultSet in (json.load(row)['results']): #Results set
        #         temp_list.append((each_resultSet['name'],each_resultSet['value']))

        for row in (curs.fetchall()):
            print(row)
            for each_col in (row): #Results set
                if (isinstance(each_col, datetime.datetime)):
                    each_col = each_col.strftime("%m-%d-%Y")
                temp_list.append(str(each_col))
        return temp_list

    except Exception as e:
        print(e)
        pdb.set_trace()




def closeConnection():
    global driver , __connection, __cursor
    driver.find_element("id", "dlgClose0").click()

    driver.close()
    driver.quit()
    __cursor.close()
    __connection.close()



#Selenium Code

def invoke_Chrome():
    global sessionid, service,options,driver
    sessionid= None
    service = Service()
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(service=service, options=options)





def get_BillingToken():
    API_USERNAME = config['Billing_cred']['username']
    API_PASSWORD = config['Billing_cred']['password']
    endPoint = '/api/v1.0/auth/authenticate'
    token_url = config['Billing_cred']['url'] + endPoint
    payload = json.dumps({
        "username": API_USERNAME,
        "password": API_PASSWORD
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", token_url, headers=headers, data=payload)
    print('token generated successfully')

    return response.json()['token']


def trigger_medicarePoller(requestID, token):
    # medicareEndPoint = "/api/v2.0/guardanthealth/billing/update?ids=" + requestID + "&types=Clinical&field=medcoverage&token=" + token
    medicareEndPoint = f"/api/v2.0/guardanthealth/billing/update?ids=%s&types=Clinical&field=medcoverage&token=%s" % (
    requestID, token)

    medicareUrl = config['Billing_cred']['billingurl'] + medicareEndPoint
    payload = ""
    headers = {
        'Authorization': f'Bearer {token}'
        # 'Authorization': 'Bearer ' + token
    }
    response = requests.request("PUT", medicareUrl, headers=headers, data=payload)
    print('medicarePoller executed')
    return response.status_code


def trigger_txStatusPoller(requestID, token):
    txStatusEndPoint = "/api/v2.0/guardanthealth/billing/update?ids=" + requestID + "&types=Clinical&token=" + token + "&field=txstatus"

    txStatusUrl = config['Billing_cred']['billingurl'] + txStatusEndPoint
    payload = ""
    headers = {
        'Authorization': 'Bearer ' + token
    }
    response = requests.request("PUT", txStatusUrl, headers=headers, data=payload)
    print('txStatusUrl executed')
    return response.status_code

def navigatetoLIMSActions():
    global sessionid, driver
    if env == 'SQA':
            uname = config['lims-sqa']['username']
            pswrd = config['lims-sqa']['password']
            lims_url = config['lims-sqa']['url']
    elif env == 'VAL':
        uname = config['lims-val']['username']
        pswrd = config['lims-val']['password']
        lims_url = config['lims-val']['url']
    elif env == 'STAGING':
        uname = config['lims-staging']['username']
        pswrd = config['lims-staging']['password']
        lims_url = config['lims-staging']['url']
    elif env == 'DEV':
        uname = config['lims-dev']['username']
        pswrd = config['lims-dev']['password']
        lims_url = config['lims-dev']['url']
    driver.get(lims_url)
    # driver.manage().window().maximize();
    lims_username = driver.find_element("id", "databaseusername")
    lims_pwrd = driver.find_element("id", "databasepassword")
    lims_username.send_keys(uname)
    lims_pwrd.send_keys(pswrd)
    driver.find_element("id", "submitlogin").click()
    time.sleep(5)
    sessionid = driver.session_id

    WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='jobtypeselector']"))).click()
    jobroleselect = Select(
        WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='jobtypeselector']"))))
    if (jobroleselect.first_selected_option.text != 'System Admin'):
        jobroleselect.select_by_visible_text('System Admin')

        # print([o.text for o in jobroleselect.options])
        # Check Selected Option
        driver.find_element("xpath", "//input[@type='checkbox'][@id='clearoldconnection']").click()
        SelectedOption = Select(
            WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, "//select[@id='jobtypeid']"))))
        if (SelectedOption.first_selected_option.text == 'System Admin'):
            print("System Admin Selected")
        else:
            SelectedOption.select_by_visible_text('System Admin')
        driver.find_element("xpath", "//button[@id='ok']").click()

    # Navigate to System Admin Menu

    time.sleep(2)
    driver.find_element("xpath", "//div[@title='Menu and Dashboard Picker']").click()
    driver.find_element("xpath",
                        "//div[@class='menugizmo_div']/ul/li[5]/a[contains(text(),'System Admin Menu')]").click()

    time.sleep(5)
    driver.switch_to.frame("_nav_frame1")

    driver.find_element("xpath", "//table[@id='contenttable1']//td[contains(text(),'Actions')]").click()

    time.sleep(5)
    driver.switch_to.default_content()

def runActionBlockinLIMS():
    global sessionid, driver , previousTaskName
    print("REquest ID entered Is "+refrequest)

    action_name=''

    # uname = config['lims-val']['username']
    # pswrd = config['lims-val']['password']
    # lims_url = config['lims-val']['url']
    # action_name = "CreateNewRequest_newPatient_wBillingData"

    # action_name = 'CancelledRequest_Portal_wBillingData'
    # action_name='CreateNewRequest_Existing_wBillingData'
    # action_name='CreateNewRequest_Existing_Timepoints'
    # action_name='test_financeInfo'

    if taskname==1:
        action_name = 'TestAccessionRequest_Initial'
    elif taskname== 2:
        action_name = 'Test_AccessionRequest_newPatient_SendACS'
    elif taskname == 3:
        action_name = 'CreateNewRequest_Portal_wBillingData'
    elif taskname == 4:
        pass


    # 0login_url = "https://lims-val.ghdna.io/ghlims/logon.jsp?sso=n"

        # navigatetoLIMSActions()

        # Select User Role - System Admin


    driver.switch_to.frame("_nav_frame1")
    driver.find_element("xpath", "//input[@id='listtop_basicsearchbox']").clear()
    driver.find_element("xpath", "//input[@id='listtop_basicsearchbox']").send_keys(action_name)
    driver.find_element("xpath", "//div[@title='Click to Search']").click()

    time.sleep(5)
    driver.switch_to.frame("list_iframe")
    driver.find_element("xpath", "//td/a[contains(text()," + action_name + ")]").click()

    driver.switch_to.default_content()
    time.sleep(5)

    driver.switch_to.frame("_nav_frame1")
    driver.switch_to.frame("maint_iframe")
    driver.find_element(By.XPATH, "//table//div[contains(text(),'Flow Chart')]").click()
    # driver.find_element("xpath", "//table//div[contains(text(),'Flow Chart')]").click()
    driver.find_element("xpath", "//td[contains(text(),'Edit/Test')]").click()

    driver.switch_to.default_content()
    dlg_frame0 = driver.find_element("xpath", "//*[@id='dlg_frame0']")
    driver.switch_to.frame(dlg_frame0);

    driver.find_element("xpath", "//*[@id='totest']//div[contains(text(),'Test')]").click()
    driver.switch_to.frame("rightframe")
    # requestIDs = getRefRequestIDs()
    previousTaskName = taskname




    # requestID = (requestIDs[i].value)
    newRequestId = performOperationInsideActionBlock(copies,refrequest)
    if newRequestId != None and taskname == 3:
            token = get_BillingToken()
            if runPollers(newRequestId, token):
                            getFinanceInfoResultSet(newRequestId)

    teardown()


def runPollers(newRequestId, token):
    medicare_resp_statusCode = trigger_medicarePoller(newRequestId, token)
    if medicare_resp_statusCode == 200:
        txStatus_resp_statusCode = trigger_txStatusPoller(newRequestId, token)
        if txStatus_resp_statusCode == 200:
            time.sleep(5)
            return True
    return False


def performOperationInsideActionBlock( copy, refrequest):
    global driver
    copies = driver.find_element("xpath", "//input[@name='copies']")
    request = driver.find_element("xpath", "//input[@name='templateid']")
    sampleid = driver.find_element("xpath", "//input[@name='sampleid']")
    copies.clear()
    copies.send_keys(copy)
    request.clear()
    request.send_keys(refrequest)
    sampleID = refrequest + '01'
    sampleid.clear()
    sampleid.send_keys(sampleID)
    driver.switch_to.default_content()
    dlg_frame0 = driver.find_element("xpath", "//*[@id='dlg_frame0']")
    driver.switch_to.frame(dlg_frame0);
    # Click Test Execute Button
    driver.find_element("xpath", "//*[@id='testexecute']//div[contains(text(),'Execute Now')]").click()
    driver.switch_to.frame("rightframe")
    time.sleep(5)

    # Get the new Request ID
    result = driver.find_element("xpath", "//table[2]//td[2]//tr[2]//textarea")
    time.sleep(3)
    resultStr = (driver.execute_script("return arguments[0].{0};".format('value'), result))
    # print(str(resultStr))
    if (('Untrapped Error' in resultStr) or ('GENERAL_ERROR' in resultStr) or (resultStr == '')):
        print('Error check input coming from performOperationInsideActionBlock')
        result_label.configure(text=resultStr)
        newRequestId = None
    else:
        # derive new Values
        newRequestId = parseString(resultStr)
        print('New request ID:' + newRequestId)
        result_label.configure(text=newRequestId)
        # newRequestId = performOperationInsideActionBlock(copies, refrequest)
    if newRequestId != None and taskname == 3:
            token = get_BillingToken()
            if runPollers(newRequestId, token):
                getFinanceInfoResultSet(newRequestId)

            teardown()
    return newRequestId

def createFlowcell(newRequestId,refsample):
    jenkins_url = config['JENKINS']['url']
    jenkins_username = config['JENKINS']['username']
    jenkins_password = config['JENKINS']['password']
    target_sampleid = newRequestId+'01'
    job_name = 'bisqa_tools/stan%2Fjenkins'
    project_name = 'GHI_01'
    product_name = 'Guardant 360'
    report_module_docker_container = 'docker.artifactory01.ghdna.io/bi-report-module:2.6-RLS'
    report_status = 'PASS'
    cancer_type = 'Lung cancer'

    server = jenkins.Jenkins(jenkins_url, username=jenkins_username,
                             password=jenkins_password)
    # Verify connection
    if server.get_whoami():
        print("Successfully connected to Jenkins")
        if server.job_exists(job_name):
            build_name = server.get_job_info(job_name)
            PARAMETERS = {'report_module_docker_container': report_module_docker_container,
                          'old_sample_id': refsample, 'new_sample_id': target_sampleid,
                          'cancer_type': cancer_type, 'project_name': project_name, 'report_status': report_status
                          }
            server.build_job(job_name, PARAMETERS)
            last_build_number = server.get_job_info(job_name)['lastCompletedBuild']['number']

def getLIMSTokenBipUpload():
    pass

def runBIPUploadAPIs():
    pass



def parseString(resultStr):
    try:
        index_of_action_block = resultStr.rfind('<action')
        resultStr = resultStr[index_of_action_block: len(resultStr)]
        finalstr = resultStr[:resultStr.find('</actionblock>')]
        # print(finalstr)
        time.sleep(3)
        root = ET.fromstring(finalstr.strip())

        if taskname == 1:
            tag_id_to_find = 'requestid'
        elif taskname == 2:
            tag_id_to_find = 'keyid1'
        elif taskname == 3:
            tag_id_to_find = "templateid"
        elif taskname == 4:
            tag_id_to_find = "templateid"


        # tag_id_to_find = "requestid"
        # tag_id_to_find ="value"

        xpath_expression = f".//property[@id='{tag_id_to_find}']"
        element = root.find(xpath_expression)

        if element is not None:
            # Get the value of the element
            element_value = element.text
            print(f"Value of element with ID {tag_id_to_find}: {element_value}")
            return element_value
        else:
            print(f"Element with ID {tag_id_to_find} not found in the XML.")
            return None
    except:
        print('-------FAILURE--------')
        print(finalstr)
        traceback.print_exc()
        pdb.set_trace()




def getFinanceInfoResultSet(requestID):
    resultset = getDatafromLIMS(requestID)
    fields= ['REQUEST', 'MEDCOVERAGE' ,'TESTCODE' , 'PAYOR' ,  'TXSTATUS' , 'POD','DOS','ERRORDETAILS']
    result= ' ,\n '.join(' : '.join(x) for x in (zip(fields,resultset)))
    result_label.configure(text=result)
    for each_data in resultset:
        print(each_data)




def teardown():

    #
    #
    entry1.delete(0, END)
    entry2.delete(0, END)
    entry3.delete(0, END)
    # driver.quit()
    # os.system(f"python3 -m folder.subfolder.{main.py}")
    # main()
    # sys.exit(0)
    # driver.quit()
    # if __cursor != None:
    #     closeConnection()

def main():
    try:
        global driver , sessionid ,previousTaskName,copies, refrequest

        load_config()
        if driver == None:
            invoke_Chrome()
        if driver.session_id != sessionid :
            navigatetoLIMSActions()
        else:
            if previousTaskName == taskname:
                performOperationInsideActionBlock( copies, refrequest)
                return
            else:
                closeConnection()
                main()
                return

        runActionBlockinLIMS()
    except Exception as e:
        # (e.__traceback__)
        traceback.print_exc()




customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme('dark-blue')
root_tk = customtkinter.CTk()  # create the Tk window like you normally do
root_tk.geometry("500x700")
root_tk.title("Guardant  Internal TestData Creator")


def getValue():
    global env , copies, refrequest, refsample,taskname
    # print(entry1.get())
    # print(entry2.get())
    # print(entry3.get())
    # print(optionmenu_1.get())
    # print (task_radio.get())
    env = optionmenu_1.get()


    copies = entry1.get()
    refrequest = entry2.get()
    refsample = entry3.get()
    taskname = task_radio.get()

    if env == 'Env*' or copies=='' or refrequest =='':
        messagebox.showerror('Python Error', 'Details missing! Please Recheck input')
        # os.system(f"python3 -m folder.subfolder.{'main.py'}")


    # entry1.option_clear()


    # runActionBlockinLIMS()
    main()
    return





# Define Frames


frame = customtkinter.CTkFrame(master=root_tk)

frame.pack(pady=20, padx=60, fill="both", expand=True)

frame2 = customtkinter.CTkFrame(master=root_tk)
frame2.pack(pady=20, padx=60, fill="both", expand=True)

# Logo and Image
dir, file = os.path.split(os.path.dirname(__file__))
# image_path = os.path.join(dir, 'Resources/logo.png')
#
# image = customtkinter.CTkImage(light_image=Image.open(image_path))

# image= customtkinter.CTkImage(dark_image=(image_path), size=(75, 75))
# image_label= customtkinter.CTkLabel(frame,image=image, text='logo')
# image_label.place(x=10,y=10)

label = customtkinter.CTkLabel(master=frame, text="Create Test Data", corner_radius=8)
label.pack(pady=12, padx=10)

label2 = customtkinter.CTkLabel(master=frame2, text="Results", corner_radius=8)
label2.pack(pady=12, padx=10)

result_label = customtkinter.CTkLabel(master=frame2, text="Wait for results here", font=("Helvetica", 12))
result_label.pack(pady=12)

optionmenu_1 = customtkinter.CTkOptionMenu(frame, values=["SQA", "VAL", "STAGING","DEV"])
optionmenu_1.pack(pady=12, padx=10)
optionmenu_1.set('Env*')

entry1 = customtkinter.CTkEntry(master=frame, placeholder_text="*No.of Copies you need*")
entry1.pack(pady=12, padx=10)
entry2 = customtkinter.CTkEntry(master=frame, placeholder_text="*Reference Request*")
entry2.pack(pady=12, padx=10)
entry3 = customtkinter.CTkEntry(master=frame, placeholder_text="Reference SampleId")
entry3.pack(pady=12, padx=10)

# Task Selection

label = customtkinter.CTkLabel(master=frame, text="Select Task to Perform", corner_radius=8)
label.pack(pady=12, padx=10)

task_radio = customtkinter.IntVar(value=1)
radiobutton_1 = customtkinter.CTkRadioButton(master=frame, text="Create Request till Received Complete State",
                                             variable=task_radio,
                                             value=1)
radiobutton_1.pack(pady=10, padx=10)

radiobutton_2 = customtkinter.CTkRadioButton(master=frame, text="Create Request till Send To ACS State", variable=task_radio,
                                             value=2)
radiobutton_2.pack(pady=10, padx=10)

radiobutton_3 = customtkinter.CTkRadioButton(master=frame, text="Create Request till Released for Billing",
                                             variable=task_radio, value=3)
radiobutton_3.pack(pady=10, padx=10)

radiobutton_4 = customtkinter.CTkRadioButton(master=frame, text="Create Request with Post Accession", variable=task_radio,
                                             value=4)
radiobutton_4.pack(pady=10, padx=10)

button = customtkinter.CTkButton(master=frame, text="Submit", command=getValue)
button.pack(pady=12, padx=10)

root_tk.mainloop()


# select_btn = customtkinter.CTkButton(frame,text='Browse Template',width=10)
# path_entry = customtkinter.CTkEntry(frame,width=200)
# save_btn = customtkinter.CTkButton (frame,text='Upload',width=50)
#
# # select_btn.pack(pady=12, padx=10)
# select_btn.grid(row=0,column =0,padx=1,pady=5)
# # path_entry.pack(pady=12, padx=10)
# path_entry.grid(row=0, column =1, padx=1, pady=5)
# # save_btn.pack(pady=12, padx=10)
# save_btn.grid(row=0, column =2, padx=1, pady=5)






# os.system(f"python3 -m folder.subfolder.{main.py}")












