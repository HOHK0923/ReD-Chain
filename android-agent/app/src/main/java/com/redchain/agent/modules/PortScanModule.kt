package com.redchain.agent.modules

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject
import java.net.InetSocketAddress
import java.net.Socket

object PortScanModule {

    suspend fun execute(params: JSONObject): JSONObject = withContext(Dispatchers.IO) {
        val target = params.getString("target")
        val startPort = params.getInt("start_port")
        val endPort = params.getInt("end_port")
        val timeout = params.optInt("timeout", 2) * 1000

        val openPorts = mutableListOf<Int>()

        coroutineScope {
            val jobs = (startPort..endPort).map { port ->
                async {
                    if (isPortOpen(target, port, timeout)) {
                        synchronized(openPorts) {
                            openPorts.add(port)
                        }
                    }
                }
            }
            jobs.awaitAll()
        }

        JSONObject().apply {
            put("target", target)
            put("scanned_ports", endPort - startPort + 1)
            put("open_ports", JSONArray(openPorts))
            put("open_count", openPorts.size)
        }
    }

    private fun isPortOpen(host: String, port: Int, timeout: Int): Boolean {
        return try {
            Socket().use { socket ->
                socket.connect(InetSocketAddress(host, port), timeout)
                true
            }
        } catch (e: Exception) {
            false
        }
    }
}
