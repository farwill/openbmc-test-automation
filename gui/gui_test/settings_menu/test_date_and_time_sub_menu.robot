*** Settings ***

Documentation   Test OpenBMC GUI "Date and time" sub-menu of "Settings"

Resource        ../../lib/gui_resource.robot

Suite Setup     Suite Setup Execution
Suite Teardown  Close Browser
Test Setup      Navigate To Date and Time Page

*** Variables ***

${xpath_date_time_heading}     //h1[text()="Date and time"]
${xpath_select_manual}         //*[@data-test-id="dateTime-radio-configureManual"]
${xpath_select_ntp}            //*[@data-test-id="dateTime-radio-configureNTP"]
${xpath_manual_date}           //input[@data-test-id="dateTime-input-manualDate"]
${xpath_manual_time}           //input[@data-test-id="dateTime-input-manualTime"]
${xpath_ntp_server1}           //input[@data-test-id="dateTime-input-ntpServer1"]
${xpath_ntp_server2}           //input[@data-test-id="dateTime-input-ntpServer2"]
${xpath_ntp_server3}           //input[@data-test-id="dateTime-input-ntpServer3"]
${xpath_select_save_settings}  //button[@data-test-id="dateTime-button-saveSettings"]


*** Test Cases ***

Verify Navigation To Date And Time Page
    [Documentation]  Verify navigation to date and time page.
    [Tags]  Verify_Navigation_To_Date_And_Time_Page

    Page Should Contain Element  ${xpath_date_time_heading}


Verify Existence Of All Sections In Date And Time Page
    [Documentation]  Verify existence of all sections in date and time page.
    [Tags]  Verify_Existence_Of_All_Sections_In_Date_And_Time_Page

    Page Should Contain  Configure settings


Verify Existence Of All Buttons In Date And Time Page
    [Documentation]  Verify existence of all buttons in date and time settings page.
    [Tags]  Verify_Existence_Of_All_Buttons_In_Date_And_Time_Page

    Page Should Contain Element  ${xpath_select_manual}
    Page Should Contain Element  ${xpath_select_ntp}
    Page Should Contain Element  ${xpath_select_save_settings}


Verify Existence Of All Input Boxes In Date And Time Page
    [Documentation]  Verify existence of all input boxes in date time page.
    [Tags]  Verify_Existence_Of_All_Input_Boxes_In_Date_And_Time_Page

    Click Element At Coordinates  ${xpath_select_manual}  0  0
    Page Should Contain Element  ${xpath_manual_date}
    Page Should Contain Element  ${xpath_manual_time}

    Click Element At Coordinates  ${xpath_select_ntp}  0  0
    Page Should Contain Element  ${xpath_ntp_server1}
    Page Should Contain Element  ${xpath_ntp_server2}
    Page Should Contain Element  ${xpath_ntp_server3}


Verify Date And Time From Configuration Section
    [Documentation]  Get date and time from configuration section and verify it via BMC CLI.
    [Tags]  Verify_Date_And_Time_From_Configuration_Section

    Click Element At Coordinates  ${xpath_select_manual}  0  0
    ${manual_date}=  Get Value  ${xpath_manual_date}
    ${manual_time}=  Get Value  ${xpath_manual_time}

    ${cli_date_time}=  CLI Get BMC DateTime
    Should contain  ${cli_date_time}  ${manual_date}  ${manual_time}


Verify Display Of Date And Time In GUI Page
     [Documentation]  Get date and time from Redfish and verify it via GUI date and time page.
     [Tags]  Verify_Display_Of_Date_And_Time_In_GUI_Page

    # Set Default timezone in profile settings page.
    Set Timezone In Profile Settings Page  Default
    Navigate To Date and Time Page

    # Get date and time from Redfish.
    ${redfish_date_time}=  CLI Get BMC DateTime
    ${redfish_date}=  Convert Date  ${redfish_date_time}  result_format=%Y-%m-%d
    ${redfish_time}=  Convert Date  ${redfish_date_time}  result_format=%H:%M

    # Verify date and time via GUI date and time page.

    Page Should Contain  ${redfish_date}
    Page Should Contain  ${redfish_time}


Verify Profile Setting Button In Date And Time Page
    [Documentation]  Verify navigation to profile setting page after clicking
    ...  on profile setting button in date and time page.
    [Tags]  Verify_Profile_Setting_Button_In_Date_And_Time_Page

    Click Element   ${xpath_profile_settings_link}
    Wait Until Page Contains Element  ${xpath_profile_settings_heading}  timeout=10
    Location Should Contain   profile-settings


Verify Existence Of Timezone Buttons In Profile Settings Page
    [Documentation]  Verify default UTC button and browser offset IST button
    ...  in Profile settings page
    [Tags]  Verify_Existence_Of_Timezone_Buttons_In_Profile_Settings_Page

    Click Element   ${xpath_profile_settings_link}
    Wait Until Page Contains Element  ${xpath_profile_settings_heading}  timeout=30
    Page Should Contain Element  ${xpath_default_UTC}
    Page Should Contain Element  ${xpath_browser_offset}


Verify Date And Time Change To Browser Offsite Time
    [Documentation]  Verify date and time change to broswer's offset time when
    ...  'Browser offset' option is selected in Profile settings page.
    [Tags]   Verify_Date_And_Time_Change_To_Browser_Offset_Time

    Click Element   ${xpath_profile_settings_link}
    Wait Until Page Contains Element  ${xpath_profile_settings_heading}  timeout=10
    Click Element At Coordinates  ${xpath_browser_offset}  0  0
    Click Element   ${xpath_profile_save_button}
    ${xpath_browser_offset_text}=  Get Text  ${xpath_browser_offset_textfield}

    # We get an output ${xpath_browser_offset_text} = Browser offset (CST UTC-6).
    # Need to compare "CST UTC-6" text so removing the spaces and other values.

    ${text}=  Set Variable  ${xpath_browser_offset_text.split("(")[1].split(")")[0]}
    Navigate To Date and Time Page
    Page Should Contain  ${text}


Verify NTP Server Input Fields In Date And Time Page
    [Documentation]  Verify NTP server input fields in date and time page.
    [Tags]  Verify_NTP_Server_Input_Fields_In_Date_And_Time_Page
    [Setup]  Setup To Power Off And Navigate

    Click Element At Coordinates  ${xpath_select_ntp}  0  0
    Input Text  ${xpath_ntp_server1}  10.10.10.10
    Input Text  ${xpath_ntp_server2}  20.20.20.20
    Input Text  ${xpath_ntp_server3}  30.30.30.30
    Click Element  ${xpath_select_save_settings}


    # Refresh the NTP Page.
    Click Element  ${xpath_refresh_button}
    Wait Until Page Contains Element  ${xpath_select_ntp}  timeout=10s

    Textfield Value Should Be  ${xpath_ntp_server1}  10.10.10.10
    Textfield Value Should Be  ${xpath_ntp_server2}  20.20.20.20
    Textfield Value Should Be  ${xpath_ntp_server3}  30.30.30.30


*** Keywords ***

Suite Setup Execution
   [Documentation]  Do test case setup tasks.

    Launch Browser And Login GUI
    Maximize Browser Window

Setup To Power Off And Navigate   
   [Documentation]  Power off system if not powered off and go to date and
   ...  time page.

   Redfish Power off  stack_mode=skip
   Navigate To Date and Time Page


Navigate To Date and Time Page
    [Documentation]  Navigate to the date and time page from main menu.

    Click Element  ${xpath_settings_menu}
    Click Element  ${xpath_date_time_sub_menu}
    Wait Until Keyword Succeeds  30 sec  10 sec  Location Should Contain  date-time
    Wait Until Element Is Not Visible   ${xpath_page_loading_progress_bar}  timeout=30

