#ifndef WIFI_CREDENTIALS_H
#define WIFI_CREDENTIALS_H

#include "wifi.h"

/*
 * ==============================================================================
 * WiFi Credentials Configuration Template
 * ==============================================================================
 * Copy this file to 'wifi_credentials.h' and fill in your network parameters.
 * Note: 'wifi_credentials.h' is ignored by git to protect credentials.
 */

#define WIFI_PROFILE  1

#if WIFI_PROFILE == 1              /* Profile 1: WPA2-PSK Network */
    #define WIFI_SSID        "YOUR_WIFI_SSID"
    #define WIFI_PASSWORD    "YOUR_WIFI_PASSWORD"
    #define WIFI_SECURITY    WIFI_ECN_WPA2_PSK
    #define WIFI_GATEWAY_IP  {192, 168, 1, 1}

#elif WIFI_PROFILE == 2            /* Profile 2: Open Network (e.g. University / Lab) */
    #define WIFI_SSID        "LAB_OPEN_WIFI"
    #define WIFI_PASSWORD    ""
    #define WIFI_SECURITY    WIFI_ECN_OPEN
    #define WIFI_GATEWAY_IP  {10, 0, 0, 1}

#elif WIFI_PROFILE == 3            /* Profile 3: Mobile Hotspot */
    #define WIFI_SSID        "MY_MOBILE_HOTSPOT"
    #define WIFI_PASSWORD    "hotspot_password"
    #define WIFI_SECURITY    WIFI_ECN_WPA2_PSK
    #define WIFI_GATEWAY_IP  {192, 168, 43, 1}

#else
    #error "Invalid WIFI_PROFILE selected"
#endif

#endif /* WIFI_CREDENTIALS_H */
