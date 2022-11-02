*** Settings ***
Documentation    Utilities for redfish BIOS attribute operations.

Resource         resource.robot
Resource         bmc_redfish_resource.robot
Resource         common_utils.robot
Resource         utils.robot
Library          tftp_update_utils.py


*** Keywords ***

Set BIOS Attribute Value And Verify

    [Documentation]  Set BIOS attribute handle with attribute value and verify.
    [Arguments]      ${attr_handle}  ${attr_val}  ${verify}=${True}

    # Description of argument(s):
    # ${attr_handle}    BIOS Attribute handle (e.g. 'vmi_if0_ipv4_method').
    # @{attr_val}       Attribute value for the given attribute handle.
    # ${verify}         Verify the new value.


    ${type_int}=    Evaluate  isinstance($attr_val, int)
    ${value}=  Set Variable If  '${type_int}' == '${True}'  ${attr_val}  '${attr_val}'

    Redfish.Patch  ${BIOS_ATTR_SETTINGS_URI}  body={"Attributes":{"${attr_handle}": ${value}}}
    ...  valid_status_codes=[${HTTP_OK}, ${HTTP_NO_CONTENT}]

    Run Keyword If  '${verify}' == '${True}'  Verify BIOS Attribute  ${attr_handle}  ${attr_val}


Set Optional BIOS Attribute Values And Verify

    [Documentation]  For the given BIOS attribute handle update with optional
    ...              attribute values and verify.
    [Arguments]  ${attr_handle}  @{attr_val_list}

    # Description of argument(s):
    # ${attr_handle}    BIOS Attribute handle (e.g. 'vmi_if0_ipv4_method').
    # @{attr_val_list}  List of the attribute values for the given attribute handle.
    #                   (e.g. ['IPv4Static', 'IPv4DHCP']).

    FOR  ${attr}  IN  @{attr_val_list}
        ${new_attr}=  Evaluate  $attr.replace('"', '')
        Set BIOS Attribute Value And Verify  ${attr_handle}  ${new_attr}
    END


Verify BIOS Attribute

    [Documentation]  Verify BIOS attribute value.
    [Arguments]  ${attr_handle}  ${attr_val}

    # Description of argument(s):
    # ${attr_handle}    BIOS Attribute handle (e.g. 'vmi_if0_ipv4_method').
    # ${attr_val}       The expected value for the given attribute handle.

    ${output}=  Redfish.Get Attribute  ${BIOS_ATTR_URI}  Attributes
    Should Be Equal  ${output['${attr_handle}']}  ${attr_val}


Switch And Verify BIOS Attribute Firmware Boot Side
    [Documentation]  Switch BIOS attribute firmware boot side value to Perm/Temp
    ...              at host power off state and verify firmware boot side
    ...              value after BMC reboot.
    [Arguments]      ${set_fw_boot_side}

    # Description of argument(s):
    # set_fw_boot_side    Firmware boot side optional value Perm/Temp.

    # Do host power off.
    Redfish Power Off  stack_mode=skip  quiet=1

    # Get pre reboot state.
    ${pre_reboot_state}=  Get Pre Reboot State

    # Get fw_boot_side value, make sure given set_fw_boot_side and
    # fw_boot_side values are not same.

    ${cur_boot_side}=  Redfish.Get Attribute  ${BIOS_ATTR_URI}  Attributes
    Should Not Be Equal  ${cur_boot_side["fw_boot_side_current"]}  ${set_fw_boot_side}
    ...  msg=Current firmware boot side & the given firmware boot side are same...

    Log To Console  Current firmware boot side :: ${cur_boot_side["fw_boot_side"]}
    Log To Console  Given firmware boot side :: ${set_fw_boot_side}

    # Set the given firmware boot side value.
    Set BIOS Attribute Value And Verify  fw_boot_side  ${set_fw_boot_side}  False

    # Power on BMC and wait for BMC to take reboot.
    Log To Console  Perform power on operation & expect BMC to take reboot...
    Redfish Power Operation  On

    Log To Console  Wait for the BMC to take reboot and come back online...
    Wait For Reboot  start_boot_seconds=${pre_reboot_state['epoch_seconds']}
    ...  wait_state_check=0

    # Post BMC reboot, host should auto power on back to runtime.
    Log To Console  BMC rebooted, wait for host to boot...
    Wait Until Keyword Succeeds  ${OS_RUNNING_TIMEOUT} min  20 sec
    ...  Is Boot Progress At Any State

    # Verify firmware boot side values after BMC reboot.
    Verify BIOS Attribute  fw_boot_side  ${set_fw_boot_side}
    Verify BIOS Attribute  fw_boot_side_current  ${set_fw_boot_side}
