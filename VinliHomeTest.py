import requests
import json
import pytest

BASE_URL = "https://qa-api-challenge.herokuapp.com"

#POST_VEHICLE_URL = "/api/v1/vehicles/{vehicle_ID}/odometer-alerts/_enroll"
#DELETE_VEHICLE_URL = "/api/v1/vehicles/{vehicle_ID}/odometer-alerts/_enroll"
#GET_ODOMETER_ALERTS_URL = "/api/v1/odometer-alerts"

valid_vehicle_IDs_to_test = [1, 100000, 1000000]
invalid_vehicle_IDs_to_test = [-1000000, -100000, -1, 0, "1a"]

#Steps to test:
#1. Attempt POST for each element in vehicle_IDs_to_test
#2. Attempt DELETE for each element in vehicle_IDs_to_test
#3. Attempt GET at GET_ODOMETER_ALERTS_URL



def test_one_positive_post_case_force_pass(vehicle_ID=1): #Force passing to confirm bug found from manual testing 
    POST_VEHICLE_URL = BASE_URL + f"/api/v1/vehicles/{vehicle_ID}/odometer-alerts/_enroll"
    resp = requests.post(POST_VEHICLE_URL)
    response_body = resp.json()
    assert resp.status_code == 200 #Passes but is a false positive, status_code should be returned as 201 
    assert response_body["enrollment"]["vehicleId"] == 2 #Passes but is a false positive, vehicleId should return 1 as specified in the paramter



@pytest.mark.parametrize("vehicle_ID", valid_vehicle_IDs_to_test) #Allows pytest to run each test with each value in data source (vehicle_IDS_to_test), 1st param = mapped variable names 2nd param = data source
def test_positive_post_case(vehicle_ID):
    POST_VEHICLE_URL = BASE_URL + f"/api/v1/vehicles/{vehicle_ID}/odometer-alerts/_enroll" #Passing in different vehicle IDs to POST endpoint
    resp = requests.post(POST_VEHICLE_URL)
    response_body = resp.json()

    format_key = [response_body["enrollment"]["vehicleId"], response_body["enrollment"]["enrolled"]]
    format_check = [vehicle_ID, True]

    ### BUG: Expected to fail since response_body["enrollment"]["vehicleId"] == 2 when vehicle_ID == 1 ###
    ### BUG: Expected to fail since status code == 200 instead of 201 ###

    assert all([x in format_check for x in format_key]) #For every x in format_key, checks if that x exists in format_check; returns true if all values found in key are found in check
    assert resp.status_code == 201 #Checking for correct status code in response; 201 for successfully creating a new resource
    
    #assert response_body["enrollment"]["vehicleId"] == vehicle_ID #Verifying that vehicle_ID passed is equal to the vehicle_ID returned in the response
    #assert response_body["enrollment"]["enrolled"] == True #User is enrolled in service alerts


@pytest.mark.parametrize("vehicle_ID", invalid_vehicle_IDs_to_test)
def test_negative_post_case(vehicle_ID):
    POST_VEHICLE_URL = BASE_URL + f"/api/v1/vehicles/{vehicle_ID}/odometer-alerts/_enroll" #Passing in different vehicle IDs to POST endpoint
    resp = requests.post(POST_VEHICLE_URL)

    format_key = resp.headers["Content-Type"]
    format_check = ["text/html", "application/json"]
    
    ### BUG: Expected to fail since status code == 404; looking for err code 400 "Bad Request"
    assert resp.status_code == 400 #Checking for "Bad Request" error since chosen values are outside parameter boundaries
    assert any(x in format_key for x in format_check) #Checking if header is either text or json


@pytest.mark.parametrize("vehicle_ID", valid_vehicle_IDs_to_test)
def test_positive_delete_case(vehicle_ID):
    DELETE_VEHICLE_URL = BASE_URL + f"/api/v1/vehicles/{vehicle_ID}/odometer-alerts/_enroll" #Passing in different vehicle_IDs to DELETE endpoint
    resp = requests.delete(DELETE_VEHICLE_URL)
    

    if not resp.text: #Check that a response body that confirms vehicle deletion exists
        assert resp.status_code == 204 #Successfully deleted vehicle, no content to display
    else:
        assert resp.status_code == 200 #Successfully deleted vehicle, a response body is returned
        assert resp.json()["status"] == "deleted" #Return status confirmation if response body exists
    
@pytest.mark.parametrize("vehicle_ID", invalid_vehicle_IDs_to_test)
def test_negative_delete_case(vehicle_ID):
    DELETE_VEHICLE_URL = BASE_URL + f"/api/v1/vehicles/{vehicle_ID}/odometer-alerts/_enroll" #Passing in different vehicle_IDs to DELETE endpoint
    resp = requests.delete(DELETE_VEHICLE_URL)

    assert resp.status_code == 404 #Resource can not be found at invalid vehicle_ID


def test_get_odometer_alerts():
    GET_ALERTS_URL = BASE_URL + "/api/v1/odometer-alerts"
    resp = requests.get(GET_ALERTS_URL)
    response_body = resp.json()
    assert resp.status_code == 200 #Request confirmed and processed 
    assert len(response_body["alerts"]) != 0 #Checking that data exists inside vehicle alert array; If fail, no data exists in the array