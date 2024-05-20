The Test Data creator app would be useful for the following use Cases:
  1. Create Bulk requests in Initial - Received Complete state.
  2. Create Bulk requests in Send to ACS State.
  3. Create a Request for End - to - End Billing scenarios Which includes Create a new Requests, send it foward to Send to ACS , Releases the requests (Change in State only ,No Report generation) and run the billing APIs, retirves the result.

Things to Note:
  1. Before using the App, users should key in their Credentials in the config.json for different ENV.
  2. The Reference Requests needs to exists in the same ENV that we are trying to create the new Requests.
  3. Once a Task is selected the App can be reused multiple times. However if the user wants to use a different task , the user should close the app and restart the app. This is to ensure a different session id for connecting with Chrome to perform actions inside LIMS.
        
